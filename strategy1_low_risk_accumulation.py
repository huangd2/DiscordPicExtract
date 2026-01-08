import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from collections import defaultdict

# Configuration
STRATEGY_NAME = "Low Risk Accumulation Strategy"
INITIAL_CAPITAL = 10000.0
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, 'combined_data.csv')
OUTPUT_CSV = os.path.join(SCRIPT_DIR, 'strategy1_low_risk_accumulation_trades.csv')

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

# Track position at end of each day
daily_positions = {}  # date -> shares held
cross_day_trades = []  # Trades that span multiple days

# Process each signal chronologically
for idx, row in df.iterrows():
    signal_date = row['date']
    signal_type = row['buy/sell']
    risk = row['risk'].lower()
    f_price = row['fPrice']
    timestamp = row['timestamp']
    
    # Handle Buy signals
    if signal_type == 'Buy' and risk == 'low':
        # Check if we have enough cash
        if cash >= f_price:
            # Buy 1 share
            cash -= f_price
            shares += 1
            current_trade_buys.append({
                'date': signal_date,
                'timestamp': timestamp,
                'price': f_price,
                'shares': 1
            })
            
            # Record buy action for CSV
            total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
            avg_price = total_cost / shares if shares > 0 else 0
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
    
    # Handle Sell signals
    elif signal_type == 'Sell' and risk in ['low', 'medium']:
        if shares > 0:
            # Sell all shares
            sell_price = f_price
            total_shares = shares
            total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
            avg_buy_price = total_cost / total_shares if total_shares > 0 else 0
            
            # Only sell if sell price is higher than average buy price
            if sell_price > avg_buy_price:
                # Calculate P&L
                proceeds = sell_price * total_shares
                pnl = proceeds - total_cost
                
                # Update cash
                cash += proceeds
                
                # Increment trade number for completed trade
                trade_number += 1
                
                # Record sell action for CSV (with PnL since position closes)
                avg_price = total_cost / total_shares if total_shares > 0 else 0
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
                    'avg_buy_price': avg_buy_price,
                    'sell_price': sell_price,
                    'cost': total_cost,
                    'proceeds': proceeds,
                    'pnl': pnl,
                    'is_win': pnl > 0,
                    'is_cross_day': buy_date != sell_date
                }
                
                trades.append(trade)
                
                if trade['is_cross_day']:
                    cross_day_trades.append(trade)
                
                # Reset current trade buys
                current_trade_buys = []
            else:
                # Sell price not above avg buy price, skip this sell signal
                pass
    
    # Track position at end of each day
    # Check if this is the last signal of the day
    is_last_signal_of_day = (idx == len(df) - 1) or (df.loc[idx + 1, 'date'] != signal_date)
    
    if is_last_signal_of_day:
        daily_positions[signal_date] = shares

# Handle final position if still open
if shares > 0:
    last_signal = df.iloc[-1]
    final_price = last_signal['fPrice']
    
    total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
    proceeds = final_price * shares
    pnl = proceeds - total_cost
    
    # Increment trade number for final trade
    trade_number += 1
    
    # Record final sell action for CSV (with PnL since position closes)
    avg_price = total_cost / shares if shares > 0 else 0
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
    
    buy_date = current_trade_buys[0]['date'] if current_trade_buys else last_signal['date']
    
    trade = {
        'buy_date': buy_date,
        'sell_date': last_signal['date'],
        'buy_timestamp': current_trade_buys[0]['timestamp'] if current_trade_buys else last_signal['timestamp'],
        'sell_timestamp': last_signal['timestamp'],
        'shares': shares,
        'avg_buy_price': total_cost / shares if shares > 0 else 0,
        'sell_price': final_price,
        'cost': total_cost,
        'proceeds': proceeds,
        'pnl': pnl,
        'is_win': pnl > 0,
        'is_cross_day': buy_date != last_signal['date']
    }
    
    trades.append(trade)
    if trade['is_cross_day']:
        cross_day_trades.append(trade)
    
    cash += proceeds
    shares = 0

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

for idx, row in df.iterrows():
    signal_date = row['date']
    signal_type = row['buy/sell']
    risk = row['risk'].lower()
    f_price = row['fPrice']
    timestamp = row['timestamp']
    
    if signal_type == 'Buy' and risk == 'low':
        if cash >= f_price:
            cash -= f_price
            shares += 1
            current_trade_buys.append({
                'date': signal_date,
                'timestamp': timestamp,
                'price': f_price,
                'shares': 1
            })
        else:
            # Track missed buy opportunity due to insufficient funds
            daily_missed_buys[signal_date] += 1
    
    elif signal_type == 'Sell' and risk in ['low', 'medium']:
        if shares > 0:
            sell_price = f_price
            total_shares = shares
            total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
            avg_buy_price = total_cost / total_shares if total_shares > 0 else 0
            
            # Only sell if sell price is higher than average buy price
            if sell_price > avg_buy_price:
                proceeds = sell_price * total_shares
                pnl = proceeds - total_cost
                
                cash += proceeds
                shares = 0
                
                # Record daily stats
                daily_trade_counts[signal_date] += 1
                daily_pnl[signal_date] += pnl
                
                current_trade_buys = []
            else:
                # Sell price not above avg buy price, skip this sell signal
                pass
    
    # Track end of day state
    is_last_signal_of_day = (idx == len(df) - 1) or (df.loc[idx + 1, 'date'] != signal_date)
    
    if is_last_signal_of_day:
        daily_cash[signal_date] = cash
        daily_shares[signal_date] = shares

