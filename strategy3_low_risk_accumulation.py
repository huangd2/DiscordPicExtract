import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from collections import defaultdict

# Configuration
STRATEGY_NAME = "Low Risk Accumulation Strategy 3 - Progressive Buy with 1.5% Stop-Loss"
INITIAL_CAPITAL = 10000.0
STOP_LOSS_PCT = 1.5  # Stop-loss at 1.5% drop from first buy price

# Progressive buy criteria: (buy_signal_number: (min_drop_percentage, shares_to_buy))
# Buy cadence: 3, 3, 6 shares (initial: 3, 0.5% drop: 3, 1.0% drop: 6)
# Maximum drop allowed: 1.0% (stop-loss triggers at 1.5%)
BUY_CRITERIA = {
    2: (0.5, 3),   # 2nd buy: >=0.5% drop, 3 shares
    3: (1.0, 6),   # 3rd buy: >=1.0% drop, 6 shares
    # No 4th buy - stop-loss triggers at 1.5% drop
}

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, 'combined_data.csv')
STRATEGY3_DIR = os.path.join(SCRIPT_DIR, 'strategy3')
os.makedirs(STRATEGY3_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(STRATEGY3_DIR, 'strategy3_low_risk_accumulation_trades.csv')

# Read and parse data
print("Reading data...")
df = pd.read_csv(CSV_FILE)

# Parse timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date

# Sort by timestamp
df = df.sort_values('timestamp').reset_index(drop=True)

# Get unique trading days
trading_days = sorted(df['date'].unique())
print(f"Found {len(trading_days)} trading days")
print(f"Date range: {trading_days[0]} to {trading_days[-1]}")

# Initialize trading state
cash = INITIAL_CAPITAL
shares = 0
trades = []  # List of completed trades
daily_stats = []  # Daily statistics
current_trade_buys = []  # Track buys for current open position
trade_actions = []  # List of all trade actions for CSV output
trade_number = 0  # Trade counter
first_buy_price = None  # Price of first buy signal in current position
buy_signal_count = 0  # Number of buy signals executed in current position (1-indexed)
half_sell_stage = 0  # 0=none, 1=first half sold, 2=both halves sold/position closed
position_cost_basis = 0.0  # Track actual cost basis of current position (to avoid rounding errors)
stop_loss_triggered_count = 0  # Track how many trades hit stop-loss

# Track position at end of each day
daily_positions = {}  # date -> shares held
cross_day_trades = []  # Trades that span multiple days

# Helper function to get buy criteria for any buy signal number
def get_buy_criteria(buy_signal_num):
    """Get buy criteria for buy signal number. Only up to 3rd buy (1.0% drop)."""
    if buy_signal_num in BUY_CRITERIA:
        return BUY_CRITERIA[buy_signal_num]
    return None  # No buys beyond 1.0% drop - stop-loss triggers at 1.5%

# Process each signal chronologically
for idx, row in df.iterrows():
    signal_date = row['date']
    signal_type = row['buy/sell']
    risk = row['risk'].lower()
    f_price = row['fPrice']
    timestamp = row['timestamp']
    
    # Handle Buy signals
    if signal_type == 'Buy' and risk == 'low':
        if shares == 0:
            # No position - first buy signal, execute immediately
            if cash >= f_price * 3:  # Need to afford 3 shares
                # Buy 3 shares
                cost = f_price * 3
                cash -= cost
                shares += 3
                current_trade_buys.append({
                    'date': signal_date,
                    'timestamp': timestamp,
                    'price': f_price,
                    'shares': 3
                })
                first_buy_price = f_price  # Set first buy price
                buy_signal_count = 1  # First buy signal executed
                position_cost_basis = cost  # Track cost basis
                
                # Record buy action for CSV
                avg_price = position_cost_basis / shares if shares > 0 else 0
                trade_actions.append({
                    'trade #': '',
                    'timestamp': timestamp,
                    'buy/sell': 'Buy',
                    'fPrice': f_price,
                    'position': shares,
                    'avgPrice': round(avg_price, 2) if shares > 0 else '',
                    'remaining capital': round(cash, 2),
                    'PnL': ''
                })
        else:
            # Position is open - check progressive buy criteria
            if first_buy_price is not None:
                # Calculate price drop percentage from first buy
                price_drop_pct = ((first_buy_price - f_price) / first_buy_price) * 100
                
                # Check stop-loss first: if price drops >= 1.5% from first buy price
                # This handles the case where max accumulation is reached but price continues to drop
                if price_drop_pct >= STOP_LOSS_PCT:
                    # Execute stop-loss: sell at exactly 1.5% below first buy price
                    stop_loss_price = first_buy_price * (1 - STOP_LOSS_PCT / 100)
                    total_shares = shares
                    proceeds = stop_loss_price * total_shares
                    pnl = proceeds - position_cost_basis
                    
                    # Update cash
                    cash += proceeds
                    
                    # Increment trade number for completed trade
                    trade_number += 1
                    stop_loss_triggered_count += 1
                    
                    # Record stop-loss action for CSV (with PnL since position closes)
                    avg_price = position_cost_basis / total_shares if total_shares > 0 else 0
                    trade_actions.append({
                        'trade #': trade_number,
                        'timestamp': timestamp,
                        'buy/sell': 'Stop-Loss',
                        'fPrice': stop_loss_price,
                        'position': 0,  # Position is now 0 after selling all
                        'avgPrice': round(avg_price, 2) if total_shares > 0 else '',
                        'remaining capital': round(cash, 2),
                        'PnL': round(pnl, 2)
                    })
                    
                    shares = 0
                    
                    # Record trade
                    buy_date = current_trade_buys[0]['date'] if current_trade_buys else signal_date
                    
                    trade = {
                        'buy_date': buy_date,
                        'sell_date': signal_date,
                        'buy_timestamp': current_trade_buys[0]['timestamp'] if current_trade_buys else timestamp,
                        'sell_timestamp': timestamp,
                        'shares': total_shares,
                        'avg_buy_price': avg_price,
                        'sell_price': stop_loss_price,
                        'cost': position_cost_basis,
                        'proceeds': proceeds,
                        'pnl': pnl,
                        'is_win': pnl > 0,
                        'is_cross_day': buy_date != signal_date,
                        'is_stop_loss': True
                    }
                    
                    trades.append(trade)
                    
                    if trade['is_cross_day']:
                        cross_day_trades.append(trade)
                    
                    # Reset current trade buys and tracking variables
                    current_trade_buys = []
                    first_buy_price = None
                    buy_signal_count = 0
                    half_sell_stage = 0
                    position_cost_basis = 0.0
                    
                    # Skip the buy signal that triggered the stop-loss to avoid back-to-back stop-losses
                    # The buy signal is only used to detect the stop-loss condition, not to start a new position
                else:
                    # Price hasn't reached stop-loss threshold, check for additional buys
                    # Determine next buy signal number
                    next_buy_signal = buy_signal_count + 1
                    
                    # Get criteria for this buy signal number
                    criteria = get_buy_criteria(next_buy_signal)
                    
                    if criteria is not None:
                        required_drop, shares_to_buy = criteria
                        
                        # Check if price drop meets criteria
                        if price_drop_pct >= required_drop:
                            # Calculate total cost for desired shares
                            total_cost = f_price * shares_to_buy
                            
                            # Determine how many shares we can actually buy
                            if cash >= total_cost:
                                # Can buy all desired shares
                                actual_shares = shares_to_buy
                            else:
                                # Buy maximum affordable whole shares
                                actual_shares = int(cash / f_price)
                            
                            # Execute buy if we can afford at least 1 share
                            if actual_shares > 0 and cash >= f_price:
                                cost = f_price * actual_shares
                                cash -= cost
                                shares += actual_shares
                                current_trade_buys.append({
                                    'date': signal_date,
                                    'timestamp': timestamp,
                                    'price': f_price,
                                    'shares': actual_shares
                                })
                                buy_signal_count = next_buy_signal  # Update buy signal count
                                position_cost_basis += cost  # Update cost basis
                                
                                # Record buy action for CSV
                                # Calculate average price from tracked cost basis
                                avg_price = position_cost_basis / shares if shares > 0 else 0
                                trade_actions.append({
                                    'trade #': '',
                                    'timestamp': timestamp,
                                    'buy/sell': 'Buy',
                                    'fPrice': f_price,
                                    'position': shares,
                                    'avgPrice': round(avg_price, 2) if shares > 0 else '',
                                    'remaining capital': round(cash, 2),
                                    'PnL': ''
                                })
                    # else: No criteria for this buy signal number (max accumulation reached) - skip buy
    
    # Handle Sell signals (any risk level, as long as price > avg buy price)
    elif signal_type == 'Sell':
        if shares > 0:
            sell_price = f_price
            total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
            avg_buy_price = total_cost / shares if shares > 0 else 0
            
            # Sell all shares if price > avg buy price
            if sell_price > avg_buy_price:
                # Sell all shares
                total_shares = shares
                proceeds = sell_price * total_shares
                pnl = proceeds - position_cost_basis  # Use tracked cost basis
                
                # Update cash
                cash += proceeds
                
                # Increment trade number for completed trade
                trade_number += 1
                
                # Record sell action for CSV (with PnL since position closes)
                avg_price = position_cost_basis / total_shares if total_shares > 0 else 0
                trade_actions.append({
                    'trade #': trade_number,
                    'timestamp': timestamp,
                    'buy/sell': 'Sell',
                    'fPrice': sell_price,
                    'position': 0,  # Position is now 0 after selling all
                    'avgPrice': round(avg_price, 2) if total_shares > 0 else '',
                    'remaining capital': round(cash, 2),
                    'PnL': round(pnl, 2)
                })
                
                shares = 0
                
                # Record trade
                buy_date = current_trade_buys[0]['date'] if current_trade_buys else signal_date
                sell_date = signal_date
                
                trade = {
                    'buy_date': buy_date,
                    'sell_date': sell_date,
                    'buy_timestamp': current_trade_buys[0]['timestamp'] if current_trade_buys else timestamp,
                    'sell_timestamp': timestamp,
                    'shares': total_shares,
                    'avg_buy_price': avg_price,
                    'sell_price': sell_price,
                    'cost': position_cost_basis,
                    'proceeds': proceeds,
                    'pnl': pnl,
                    'is_win': pnl > 0,
                    'is_cross_day': buy_date != sell_date,
                    'is_stop_loss': False
                }
                
                trades.append(trade)
                
                if trade['is_cross_day']:
                    cross_day_trades.append(trade)
                
                # Reset current trade buys and tracking variables
                current_trade_buys = []
                first_buy_price = None
                buy_signal_count = 0
                half_sell_stage = 0
                position_cost_basis = 0.0
            else:
                # Sell price not above avg buy price, skip this sell signal
                pass
    
    # Track position at end of each day
    # Check if this is the last signal of the day
    is_last_signal_of_day = (idx == len(df) - 1) or (df.loc[idx + 1, 'date'] != signal_date)
    
    if is_last_signal_of_day:
        daily_positions[signal_date] = shares

# Handle final position if still open
# Check stop-loss first (1.5% drop from first buy), then check if price > avg buy price
if shares > 0:
    last_signal = df.iloc[-1]
    final_price = last_signal['fPrice']
    
    avg_buy_price = position_cost_basis / shares if shares > 0 else 0
    
    # Check stop-loss first (if no sell signal occurred and price dropped 1.5% from first buy)
    if first_buy_price is not None:
        price_drop_pct = ((first_buy_price - final_price) / first_buy_price) * 100
        if price_drop_pct >= STOP_LOSS_PCT:
            # Trigger stop-loss
            stop_loss_price = first_buy_price * (1 - STOP_LOSS_PCT / 100)
            proceeds = stop_loss_price * shares
            pnl = proceeds - position_cost_basis
            
            # Increment trade number for final trade
            trade_number += 1
            stop_loss_triggered_count += 1
            
            # Record final stop-loss action for CSV (with PnL since position closes)
            avg_price = position_cost_basis / shares if shares > 0 else 0
            trade_actions.append({
                'trade #': trade_number,
                'timestamp': last_signal['timestamp'],
                'buy/sell': 'Stop-Loss',
                'fPrice': stop_loss_price,
                'position': 0,  # Position is now 0 after selling all
                'avgPrice': round(avg_price, 2) if shares > 0 else '',
                'remaining capital': round(cash + proceeds, 2),
                'PnL': round(pnl, 2)
            })
            
            cash += proceeds
            
            buy_date = current_trade_buys[0]['date'] if current_trade_buys else last_signal['date']
            
            trade = {
                'buy_date': buy_date,
                'sell_date': last_signal['date'],
                'buy_timestamp': current_trade_buys[0]['timestamp'] if current_trade_buys else last_signal['timestamp'],
                'sell_timestamp': last_signal['timestamp'],
                'shares': shares,
                'avg_buy_price': avg_price,
                'sell_price': stop_loss_price,
                'cost': position_cost_basis,
                'proceeds': proceeds,
                'pnl': pnl,
                'is_win': pnl > 0,
                'is_cross_day': buy_date != last_signal['date'],
                'is_stop_loss': True
            }
            
            trades.append(trade)
            if trade['is_cross_day']:
                cross_day_trades.append(trade)
            
            shares = 0
        # Only sell if final price > avg buy price (follow the rule)
        elif final_price > avg_buy_price:
            proceeds = final_price * shares
            pnl = proceeds - position_cost_basis
            
            # Increment trade number for final trade
            trade_number += 1
            
            # Record final sell action for CSV (with PnL since position closes)
            avg_price = position_cost_basis / shares if shares > 0 else 0
            trade_actions.append({
                'trade #': trade_number,
                'timestamp': last_signal['timestamp'],
                'buy/sell': 'Sell',
                'fPrice': final_price,
                'position': 0,  # Position is now 0 after selling all
                'avgPrice': round(avg_price, 2) if shares > 0 else '',
                'remaining capital': round(cash + proceeds, 2),
                'PnL': round(pnl, 2)
            })
            
            cash += proceeds
            
            buy_date = current_trade_buys[0]['date'] if current_trade_buys else last_signal['date']
            
            trade = {
                'buy_date': buy_date,
                'sell_date': last_signal['date'],
                'buy_timestamp': current_trade_buys[0]['timestamp'] if current_trade_buys else last_signal['timestamp'],
                'sell_timestamp': last_signal['timestamp'],
                'shares': shares,
                'avg_buy_price': avg_price,
                'sell_price': final_price,
                'cost': position_cost_basis,
                'proceeds': proceeds,
                'pnl': pnl,
                'is_win': pnl > 0,
                'is_cross_day': buy_date != last_signal['date'],
                'is_stop_loss': False
            }
            
            trades.append(trade)
            if trade['is_cross_day']:
                cross_day_trades.append(trade)
            
            shares = 0
    # else: Final position not sold because price condition not met - keep position for valuation

# Calculate daily statistics
daily_trade_counts = defaultdict(int)
daily_pnl = defaultdict(float)
daily_cash = {}
daily_shares = {}
daily_missed_buys = defaultdict(int)  # Track missed buy opportunities due to insufficient funds

# Re-process to get daily stats
cash = INITIAL_CAPITAL
shares = 0
current_trade_buys = []
first_buy_price = None  # Reset for daily stats calculation
buy_signal_count = 0  # Reset for daily stats calculation
half_sell_stage = 0  # Reset for daily stats calculation
position_cost_basis = 0.0  # Reset for daily stats calculation

for idx, row in df.iterrows():
    signal_date = row['date']
    signal_type = row['buy/sell']
    risk = row['risk'].lower()
    f_price = row['fPrice']
    timestamp = row['timestamp']
    
    if signal_type == 'Buy' and risk == 'low':
        if shares == 0:
            # No position - first buy signal, execute immediately
            if cash >= f_price * 3:  # Need to afford 3 shares
                cash -= f_price * 3
                shares += 3
                current_trade_buys.append({
                    'date': signal_date,
                    'timestamp': timestamp,
                    'price': f_price,
                    'shares': 3
                })
                first_buy_price = f_price
                buy_signal_count = 1
                position_cost_basis = f_price * 3
        else:
            # Position is open - check progressive buy criteria
            if first_buy_price is not None:
                price_drop_pct = ((first_buy_price - f_price) / first_buy_price) * 100
                
                # Check stop-loss first: if price drops >= 1.5% from first buy price
                if price_drop_pct >= STOP_LOSS_PCT:
                    # Execute stop-loss
                    stop_loss_price = first_buy_price * (1 - STOP_LOSS_PCT / 100)
                    proceeds = stop_loss_price * shares
                    pnl = proceeds - position_cost_basis
                    
                    cash += proceeds
                    shares = 0
                    
                    # Record daily stats
                    daily_trade_counts[signal_date] += 1
                    daily_pnl[signal_date] += pnl
                    
                    current_trade_buys = []
                    first_buy_price = None
                    buy_signal_count = 0
                    half_sell_stage = 0
                    position_cost_basis = 0.0
                else:
                    # Price hasn't reached stop-loss threshold, check for additional buys
                    next_buy_signal = buy_signal_count + 1
                    criteria = get_buy_criteria(next_buy_signal)
                    
                    if criteria is not None:
                        required_drop, shares_to_buy = criteria
                        if price_drop_pct >= required_drop:
                            total_cost = f_price * shares_to_buy
                            if cash >= total_cost:
                                actual_shares = shares_to_buy
                            else:
                                actual_shares = int(cash / f_price)
                            
                            if actual_shares > 0 and cash >= f_price:
                                cost = f_price * actual_shares
                                cash -= cost
                                shares += actual_shares
                                current_trade_buys.append({
                                    'date': signal_date,
                                    'timestamp': timestamp,
                                    'price': f_price,
                                    'shares': actual_shares
                                })
                                buy_signal_count = next_buy_signal
                                position_cost_basis += cost
                            else:
                                daily_missed_buys[signal_date] += 1
                    # else: No criteria for this buy signal number (max accumulation reached) - skip buy
        # Track missed buys if we couldn't afford first buy
        if shares == 0 and cash < f_price * 3:
            daily_missed_buys[signal_date] += 1
    
    elif signal_type == 'Sell':
        if shares > 0:
            sell_price = f_price
            total_shares = shares
            avg_buy_price = position_cost_basis / total_shares if total_shares > 0 else 0
            
            # Sell all shares if price > avg buy price
            if sell_price > avg_buy_price:
                proceeds = sell_price * total_shares
                pnl = proceeds - position_cost_basis
                
                cash += proceeds
                shares = 0
                
                # Record daily stats
                daily_trade_counts[signal_date] += 1
                daily_pnl[signal_date] += pnl
                
                current_trade_buys = []
                first_buy_price = None
                buy_signal_count = 0
                half_sell_stage = 0
                position_cost_basis = 0.0
    
    # Track end of day state
    is_last_signal_of_day = (idx == len(df) - 1) or (df.loc[idx + 1, 'date'] != signal_date)
    
    if is_last_signal_of_day:
        daily_cash[signal_date] = cash
        daily_shares[signal_date] = shares

# Handle final position (for daily stats - check stop-loss first, then sell if profitable)
if shares > 0:
    last_signal = df.iloc[-1]
    final_price = last_signal['fPrice']
    avg_buy_price = position_cost_basis / shares if shares > 0 else 0
    
    # Check stop-loss first
    if first_buy_price is not None:
        price_drop_pct = ((first_buy_price - final_price) / first_buy_price) * 100
        if price_drop_pct >= STOP_LOSS_PCT:
            # Execute stop-loss
            stop_loss_price = first_buy_price * (1 - STOP_LOSS_PCT / 100)
            proceeds = stop_loss_price * shares
            pnl = proceeds - position_cost_basis
            
            daily_trade_counts[last_signal['date']] += 1
            daily_pnl[last_signal['date']] += pnl
            daily_cash[last_signal['date']] += proceeds
        elif final_price > avg_buy_price:
            proceeds = final_price * shares
            pnl = proceeds - position_cost_basis
            
            daily_trade_counts[last_signal['date']] += 1
            daily_pnl[last_signal['date']] += pnl
            daily_cash[last_signal['date']] += proceeds
    # else: Final position not sold - no trade recorded

# Calculate statistics
total_trades = len(trades)
winning_trades = sum(1 for t in trades if t['is_win'])
losing_trades = sum(1 for t in trades if not t['is_win'])
stop_loss_trades = sum(1 for t in trades if t.get('is_stop_loss', False))

# Final value includes cash plus any remaining position value
# Note: If final position was sold, shares should be 0 and final_value = cash
# Use the remaining capital from the last trade action if available, otherwise calculate from cash and shares
if len(trade_actions) > 0 and trade_actions[-1].get('remaining capital') is not None:
    # Use the remaining capital from the last recorded trade action (most accurate)
    final_value = trade_actions[-1]['remaining capital']
elif shares > 0:
    last_signal = df.iloc[-1]
    final_price = last_signal['fPrice']
    final_value = cash + (shares * final_price)
else:
    final_value = cash

# Calculate total P&L as difference between final value and initial capital
# This includes both realized P&L from trades and unrealized P&L from any remaining position
total_pnl = final_value - INITIAL_CAPITAL

days_with_zero_position = sum(1 for shares in daily_positions.values() if shares == 0)
days_with_position = len(trading_days) - days_with_zero_position
days_with_cross_day_position = sum(1 for date in trading_days[:-1] if daily_positions.get(date, 0) > 0)

cross_day_wins = sum(1 for t in cross_day_trades if t['is_win'])
cross_day_losses = len(cross_day_trades) - cross_day_wins

# Print comprehensive summary
print("\n" + "="*80)
print(f"TRADING STRATEGY BACKTEST RESULTS: {STRATEGY_NAME}")
print("="*80)

print(f"\nCAPITAL & PERFORMANCE:")
print(f"  Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"  Final Portfolio Value: ${final_value:,.2f}")
print(f"  Total P&L: ${total_pnl:,.2f}")
print(f"  Return: {(final_value/INITIAL_CAPITAL - 1)*100:.2f}%")

print(f"\nTRADING DAYS:")
print(f"  Total Trading Days: {len(trading_days)}")
print(f"  Days with Zero Position at End: {days_with_zero_position}")
print(f"  Days with Position at End: {days_with_position}")
print(f"  Days with Position Crossing to Next Day: {days_with_cross_day_position}")

print(f"\nTRADE STATISTICS:")
print(f"  Total Trades Executed: {total_trades}")
print(f"  Winning Trades: {winning_trades} ({winning_trades/total_trades*100:.1f}%)" if total_trades > 0 else "  Winning Trades: 0")
print(f"  Losing Trades: {losing_trades} ({losing_trades/total_trades*100:.1f}%)" if total_trades > 0 else "  Losing Trades: 0")
print(f"  Stop-Loss Triggered: {stop_loss_trades} ({stop_loss_trades/total_trades*100:.1f}%)" if total_trades > 0 else "  Stop-Loss Triggered: 0")
print(f"  Average P&L per Trade: ${total_pnl/total_trades:.2f}" if total_trades > 0 else "  Average P&L per Trade: $0.00")

if winning_trades > 0:
    avg_win = sum(t['pnl'] for t in trades if t['is_win']) / winning_trades
    print(f"  Average Winning Trade: ${avg_win:.2f}")

if losing_trades > 0:
    avg_loss = sum(t['pnl'] for t in trades if not t['is_win']) / losing_trades
    print(f"  Average Losing Trade: ${avg_loss:.2f}")

if stop_loss_trades > 0:
    stop_loss_pnl = sum(t['pnl'] for t in trades if t.get('is_stop_loss', False))
    avg_stop_loss = stop_loss_pnl / stop_loss_trades
    print(f"  Average Stop-Loss Trade: ${avg_stop_loss:.2f}")

print(f"\nCROSS-DAY TRADES:")
print(f"  Total Cross-Day Trades: {len(cross_day_trades)}")
print(f"  Cross-Day Wins: {cross_day_wins} ({cross_day_wins/len(cross_day_trades)*100:.1f}%)" if cross_day_trades else "  Cross-Day Wins: 0")
print(f"  Cross-Day Losses: {cross_day_losses} ({cross_day_losses/len(cross_day_trades)*100:.1f}%)" if cross_day_trades else "  Cross-Day Losses: 0")

if cross_day_trades:
    cross_day_pnl = sum(t['pnl'] for t in cross_day_trades)
    print(f"  Cross-Day Total P&L: ${cross_day_pnl:.2f}")

print(f"\nDAILY TRADE DISTRIBUTION:")
trade_counts_list = list(daily_trade_counts.values())
if trade_counts_list:
    print(f"  Min Trades per Day: {min(trade_counts_list)}")
    print(f"  Max Trades per Day: {max(trade_counts_list)}")
    print(f"  Average Trades per Day: {np.mean(trade_counts_list):.2f}")

# Calculate days with no trades
days_with_no_trades = sum(1 for day in trading_days if daily_trade_counts.get(day, 0) == 0)
print(f"  Days with No Trades: {days_with_no_trades} ({days_with_no_trades/len(trading_days)*100:.1f}%)")

# Calculate daily P&L statistics for winning and losing days
daily_pnl_list = [daily_pnl.get(day, 0) for day in trading_days]
winning_days_pnl = [pnl for pnl in daily_pnl_list if pnl > 0]
losing_days_pnl = [pnl for pnl in daily_pnl_list if pnl < 0]
zero_days_pnl = [pnl for pnl in daily_pnl_list if pnl == 0]

print(f"\nDAILY P&L STATISTICS:")
print(f"  Total Days: {len(trading_days)}")
print(f"  Winning Days: {len(winning_days_pnl)} ({len(winning_days_pnl)/len(trading_days)*100:.1f}%)")
if winning_days_pnl:
    print(f"    Min: ${min(winning_days_pnl):.2f}")
    print(f"    Max: ${max(winning_days_pnl):.2f}")
    print(f"    Mean: ${np.mean(winning_days_pnl):.2f}")
    print(f"    Median: ${np.median(winning_days_pnl):.2f}")

print(f"  Losing Days: {len(losing_days_pnl)} ({len(losing_days_pnl)/len(trading_days)*100:.1f}%)")
if losing_days_pnl:
    print(f"    Min: ${min(losing_days_pnl):.2f}")
    print(f"    Max: ${max(losing_days_pnl):.2f}")
    print(f"    Mean: ${np.mean(losing_days_pnl):.2f}")
    print(f"    Median: ${np.median(losing_days_pnl):.2f}")

print(f"  Zero P&L Days: {len(zero_days_pnl)} ({len(zero_days_pnl)/len(trading_days)*100:.1f}%)")

# Find big losing days (>$50 loss) and check for capital constraints
big_losing_days = []
for day in trading_days:
    pnl = daily_pnl.get(day, 0)
    if pnl < -50:
        big_losing_days.append((day, pnl))

# Check if big losing days closed cross-day positions and if they were limited by funds
print(f"\nBIG LOSING DAYS (Loss > $50):")
if big_losing_days:
    print(f"  Total Big Losing Days: {len(big_losing_days)}")
    
    # Now analyze each big losing day
    for day, pnl in sorted(big_losing_days, key=lambda x: x[1]):  # Sort by loss amount
        # Check if any trades on this day closed cross-day positions
        day_trades = [t for t in trades if t['sell_date'] == day]
        cross_day_closed = any(t['is_cross_day'] for t in day_trades)
        stop_loss_closed = any(t.get('is_stop_loss', False) for t in day_trades)
        
        # Check for missed buys on this day
        missed_buys_on_day = daily_missed_buys.get(day, 0)
        
        # Get cash at start of day (from previous day's end)
        day_index = trading_days.index(day)
        if day_index > 0:
            prev_day = trading_days[day_index - 1]
            cash_at_start = daily_cash.get(prev_day, INITIAL_CAPITAL)
        else:
            cash_at_start = INITIAL_CAPITAL
        
        # Check if we had insufficient funds at start of day
        day_signals = df[df['date'] == day].sort_values('timestamp')
        first_buy_price = None
        for sig_idx, sig_row in day_signals.iterrows():
            if sig_row['buy/sell'] == 'Buy' and sig_row['risk'].lower() == 'low':
                first_buy_price = sig_row['fPrice']
                break
        
        funds_limited = False
        if missed_buys_on_day > 0:
            funds_limited = True
        elif first_buy_price and cash_at_start < first_buy_price * 3:
            # Check if we couldn't afford the first buy signal (3 shares)
            funds_limited = True
        
        # Build indicator string
        indicators = []
        if cross_day_closed:
            indicators.append("Cross-day position closed")
        if stop_loss_closed:
            indicators.append("Stop-loss triggered")
        if funds_limited:
            indicators.append(f"Limited by funds (missed {missed_buys_on_day} buy signal(s), cash at start: ${cash_at_start:.2f})")
        
        indicator_str = " (" + ", ".join(indicators) + ")" if indicators else ""
        print(f"    {day}: ${pnl:.2f}{indicator_str}")
else:
    print(f"  No days with loss > $50")

print("\n" + "="*80)

# Write statistics to CSV file
STATS_CSV = os.path.join(STRATEGY3_DIR, 'strategy3_statistics.csv')
stats_data = {
    'Metric': [
        'Initial Capital',
        'Final Portfolio Value',
        'Total P&L',
        'Return (%)',
        'Total Trading Days',
        'Days with Zero Position at End',
        'Days with Position at End',
        'Days with Position Crossing to Next Day',
        'Total Trades Executed',
        'Winning Trades',
        'Losing Trades',
        'Win Rate (%)',
        'Stop-Loss Triggered',
        'Stop-Loss Rate (%)',
        'Average P&L per Trade',
        'Average Winning Trade',
        'Average Losing Trade',
        'Average Stop-Loss Trade',
        'Total Cross-Day Trades',
        'Cross-Day Wins',
        'Cross-Day Losses',
        'Cross-Day Win Rate (%)',
        'Cross-Day Total P&L',
        'Min Trades per Day',
        'Max Trades per Day',
        'Average Trades per Day',
        'Days with No Trades',
        'Days with No Trades (%)',
        'Total Days',
        'Winning Days',
        'Winning Days (%)',
        'Losing Days',
        'Losing Days (%)',
        'Zero P&L Days',
        'Zero P&L Days (%)',
        'Min Winning Day P&L',
        'Max Winning Day P&L',
        'Mean Winning Day P&L',
        'Median Winning Day P&L',
        'Min Losing Day P&L',
        'Max Losing Day P&L',
        'Mean Losing Day P&L',
        'Median Losing Day P&L',
        'Big Losing Days (Loss > $50)',
    ],
    'Value': [
        f"${INITIAL_CAPITAL:,.2f}",
        f"${final_value:,.2f}",
        f"${total_pnl:,.2f}",
        f"{(final_value/INITIAL_CAPITAL - 1)*100:.2f}",
        len(trading_days),
        days_with_zero_position,
        days_with_position,
        days_with_cross_day_position,
        total_trades,
        winning_trades,
        losing_trades,
        f"{winning_trades/total_trades*100:.1f}" if total_trades > 0 else "0.0",
        stop_loss_trades,
        f"{stop_loss_trades/total_trades*100:.1f}" if total_trades > 0 else "0.0",
        f"${total_pnl/total_trades:.2f}" if total_trades > 0 else "$0.00",
        f"${sum(t['pnl'] for t in trades if t['is_win']) / winning_trades:.2f}" if winning_trades > 0 else "$0.00",
        f"${sum(t['pnl'] for t in trades if not t['is_win']) / losing_trades:.2f}" if losing_trades > 0 else "$0.00",
        f"${sum(t['pnl'] for t in trades if t.get('is_stop_loss', False)) / stop_loss_trades:.2f}" if stop_loss_trades > 0 else "$0.00",
        len(cross_day_trades),
        cross_day_wins,
        cross_day_losses,
        f"{cross_day_wins/len(cross_day_trades)*100:.1f}" if cross_day_trades else "0.0",
        f"${sum(t['pnl'] for t in cross_day_trades):.2f}" if cross_day_trades else "$0.00",
        min(trade_counts_list) if trade_counts_list else 0,
        max(trade_counts_list) if trade_counts_list else 0,
        f"{np.mean(trade_counts_list):.2f}" if trade_counts_list else "0.00",
        days_with_no_trades,
        f"{days_with_no_trades/len(trading_days)*100:.1f}",
        len(trading_days),
        len(winning_days_pnl),
        f"{len(winning_days_pnl)/len(trading_days)*100:.1f}",
        len(losing_days_pnl),
        f"{len(losing_days_pnl)/len(trading_days)*100:.1f}",
        len(zero_days_pnl),
        f"{len(zero_days_pnl)/len(trading_days)*100:.1f}",
        f"${min(winning_days_pnl):.2f}" if winning_days_pnl else "$0.00",
        f"${max(winning_days_pnl):.2f}" if winning_days_pnl else "$0.00",
        f"${np.mean(winning_days_pnl):.2f}" if winning_days_pnl else "$0.00",
        f"${np.median(winning_days_pnl):.2f}" if winning_days_pnl else "$0.00",
        f"${min(losing_days_pnl):.2f}" if losing_days_pnl else "$0.00",
        f"${max(losing_days_pnl):.2f}" if losing_days_pnl else "$0.00",
        f"${np.mean(losing_days_pnl):.2f}" if losing_days_pnl else "$0.00",
        f"${np.median(losing_days_pnl):.2f}" if losing_days_pnl else "$0.00",
        len(big_losing_days),
    ]
}
stats_df = pd.DataFrame(stats_data)
stats_df.to_csv(STATS_CSV, index=False)
print(f"\nWriting statistics to CSV...")
print(f"  Saved: {STATS_CSV}")

# Write trade actions to CSV file
print("\nWriting trade actions to CSV...")
trade_df = pd.DataFrame(trade_actions)
trade_df.to_csv(OUTPUT_CSV, index=False)
print(f"  Saved: {OUTPUT_CSV}")
print(f"  Total actions recorded: {len(trade_actions)}")

# Create visualizations
print("\nGenerating visualizations...")

# 1. Histogram: Trades per day
plt.figure(figsize=(12, 6))
trade_counts_by_day = [daily_trade_counts.get(day, 0) for day in trading_days]
if trade_counts_by_day:
    plt.hist(trade_counts_by_day, bins=range(max(trade_counts_by_day)+2), edgecolor='black', alpha=0.7)
plt.xlabel('Number of Trades per Day')
plt.ylabel('Frequency (Days)')
plt.title('Histogram: Number of Trades per Day')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(STRATEGY3_DIR, 'trades_per_day_histogram.png'), dpi=300, bbox_inches='tight')
print(f"  Saved: {os.path.join(STRATEGY3_DIR, 'trades_per_day_histogram.png')}")
plt.close()

# 2. Histogram: Daily P&L
plt.figure(figsize=(12, 6))
daily_pnl_list = [daily_pnl.get(day, 0) for day in trading_days]
plt.hist(daily_pnl_list, bins=50, edgecolor='black', alpha=0.7, color='green' if sum(daily_pnl_list) >= 0 else 'red')
plt.xlabel('Daily P&L ($)')
plt.ylabel('Frequency (Days)')
plt.title('Histogram: Daily Profit/Loss')
plt.axvline(x=0, color='black', linestyle='--', linewidth=1)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(STRATEGY3_DIR, 'daily_pnl_histogram.png'), dpi=300, bbox_inches='tight')
print(f"  Saved: {os.path.join(STRATEGY3_DIR, 'daily_pnl_histogram.png')}")
plt.close()

