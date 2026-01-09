import pandas as pd

# Read statistics files
s2 = pd.read_csv('strategy2/strategy2_statistics.csv')
s3 = pd.read_csv('strategy3/strategy3_statistics.csv')

print("=" * 100)
print("STRATEGY 2 vs STRATEGY 3 COMPARISON")
print("=" * 100)

# Key metrics to compare
metrics = [
    'Initial Capital',
    'Final Portfolio Value',
    'Total P&L',
    'Return (%)',
    'Total Trades Executed',
    'Winning Trades',
    'Losing Trades',
    'Win Rate (%)',
    'Stop-Loss Triggered',
    'Stop-Loss Rate (%)',
    'Average P&L per Trade',
    'Average Winning Trade',
    'Average Losing Trade',
    'Total Cross-Day Trades',
    'Cross-Day Wins',
    'Cross-Day Losses',
    'Cross-Day Win Rate (%)',
    'Cross-Day Total P&L',
    'Days with Zero Position at End',
    'Days with Position at End',
    'Days with Position Crossing to Next Day',
    'Winning Days',
    'Winning Days (%)',
    'Losing Days',
    'Losing Days (%)',
    'Zero P&L Days',
    'Zero P&L Days (%)',
    'Mean Winning Day P&L',
    'Median Winning Day P&L',
    'Max Winning Day P&L',
]

print("\nKEY PERFORMANCE METRICS:")
print("-" * 100)
print(f"{'Metric':<40} {'Strategy 2':<25} {'Strategy 3':<25} {'Difference':<15}")
print("-" * 100)

for metric in metrics:
    s2_row = s2[s2['Metric'] == metric]
    s3_row = s3[s3['Metric'] == metric]
    
    if len(s2_row) > 0 and len(s3_row) > 0:
        v2 = s2_row['Value'].values[0]
        v3 = s3_row['Value'].values[0]
        
        # Try to calculate difference for numeric values
        diff = ""
        try:
            # Remove $ and commas, convert to float
            v2_num = float(str(v2).replace('$', '').replace(',', ''))
            v3_num = float(str(v3).replace('$', '').replace(',', ''))
            diff_num = v3_num - v2_num
            if diff_num >= 0:
                diff = f"+${diff_num:.2f}" if '$' in str(v2) else f"+{diff_num:.2f}"
            else:
                diff = f"${diff_num:.2f}" if '$' in str(v2) else f"{diff_num:.2f}"
        except:
            pass
        
        print(f"{metric:<40} {str(v2):<25} {str(v3):<25} {diff:<15}")

print("\n" + "=" * 100)
print("SUMMARY ANALYSIS")
print("=" * 100)

# Extract key values for analysis
s2_final = float(s2[s2['Metric'] == 'Final Portfolio Value']['Value'].values[0].replace('$', '').replace(',', ''))
s3_final = float(s3[s3['Metric'] == 'Final Portfolio Value']['Value'].values[0].replace('$', '').replace(',', ''))
s2_return = float(s2[s2['Metric'] == 'Return (%)']['Value'].values[0])
s3_return = float(s3[s3['Metric'] == 'Return (%)']['Value'].values[0])
s2_trades = int(s2[s2['Metric'] == 'Total Trades Executed']['Value'].values[0])
s3_trades = int(s3[s3['Metric'] == 'Total Trades Executed']['Value'].values[0])
s2_avg_pnl = float(s2[s2['Metric'] == 'Average P&L per Trade']['Value'].values[0].replace('$', ''))
s3_avg_pnl = float(s3[s3['Metric'] == 'Average P&L per Trade']['Value'].values[0].replace('$', ''))

print(f"\n1. PERFORMANCE:")
print(f"   Strategy 2: ${s2_final:,.2f} ({s2_return:.2f}% return)")
print(f"   Strategy 3: ${s3_final:,.2f} ({s3_return:.2f}% return)")
print(f"   Difference: ${s3_final - s2_final:,.2f} ({(s3_return - s2_return):.2f}% points)")
if s2_final > s3_final:
        print(f"   -> Strategy 2 outperforms by ${s2_final - s3_final:,.2f} ({(s2_return - s3_return):.2f}% points)")