# Handle final position
if shares > 0:
    last_signal = df.iloc[-1]
    final_price = last_signal['fPrice']
    total_cost = sum(buy['price'] * buy['shares'] for buy in current_trade_buys)
    proceeds = final_price * shares
    pnl = proceeds - total_cost
    
    daily_trade_counts[last_signal['date']] += 1
    daily_pnl[last_signal['date']] += pnl
    daily_cash[last_signal['date']] += proceeds

# Calculate statistics
total_trades = len(trades)
winning_trades = sum(1 for t in trades if t['is_win'])
losing_trades = sum(1 for t in trades if not t['is_win'])
total_pnl = sum(t['pnl'] for t in trades)
final_value = cash

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
print(f"  Winning Trades: {winning_trades} ({winning_trades/total_trades*100:.1f}%)")
print(f"  Losing Trades: {losing_trades} ({losing_trades/total_trades*100:.1f}%)")
print(f"  Average P&L per Trade: ${total_pnl/total_trades:.2f}" if total_trades > 0 else "  Average P&L per Trade: $0.00")

if winning_trades > 0:
    avg_win = sum(t['pnl'] for t in trades if t['is_win']) / winning_trades
    print(f"  Average Winning Trade: ${avg_win:.2f}")

if losing_trades > 0:
    avg_loss = sum(t['pnl'] for t in trades if not t['is_win']) / losing_trades
    print(f"  Average Losing Trade: ${avg_loss:.2f}")

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
        elif first_buy_price and cash_at_start < first_buy_price:
            # Check if we couldn't afford the first buy signal
            funds_limited = True
        
        # Build indicator string
        indicators = []
        if cross_day_closed:
            indicators.append("Cross-day position closed")
        if funds_limited:
            indicators.append(f"Limited by funds (missed {missed_buys_on_day} buy signal(s), cash at start: ${cash_at_start:.2f})")
        
        indicator_str = " (" + ", ".join(indicators) + ")" if indicators else ""
        print(f"    {day}: ${pnl:.2f}{indicator_str}")
else:
    print(f"  No days with loss > $50")

print("\n" + "="*80)

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
plt.hist(trade_counts_by_day, bins=range(max(trade_counts_by_day)+2), edgecolor='black', alpha=0.7)
plt.xlabel('Number of Trades per Day')
plt.ylabel('Frequency (Days)')
plt.title('Histogram: Number of Trades per Day')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('trades_per_day_histogram.png', dpi=300, bbox_inches='tight')
print("  Saved: trades_per_day_histogram.png")
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
plt.savefig('daily_pnl_histogram.png', dpi=300, bbox_inches='tight')
print("  Saved: daily_pnl_histogram.png")
plt.close()

# 3. Equity curve (by trading day)
plt.figure(figsize=(14, 7))
equity_by_day = []
running_cash = INITIAL_CAPITAL
running_shares = 0
current_trade_buys = []

for day in trading_days:
    day_signals = df[df['date'] == day].sort_values('timestamp')
    last_price = day_signals.iloc[-1]['fPrice']  # Use last signal price for valuation
    
    for idx, row in day_signals.iterrows():
        signal_type = row['buy/sell']
        risk = row['risk'].lower()
        f_price = row['fPrice']
        
        if signal_type == 'Buy' and risk == 'low':
            if running_cash >= f_price:
                running_cash -= f_price
                running_shares += 1
                current_trade_buys.append({'price': f_price, 'shares': 1})
        
        elif signal_type == 'Sell' and risk in ['low', 'medium']:
            if running_shares > 0:
                sell_price = f_price
                proceeds = sell_price * running_shares
                running_cash += proceeds
                running_shares = 0
                current_trade_buys = []
                last_price = f_price  # Update last price after sell
    
    # Calculate portfolio value at end of day
    portfolio_value = running_cash + (running_shares * last_price if running_shares > 0 else 0)
    equity_by_day.append(portfolio_value)

# Plot equity curve
plt.plot(range(len(trading_days)), equity_by_day, linewidth=2, color='blue', marker='o', markersize=3)
plt.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', linewidth=1, label=f'Initial Capital (${INITIAL_CAPITAL:,.0f})')
plt.xlabel('Trading Day')
plt.ylabel('Portfolio Value ($)')
plt.title('Equity Curve: Portfolio Value Over Time (End of Day)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('equity_curve.png', dpi=300, bbox_inches='tight')
print("  Saved: equity_curve.png")
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
    plt.savefig('trade_win_loss.png', dpi=300, bbox_inches='tight')
    print("  Saved: trade_win_loss.png")
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
plt.savefig('daily_pnl_over_time.png', dpi=300, bbox_inches='tight')
print("  Saved: daily_pnl_over_time.png")
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
plt.savefig('daily_positions.png', dpi=300, bbox_inches='tight')
print("  Saved: daily_positions.png")
plt.close()

print("\nAll visualizations saved successfully!")
print("="*80)