# 3. Equity curve (by trading day)
plt.figure(figsize=(14, 7))
equity_by_day = []
running_cash = INITIAL_CAPITAL
running_shares = 0
current_trade_buys = []
first_buy_price = None  # Reset for equity curve calculation
buy_signal_count = 0  # Reset for equity curve calculation
half_sell_stage = 0  # Reset for equity curve calculation

for day in trading_days:
    day_signals = df[df['date'] == day].sort_values('timestamp')
    last_price = day_signals.iloc[-1]['fPrice']  # Use last signal price for valuation
    
    for idx, row in day_signals.iterrows():
        signal_type = row['buy/sell']
        risk = row['risk'].lower()
        f_price = row['fPrice']
        
        if signal_type == 'Buy' and risk == 'low':
            if running_shares == 0:
                # No position - first buy signal, execute immediately
                if running_cash >= f_price * 3:  # Need to afford 3 shares
                    running_cash -= f_price * 3
                    running_shares += 3
                    current_trade_buys.append({'price': f_price, 'shares': 3})
                    first_buy_price = f_price
                    buy_signal_count = 1
            else:
                # Position is open - check progressive buy criteria
                if first_buy_price is not None:
                    price_drop_pct = ((first_buy_price - f_price) / first_buy_price) * 100
                    
                    # Check stop-loss first: if price drops >= 1.5% from first buy price
                    if price_drop_pct >= STOP_LOSS_PCT:
                        # Execute stop-loss: sell at exactly 1.5% below first buy price
                        stop_loss_price = first_buy_price * (1 - STOP_LOSS_PCT / 100)
                        proceeds = stop_loss_price * running_shares
                        running_cash += proceeds
                        running_shares = 0
                        current_trade_buys = []
                        first_buy_price = None
                        buy_signal_count = 0
                        half_sell_stage = 0
                        # Skip the buy signal that triggered the stop-loss to avoid back-to-back stop-losses
                    else:
                        # Price hasn't reached stop-loss threshold, check for additional buys
                        next_buy_signal = buy_signal_count + 1
                        criteria = get_buy_criteria(next_buy_signal)
                        
                        if criteria is not None:
                            required_drop, shares_to_buy = criteria
                            if price_drop_pct >= required_drop:
                                total_cost = f_price * shares_to_buy
                                if running_cash >= total_cost:
                                    actual_shares = shares_to_buy
                                else:
                                    actual_shares = int(running_cash / f_price)
                                
                                if actual_shares > 0 and running_cash >= f_price:
                                    cost = f_price * actual_shares
                                    running_cash -= cost
                                    running_shares += actual_shares
                                    current_trade_buys.append({'price': f_price, 'shares': actual_shares})
                                    buy_signal_count = next_buy_signal
        
        elif signal_type == 'Sell':
            if running_shares > 0:
                sell_price = f_price
                total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
                avg_buy_price = total_cost / running_shares if running_shares > 0 else 0
                
                # Sell all shares if price > avg buy price
                if sell_price > avg_buy_price:
                    proceeds = sell_price * running_shares
                    running_cash += proceeds
                    running_shares = 0
                    current_trade_buys = []
                    last_price = sell_price
                    first_buy_price = None
                    buy_signal_count = 0
                    half_sell_stage = 0
    
    # Calculate portfolio value at end of day
    portfolio_value = running_cash + (running_shares * last_price if running_shares > 0 else 0)
    equity_by_day.append(portfolio_value)

