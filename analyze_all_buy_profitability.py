import pandas as pd
import numpy as np
from datetime import datetime

# Read the combined data
print("Reading combined_data.csv...")
df = pd.read_csv('combined_data.csv')

# Parse timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date

# Sort by timestamp
df = df.sort_values('timestamp').reset_index(drop=True)

# Normalize buy/sell column
df['buy/sell'] = df['buy/sell'].str.strip().str.capitalize()

print(f"Total signals: {len(df)}")
print(f"Buy signals: {len(df[df['buy/sell'] == 'Buy'])}")
print(f"Sell signals: {len(df[df['buy/sell'] == 'Sell'])}")
print()

# Initialize results
results = []

# Analyze ALL buy signals for profitability
for i in range(len(df)):
    row = df.iloc[i]
    
    if row['buy/sell'] != 'Buy':
        continue
    
    buy_price = row['fPrice']
    buy_timestamp = row['timestamp']
    buy_risk = row['risk']
    
    result = {
        'buy_timestamp': buy_timestamp,
        'buy_price': buy_price,
        'buy_risk': buy_risk,
        'pattern_type': None,
        'has_profitable_sell': False,
        'first_profitable_sell_price': None,
        'first_profitable_sell_timestamp': None,
        'profit_pct': None,
        'duration_minutes': None,
        'signals_until_profitable_sell': None,
        'has_any_sell': False,
        'first_sell_price': None,
        'first_sell_timestamp': None,
        'first_sell_profit_pct': None,
    }
    
    # Check what pattern this buy signal follows
    # Pattern 1: Buy -> Sell
    if i + 1 < len(df) and df.iloc[i + 1]['buy/sell'] == 'Sell':
        result['pattern_type'] = 'Buy->Sell'
        sell1 = df.iloc[i + 1]
        result['has_any_sell'] = True
        result['first_sell_price'] = sell1['fPrice']
        result['first_sell_timestamp'] = sell1['timestamp']
        result['first_sell_profit_pct'] = ((sell1['fPrice'] - buy_price) / buy_price) * 100
        
        if sell1['fPrice'] > buy_price:
            result['has_profitable_sell'] = True
            result['first_profitable_sell_price'] = sell1['fPrice']
            result['first_profitable_sell_timestamp'] = sell1['timestamp']
            result['profit_pct'] = result['first_sell_profit_pct']
            duration = sell1['timestamp'] - buy_timestamp
            result['duration_minutes'] = duration.total_seconds() / 60
            result['signals_until_profitable_sell'] = 1
    
    # Pattern 2: Buy -> Buy -> Sell
    elif (i + 2 < len(df) and 
          df.iloc[i + 1]['buy/sell'] == 'Buy' and 
          df.iloc[i + 2]['buy/sell'] == 'Sell'):
        result['pattern_type'] = 'Buy->Buy->Sell'
        sell1 = df.iloc[i + 2]
        result['has_any_sell'] = True
        result['first_sell_price'] = sell1['fPrice']
        result['first_sell_timestamp'] = sell1['timestamp']
        result['first_sell_profit_pct'] = ((sell1['fPrice'] - buy_price) / buy_price) * 100
        
        if sell1['fPrice'] > buy_price:
            result['has_profitable_sell'] = True
            result['first_profitable_sell_price'] = sell1['fPrice']
            result['first_profitable_sell_timestamp'] = sell1['timestamp']
            result['profit_pct'] = result['first_sell_profit_pct']
            duration = sell1['timestamp'] - buy_timestamp
            result['duration_minutes'] = duration.total_seconds() / 60
            result['signals_until_profitable_sell'] = 2
    
    # Pattern 3: Buy -> Buy -> Buy -> Sell
    elif (i + 3 < len(df) and 
          df.iloc[i + 1]['buy/sell'] == 'Buy' and 
          df.iloc[i + 2]['buy/sell'] == 'Buy' and 
          df.iloc[i + 3]['buy/sell'] == 'Sell'):
        result['pattern_type'] = 'Buy->Buy->Buy->Sell'
        sell1 = df.iloc[i + 3]
        result['has_any_sell'] = True
        result['first_sell_price'] = sell1['fPrice']
        result['first_sell_timestamp'] = sell1['timestamp']
        result['first_sell_profit_pct'] = ((sell1['fPrice'] - buy_price) / buy_price) * 100
        
        if sell1['fPrice'] > buy_price:
            result['has_profitable_sell'] = True
            result['first_profitable_sell_price'] = sell1['fPrice']
            result['first_profitable_sell_timestamp'] = sell1['timestamp']
            result['profit_pct'] = result['first_sell_profit_pct']
            duration = sell1['timestamp'] - buy_timestamp
            result['duration_minutes'] = duration.total_seconds() / 60
            result['signals_until_profitable_sell'] = 3
    
    # Pattern 4: Buy -> Buy -> Buy -> Buy -> Sell
    elif (i + 4 < len(df) and 
          df.iloc[i + 1]['buy/sell'] == 'Buy' and 
          df.iloc[i + 2]['buy/sell'] == 'Buy' and 
          df.iloc[i + 3]['buy/sell'] == 'Buy' and 
          df.iloc[i + 4]['buy/sell'] == 'Sell'):
        result['pattern_type'] = 'Buy->Buy->Buy->Buy->Sell'
        sell1 = df.iloc[i + 4]
        result['has_any_sell'] = True
        result['first_sell_price'] = sell1['fPrice']
        result['first_sell_timestamp'] = sell1['timestamp']
        result['first_sell_profit_pct'] = ((sell1['fPrice'] - buy_price) / buy_price) * 100
        
        if sell1['fPrice'] > buy_price:
            result['has_profitable_sell'] = True
            result['first_profitable_sell_price'] = sell1['fPrice']
            result['first_profitable_sell_timestamp'] = sell1['timestamp']
            result['profit_pct'] = result['first_sell_profit_pct']
            duration = sell1['timestamp'] - buy_timestamp
            result['duration_minutes'] = duration.total_seconds() / 60
            result['signals_until_profitable_sell'] = 4
    
    # Other patterns - look for ANY sell signal within next 10 signals
    else:
        result['pattern_type'] = 'Other'
        
        # Look for first sell signal within next 10 signals
        sell_found = False
        for j in range(i + 1, min(i + 11, len(df))):
            future_signal = df.iloc[j]
            
            if future_signal['buy/sell'] == 'Sell':
                sell_found = True
                result['has_any_sell'] = True
                result['first_sell_price'] = future_signal['fPrice']
                result['first_sell_timestamp'] = future_signal['timestamp']
                result['first_sell_profit_pct'] = ((future_signal['fPrice'] - buy_price) / buy_price) * 100
                
                if future_signal['fPrice'] > buy_price:
                    result['has_profitable_sell'] = True
                    result['first_profitable_sell_price'] = future_signal['fPrice']
                    result['first_profitable_sell_timestamp'] = future_signal['timestamp']
                    result['profit_pct'] = result['first_sell_profit_pct']
                    duration = future_signal['timestamp'] - buy_timestamp
                    result['duration_minutes'] = duration.total_seconds() / 60
                    result['signals_until_profitable_sell'] = j - i
                break
        
        # If no sell in next 10 signals, check further (up to 20 signals)
        if not sell_found:
            for j in range(i + 11, min(i + 21, len(df))):
                future_signal = df.iloc[j]
                
                if future_signal['buy/sell'] == 'Sell':
                    result['has_any_sell'] = True
                    result['first_sell_price'] = future_signal['fPrice']
                    result['first_sell_timestamp'] = future_signal['timestamp']
                    result['first_sell_profit_pct'] = ((future_signal['fPrice'] - buy_price) / buy_price) * 100
                    
                    if future_signal['fPrice'] > buy_price:
                        result['has_profitable_sell'] = True
                        result['first_profitable_sell_price'] = future_signal['fPrice']
                        result['first_profitable_sell_timestamp'] = future_signal['timestamp']
                        result['profit_pct'] = result['first_sell_profit_pct']
                        duration = future_signal['timestamp'] - buy_timestamp
                        result['duration_minutes'] = duration.total_seconds() / 60
                        result['signals_until_profitable_sell'] = j - i
                    break
    
    results.append(result)

