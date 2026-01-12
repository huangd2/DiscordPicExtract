import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, 'combined_data.csv')
INITIAL_CAPITAL = 10000.0

# Strategy configurations
STRATEGIES = {
    'Strategy 2': {
        'trades_csv': os.path.join(SCRIPT_DIR, 'strategy2', 'strategy2_low_risk_accumulation_trades.csv'),
        'color': '#3498db'
    },
    'Strategy 3': {
        'trades_csv': os.path.join(SCRIPT_DIR, 'strategy3', 'strategy3_low_risk_accumulation_trades.csv'),
        'color': '#9b59b6'
    },
    'Strategy 4': {
        'trades_csv': os.path.join(SCRIPT_DIR, 'strategy4', 'strategy4_progressive_exit_trades.csv'),
        'color': '#e67e22'
    },
    'Strategy 4.1': {
        'trades_csv': os.path.join(SCRIPT_DIR, 'strategy4', 'strategy4_progressive_exit_even_thirds_trades.csv'),
        'color': '#2ecc71'
    }
}

print("Reading data...")
df = pd.read_csv(CSV_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date
df = df.sort_values('timestamp').reset_index(drop=True)
trading_days = sorted(df['date'].unique())
print(f"Found {len(trading_days)} trading days")

def extract_equity_and_pnl(trades_csv, strategy_name):
    """Extract equity curve and daily P&L from trades CSV"""
    try:
        trades_df = pd.read_csv(trades_csv)
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df['date'] = trades_df['timestamp'].dt.date
        trades_df = trades_df.sort_values('timestamp').reset_index(drop=True)
        
        # Initialize tracking
        equity_by_day = []
        daily_pnl_dict = defaultdict(float)
        cash = INITIAL_CAPITAL
        shares = 0
        
        # Process each trading day
        for day in trading_days:
            # Get day's signals for last price
            day_signals = df[df['date'] == day].sort_values('timestamp')
            last_price = day_signals.iloc[-1]['fPrice'] if len(day_signals) > 0 else 0
            
            # Get all trades for this day
            day_trades = trades_df[trades_df['date'] == day].sort_values('timestamp')
            
            # Process trades chronologically
            for _, trade in day_trades.iterrows():
                # Update cash and shares from trade record
                if 'remaining capital' in trade.index and pd.notna(trade['remaining capital']):
                    cash = float(trade['remaining capital'])
                if 'position' in trade.index and pd.notna(trade['position']):
                    shares = int(trade['position']) if pd.notna(trade['position']) else 0
                
                # Accumulate P&L
                if 'PnL' in trade.index and pd.notna(trade['PnL']):
                    daily_pnl_dict[day] += float(trade['PnL'])
            
            # Calculate portfolio value at end of day
            portfolio_value = cash + (shares * last_price if shares > 0 else 0)
            equity_by_day.append(portfolio_value)
        
        daily_pnl_list = [daily_pnl_dict.get(day, 0.0) for day in trading_days]
        
        return equity_by_day, daily_pnl_list
        
    except Exception as e:
        print(f"Error processing {strategy_name}: {e}")
        import traceback
        traceback.print_exc()
        return None, None

# Extract data for all strategies
strategy_data = {}
for strategy_name, config in STRATEGIES.items():
    print(f"\nProcessing {strategy_name}...")
    equity, pnl = extract_equity_and_pnl(config['trades_csv'], strategy_name)
    if equity is not None and len(equity) == len(trading_days):
        strategy_data[strategy_name] = {
            'equity': equity,
            'daily_pnl': pnl,
            'color': config['color']
        }
        final_value = equity[-1]
        total_pnl = sum(pnl)
        print(f"  [OK] Equity curve: {len(equity)} points, Final: ${final_value:,.2f}")
        print(f"  [OK] Daily P&L: {len(pnl)} points, Total: ${total_pnl:,.2f}")
    else:
        print(f"  [FAILED] Failed to extract data")

if len(strategy_data) == 4:
    print("\nGenerating comparison charts...")
    
    # 1. Equity Curve Comparison (ONE plot with 4 lines overlaid)
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.suptitle('Equity Curve Comparison: Strategies 2, 3, 4, and 4.1', fontsize=16, fontweight='bold')
    
    strategy_order = ['Strategy 2', 'Strategy 3', 'Strategy 4', 'Strategy 4.1']
    
    # Plot all strategies on the same graph (overlay)
    for strategy_name in strategy_order:
        if strategy_name in strategy_data:
            data = strategy_data[strategy_name]
            ax.plot(range(len(trading_days)), data['equity'], 
                    linewidth=2.5, color=data['color'], marker='o', markersize=2, 
                    label=f"{strategy_name} (Final: ${data['equity'][-1]:,.2f})", alpha=0.9)
    
    ax.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', linewidth=1.5, alpha=0.6, label='Initial Capital')
    ax.set_xlabel('Trading Day', fontsize=12)
    ax.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax.set_title('Equity Curve Comparison: All Strategies Overlaid', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='best')
    
    # Find global min/max for y-axis
    all_equities = []
    for strategy_name in strategy_order:
        if strategy_name in strategy_data:
            all_equities.extend(strategy_data[strategy_name]['equity'])
    global_min_equity = min(all_equities)
    global_max_equity = max(all_equities)
    ax.set_ylim([min(INITIAL_CAPITAL * 0.98, global_min_equity * 0.99), global_max_equity * 1.01])
    
    plt.tight_layout()
    equity_comparison_path = os.path.join(SCRIPT_DIR, 'strategy4', 'equity_curve_comparison.png')
    plt.savefig(equity_comparison_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {equity_comparison_path}")
    plt.close()
    
    # 2. Daily P&L Comparison (2x2 grid with same y-axis range: -120 to 170)
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    fig.suptitle('Daily P&L Comparison: Strategies 2, 3, 4, and 4.1', fontsize=16, fontweight='bold')
    
    # Fixed y-axis range for all plots
    y_min = -120
    y_max = 170
    
    for idx, strategy_name in enumerate(strategy_order):
        if strategy_name in strategy_data:
            row = idx // 2
            col = idx % 2
            ax = axes[row, col]
            data = strategy_data[strategy_name]
            
            colors = ['green' if pnl >= 0 else 'red' for pnl in data['daily_pnl']]
            ax.bar(range(len(trading_days)), data['daily_pnl'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
            ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
            ax.set_xlabel('Trading Day', fontsize=11)
            ax.set_ylabel('Daily P&L ($)', fontsize=11)
            total_pnl = sum(data['daily_pnl'])
            ax.set_title(f'{strategy_name} Daily P&L (Total: ${total_pnl:,.2f})', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            # Set same y-axis range for all plots: -120 to 170
            ax.set_ylim([y_min, y_max])
            
            # Add statistics text
            winning_days = sum(1 for pnl in data['daily_pnl'] if pnl > 0)
            losing_days = sum(1 for pnl in data['daily_pnl'] if pnl < 0)
            stats_text = f'Winning Days: {winning_days} | Losing Days: {losing_days}'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   fontsize=9, verticalalignment='top', 
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    pnl_comparison_path = os.path.join(SCRIPT_DIR, 'strategy4', 'daily_pnl_comparison.png')
    plt.savefig(pnl_comparison_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {pnl_comparison_path}")
    plt.close()
    
    print("\n[OK] All comparison charts generated successfully!")
else:
    print(f"\n[FAILED] Only {len(strategy_data)}/4 strategies processed successfully")
    print("Please ensure all strategy trade CSV files exist and are properly formatted.")