# Handle final position if still open (check stop-loss first, then sell at final price for equity curve)
if running_shares > 0:
    final_price = df[df['date'] == trading_days[-1]].iloc[-1]['fPrice']
    if first_buy_price is not None:
        price_drop_pct = ((first_buy_price - final_price) / first_buy_price) * 100
        if price_drop_pct >= STOP_LOSS_PCT:
            # Execute stop-loss
            stop_loss_price = first_buy_price * (1 - STOP_LOSS_PCT / 100)
            final_proceeds = stop_loss_price * running_shares
            running_cash += final_proceeds
            running_shares = 0
            # Update final equity value
            equity_by_day[-1] = running_cash
        else:
            total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
            avg_buy_price = total_cost / running_shares if running_shares > 0 else 0
            if final_price > avg_buy_price:
                final_proceeds = final_price * running_shares
                running_cash += final_proceeds
                running_shares = 0
                # Update final equity value
                equity_by_day[-1] = running_cash
            else:
                # Keep position, value at final price
                equity_by_day[-1] = running_cash + (running_shares * final_price)
    else:
        # Keep position, value at final price
        equity_by_day[-1] = running_cash + (running_shares * final_price)

# Plot equity curve
plt.plot(range(len(trading_days)), equity_by_day, linewidth=2, color='blue', marker='o', markersize=3)
plt.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', linewidth=1, label=f'Initial Capital (${INITIAL_CAPITAL:,.0f})')
plt.xlabel('Trading Day')
plt.ylabel('Portfolio Value ($)')
plt.title('Equity Curve: Portfolio Value Over Time (End of Day)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(STRATEGY3_DIR, 'equity_curve.png'), dpi=300, bbox_inches='tight')
print(f"  Saved: {os.path.join(STRATEGY3_DIR, 'equity_curve.png')}")
plt.close()

# 4. Win/Loss pie chart
if total_trades > 0:
    plt.figure(figsize=(10, 8))
    labels = ['Winning Trades', 'Losing Trades']
    sizes = [winning_trades, losing_trades]
    colors = ['#2ecc71', '#e74c3c']
    explode = (0.05, 0.05)
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    plt.title(f'Trade Win/Loss Distribution\n(Total: {total_trades} trades)')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(STRATEGY3_DIR, 'trade_win_loss.png'), dpi=300, bbox_inches='tight')
    print(f"  Saved: {os.path.join(STRATEGY3_DIR, 'trade_win_loss.png')}")
    plt.close()