# Convert to DataFrame
results_df = pd.DataFrame(results)

print("=" * 80)
print("COMPREHENSIVE BUY SIGNAL PROFITABILITY ANALYSIS")
print("=" * 80)
print()

total_buys = len(results_df)
print(f"Total Buy Signals: {total_buys}")
print()

# Overall profitability
profitable = results_df['has_profitable_sell'].sum()
profitable_pct = profitable / total_buys * 100
print(f"Buy signals with profitable sell opportunity: {profitable} ({profitable_pct:.2f}%)")
print()

# Breakdown by pattern
print("=" * 80)
print("PROFITABILITY BY PATTERN")
print("=" * 80)
print()

pattern_summary = []
patterns = ['Buy->Sell', 'Buy->Buy->Sell', 'Buy->Buy->Buy->Sell', 'Buy->Buy->Buy->Buy->Sell', 'Other']

for pattern in patterns:
    pattern_df = results_df[results_df['pattern_type'] == pattern]
    
    if len(pattern_df) == 0:
        continue
    
    pattern_profitable = pattern_df['has_profitable_sell'].sum()
    pattern_total = len(pattern_df)
    pattern_profitable_pct = pattern_profitable / pattern_total * 100 if pattern_total > 0 else 0
    
    pattern_summary.append({
        'Pattern': pattern,
        'Total Buy Signals': pattern_total,
        'Profitable': pattern_profitable,
        'Profitability %': pattern_profitable_pct,
        'Not Profitable': pattern_total - pattern_profitable,
    })
    
    print(f"{pattern}:")
    print(f"  Total: {pattern_total} ({pattern_total/total_buys*100:.2f}% of all buys)")
    print(f"  Profitable: {pattern_profitable} ({pattern_profitable_pct:.2f}% of pattern)")
    print(f"  Not Profitable: {pattern_total - pattern_profitable}")
    
    if pattern_profitable > 0:
        profitable_pattern_df = pattern_df[pattern_df['has_profitable_sell']]
        print(f"  Average Profit: {profitable_pattern_df['profit_pct'].mean():.4f}%")
        print(f"  Median Profit: {profitable_pattern_df['profit_pct'].median():.4f}%")
        
        if pattern != 'Other':
            avg_duration = profitable_pattern_df['duration_minutes'].mean()
            median_duration = profitable_pattern_df['duration_minutes'].median()
            print(f"  Avg Duration: {avg_duration:.2f} minutes ({avg_duration/60:.2f} hours)")
            print(f"  Median Duration: {median_duration:.2f} minutes ({median_duration/60:.2f} hours)")
    
    print()