else:
    print(f"   -> Strategy 3 outperforms by ${s3_final - s2_final:,.2f} ({(s3_return - s2_return):.2f}% points)")

print(f"\n2. TRADING ACTIVITY:")
print(f"   Strategy 2: {s2_trades} trades executed")
print(f"   Strategy 3: {s3_trades} trades executed")
print(f"   Difference: {s3_trades - s2_trades} trades ({((s3_trades - s2_trades) / s2_trades * 100):.1f}% fewer)")
if s2_trades > s3_trades:
    print(f"   -> Strategy 2 is more active ({(s2_trades - s3_trades)} more trades)")
else:
    print(f"   -> Strategy 3 is more active ({(s3_trades - s2_trades)} more trades)")

print(f"\n3. AVERAGE TRADE QUALITY:")
print(f"   Strategy 2: ${s2_avg_pnl:.2f} per trade")
print(f"   Strategy 3: ${s3_avg_pnl:.2f} per trade")
print(f"   Difference: ${s3_avg_pnl - s2_avg_pnl:.2f} per trade")
if s2_avg_pnl > s3_avg_pnl:
    print(f"   -> Strategy 2 has higher average P&L per trade")
else:
    print(f"   -> Strategy 3 has higher average P&L per trade")

# Position holding analysis
s2_zero_days = int(s2[s2['Metric'] == 'Days with Zero Position at End']['Value'].values[0])
s3_zero_days = int(s3[s3['Metric'] == 'Days with Zero Position at End']['Value'].values[0])
s2_pos_days = int(s2[s2['Metric'] == 'Days with Position at End']['Value'].values[0])
s3_pos_days = int(s3[s3['Metric'] == 'Days with Position at End']['Value'].values[0])

print(f"\n4. POSITION HOLDING:")
print(f"   Strategy 2: {s2_zero_days} days with zero position, {s2_pos_days} days with position")
print(f"   Strategy 3: {s3_zero_days} days with zero position, {s3_pos_days} days with position")
print(f"   -> Strategy 3 holds positions longer ({s3_pos_days - s2_pos_days} more days with position)")

# Cross-day trades
s2_cross = int(s2[s2['Metric'] == 'Total Cross-Day Trades']['Value'].values[0])
s3_cross = int(s3[s3['Metric'] == 'Total Cross-Day Trades']['Value'].values[0])
s2_cross_pnl = float(s2[s2['Metric'] == 'Cross-Day Total P&L']['Value'].values[0].replace('$', '').replace(',', ''))
s3_cross_pnl = float(s3[s3['Metric'] == 'Cross-Day Total P&L']['Value'].values[0].replace('$', '').replace(',', ''))

print(f"\n5. CROSS-DAY TRADES:")
print(f"   Strategy 2: {s2_cross} cross-day trades, ${s2_cross_pnl:.2f} total P&L")
print(f"   Strategy 3: {s3_cross} cross-day trades, ${s3_cross_pnl:.2f} total P&L")
if s2_cross > 0:
    print(f"   Strategy 2 avg: ${s2_cross_pnl / s2_cross:.2f} per cross-day trade")
if s3_cross > 0:
    print(f"   Strategy 3 avg: ${s3_cross_pnl / s3_cross:.2f} per cross-day trade")

print("\n" + "=" * 100)
print("KEY DIFFERENCES:")
print("=" * 100)
print("Strategy 2: Uses 1,1,2,2,3,4,4 share allocation (up to 3.0% drop)")
print("Strategy 3: Uses 3,3,6 share allocation (up to 1.0% drop) with 1.5% stop-loss")
print("\nStrategy 2 allows deeper accumulation (up to 3% drop) with more trades")
print("Strategy 3 uses larger initial positions but limits accumulation to 1% drop")
print("=" * 100)