# 5. Daily P&L over time
plt.figure(figsize=(14, 7))
daily_pnl_sorted = [daily_pnl.get(day, 0) for day in trading_days]
colors = ['green' if pnl >= 0 else 'red' for pnl in daily_pnl_sorted]
plt.bar(range(len(trading_days)), daily_pnl_sorted, color=colors, alpha=0.7, edgecolor='black')
plt.xlabel('Trading Day')
plt.ylabel('Daily P&L ($)')
plt.title('Daily Profit/Loss Over Time')
plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(STRATEGY3_DIR, 'daily_pnl_over_time.png'), dpi=300, bbox_inches='tight')
print(f"  Saved: {os.path.join(STRATEGY3_DIR, 'daily_pnl_over_time.png')}")
plt.close()

# 6. Position state at end of each day
plt.figure(figsize=(14, 7))
end_of_day_shares = [daily_positions.get(day, 0) for day in trading_days]
plt.bar(range(len(trading_days)), end_of_day_shares, alpha=0.7, edgecolor='black', color='orange')
plt.xlabel('Trading Day')
plt.ylabel('Shares Held at End of Day')
plt.title('Position State at End of Each Trading Day')
plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(STRATEGY3_DIR, 'daily_positions.png'), dpi=300, bbox_inches='tight')
print(f"  Saved: {os.path.join(STRATEGY3_DIR, 'daily_positions.png')}")
plt.close()

print("\nAll visualizations saved successfully!")
print("="*80)