# Summary table
summary_df = pd.DataFrame(pattern_summary)
print("=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print()
print(summary_df.to_string(index=False))
print()

# Analyze "Other" pattern in detail
other_df = results_df[results_df['pattern_type'] == 'Other']
print("=" * 80)
print("DETAILED ANALYSIS: 'OTHER' PATTERNS")
print("=" * 80)
print()

if len(other_df) > 0:
    print(f"Total 'Other' pattern buy signals: {len(other_df)}")
    print()
    
    # How many have any sell signal?
    has_sell = other_df['has_any_sell'].sum()
    print(f"Buy signals with ANY sell signal (within 20 signals): {has_sell} ({has_sell/len(other_df)*100:.2f}%)")
    
    # How many have profitable sell?
    other_profitable = other_df['has_profitable_sell'].sum()
    print(f"Buy signals with profitable sell: {other_profitable} ({other_profitable/len(other_df)*100:.2f}%)")
    print()
    
    # For those with sell signals, what's the profitability?
    other_with_sell = other_df[other_df['has_any_sell']]
    if len(other_with_sell) > 0:
        profitable_rate = other_with_sell['has_profitable_sell'].sum() / len(other_with_sell) * 100
        print(f"Profitability rate (when sell exists): {profitable_rate:.2f}%")
        print()
        
        # Signals until profitable sell
        other_profitable_df = other_df[other_df['has_profitable_sell']]
        if len(other_profitable_df) > 0:
            print(f"Signals until profitable sell:")
            print(f"  Mean: {other_profitable_df['signals_until_profitable_sell'].mean():.2f}")
            print(f"  Median: {other_profitable_df['signals_until_profitable_sell'].median():.2f}")
            print(f"  Min: {other_profitable_df['signals_until_profitable_sell'].min()}")
            print(f"  Max: {other_profitable_df['signals_until_profitable_sell'].max()}")
            print()
            
            print(f"Profit Statistics:")
            print(f"  Mean: {other_profitable_df['profit_pct'].mean():.4f}%")
            print(f"  Median: {other_profitable_df['profit_pct'].median():.4f}%")
            print(f"  Min: {other_profitable_df['profit_pct'].min():.4f}%")
            print(f"  Max: {other_profitable_df['profit_pct'].max():.4f}%")
            print()
            
            print(f"Duration Statistics:")
            print(f"  Mean: {other_profitable_df['duration_minutes'].mean():.2f} minutes ({other_profitable_df['duration_minutes'].mean()/60:.2f} hours)")
            print(f"  Median: {other_profitable_df['duration_minutes'].median():.2f} minutes ({other_profitable_df['duration_minutes'].median()/60:.2f} hours)")
            print()
    
    # Check for common patterns in "Other"
    print("Common patterns in 'Other' category:")
    print("-" * 80)
    
    # Count consecutive buys before first sell
    other_with_sell = other_df[other_df['has_any_sell']].copy()
    if len(other_with_sell) > 0:
        # This is approximate - we'd need to re-analyze to get exact pattern
        # But we can see signals_until_profitable_sell distribution
        if 'signals_until_profitable_sell' in other_with_sell.columns:
            profitable_other = other_with_sell[other_with_sell['has_profitable_sell']]
            if len(profitable_other) > 0:
                signal_counts = profitable_other['signals_until_profitable_sell'].value_counts().sort_index()
                print("Signals until profitable sell (Other patterns):")
                for signals, count in signal_counts.head(10).items():
                    pct = count / len(profitable_other) * 100
                    print(f"  {int(signals)} signals: {count} cases ({pct:.2f}%)")
                print()

# Overall statistics
print("=" * 80)
print("OVERALL PROFITABILITY STATISTICS")
print("=" * 80)
print()

profitable_df = results_df[results_df['has_profitable_sell']]
print(f"Total Profitable Buy Signals: {len(profitable_df)} ({profitable_pct:.2f}%)")
print()

if len(profitable_df) > 0:
    print("Profit Statistics (All Profitable Cases):")
    print(f"  Mean: {profitable_df['profit_pct'].mean():.4f}%")
    print(f"  Median: {profitable_df['profit_pct'].median():.4f}%")
    print(f"  Min: {profitable_df['profit_pct'].min():.4f}%")
    print(f"  Max: {profitable_df['profit_pct'].max():.4f}%")
    print(f"  Std Dev: {profitable_df['profit_pct'].std():.4f}%")
    print()
    
    # Duration for all profitable (where available)
    profitable_with_duration = profitable_df[profitable_df['duration_minutes'].notna()]
    if len(profitable_with_duration) > 0:
        print("Duration Statistics (All Profitable Cases):")
        print(f"  Mean: {profitable_with_duration['duration_minutes'].mean():.2f} minutes ({profitable_with_duration['duration_minutes'].mean()/60:.2f} hours)")
        print(f"  Median: {profitable_with_duration['duration_minutes'].median():.2f} minutes ({profitable_with_duration['duration_minutes'].median()/60:.2f} hours)")
        print()

# Risk level analysis
print("=" * 80)
print("PROFITABILITY BY RISK LEVEL")
print("=" * 80)
print()

risk_levels = results_df['buy_risk'].unique()
for risk in sorted(risk_levels):
    risk_df = results_df[results_df['buy_risk'] == risk]
    risk_profitable = risk_df['has_profitable_sell'].sum()
    risk_total = len(risk_df)
    risk_pct = risk_profitable / risk_total * 100 if risk_total > 0 else 0
    
    print(f"{risk.capitalize()} Risk:")
    print(f"  Total: {risk_total}")
    print(f"  Profitable: {risk_profitable} ({risk_pct:.2f}%)")
    
    if risk_profitable > 0:
        profitable_risk_df = risk_df[risk_df['has_profitable_sell']]
        print(f"  Average Profit: {profitable_risk_df['profit_pct'].mean():.4f}%")
        print(f"  Median Profit: {profitable_risk_df['profit_pct'].median():.4f}%")
    print()

# Save results
output_file = 'all_buy_profitability_analysis.csv'
results_df.to_csv(output_file, index=False)
print(f"Detailed results saved to: {output_file}")
print("=" * 80)

