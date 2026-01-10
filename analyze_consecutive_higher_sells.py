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

# Iterate through the dataframe to find the pattern:
# Buy (executed) -> Sell (higher than buy) -> Another Sell (higher than buy, no signals in between with price < buy)
for i in range(len(df)):
    row = df.iloc[i]
    
    # Only process buy signals (executed buys)
    if row['buy/sell'] != 'Buy':
        continue
    
    buy_price = row['fPrice']
    buy_timestamp = row['timestamp']
    buy_risk = row['risk']
    
    result = {
        'buy_timestamp': buy_timestamp,
        'buy_price': buy_price,
        'buy_risk': buy_risk,
        'has_first_higher_sell': False,
        'first_sell_price': None,
        'first_sell_timestamp': None,
        'first_sell_pct_increase': None,
        'has_second_higher_sell': False,
        'second_sell_price': None,
        'second_sell_timestamp': None,
        'second_sell_pct_increase': None,
        'signals_between_count': None,
        'low_price_signal_found': False,
        'lowest_price_between': None,
    }
    
    # Check if the immediate next signal is a Sell that's higher than the buy price
    first_sell_pos = None
    if i + 1 < len(df):
        next_row = df.iloc[i + 1]
        if next_row['buy/sell'] == 'Sell' and next_row['fPrice'] > buy_price:
            first_sell_pos = i + 1
            first_sell = next_row
            result['has_first_higher_sell'] = True
            result['first_sell_price'] = first_sell['fPrice']
            result['first_sell_timestamp'] = first_sell['timestamp']
            result['first_sell_pct_increase'] = ((first_sell['fPrice'] - buy_price) / buy_price) * 100
    
    # If we found the first higher sell, look for a second higher sell
    # Check all potential second sells and only count those with no signals < buy_price in between
    if first_sell_pos is not None:
        second_sell_pos = None
        found_low_price_before_second = False
        
        # Look for all potential second sells
        for j in range(first_sell_pos + 1, len(df)):
            next_row = df.iloc[j]
            
            # If we find a sell signal that's higher than buy_price, check if there are any low-price signals before it
            if next_row['buy/sell'] == 'Sell' and next_row['fPrice'] > buy_price:
                # Check all signals between first_sell and this potential second_sell
                has_low_price_between = False
                signals_between = []
                lowest_in_range = None
                
                for k in range(first_sell_pos + 1, j):
                    signal_between = df.iloc[k]
                    signals_between.append({
                        'type': signal_between['buy/sell'],
                        'price': signal_between['fPrice'],
                        'timestamp': signal_between['timestamp']
                    })
                    
                    # Track the lowest price we see
                    if lowest_in_range is None or signal_between['fPrice'] < lowest_in_range:
                        lowest_in_range = signal_between['fPrice']
                    
                    # Check if any signal has price < buy_price
                    if signal_between['fPrice'] < buy_price:
                        has_low_price_between = True
                        break
                
                # Only count this as second sell if there are NO low-price signals in between
                if not has_low_price_between:
                    second_sell_pos = j
                    second_sell = next_row
                    result['has_second_higher_sell'] = True
                    result['second_sell_price'] = second_sell['fPrice']
                    result['second_sell_timestamp'] = second_sell['timestamp']
                    result['second_sell_pct_increase'] = ((second_sell['fPrice'] - buy_price) / buy_price) * 100
                    result['signals_between_count'] = len(signals_between)
                    result['lowest_price_between'] = lowest_in_range if lowest_in_range is not None else buy_price
                    break
                else:
                    # Found a low-price signal before this second sell
                    found_low_price_before_second = True
                    result['low_price_signal_found'] = True
                    result['lowest_price_between'] = lowest_in_range
                    result['signals_between_count'] = len(signals_between)
                    # Continue looking for another potential second sell (but we'll mark that we found low price)
            
            # Track if we encounter a low-price signal before finding any second sell
            elif next_row['fPrice'] < buy_price and second_sell_pos is None:
                found_low_price_before_second = True
                result['low_price_signal_found'] = True
                if result['lowest_price_between'] is None or next_row['fPrice'] < result['lowest_price_between']:
                    result['lowest_price_between'] = next_row['fPrice']
    
    results.append(result)

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Calculate statistics
print("=" * 80)
print("CONSECUTIVE HIGHER SELLS ANALYSIS")
print("=" * 80)
print()
print("Pattern: Buy (executed) -> Immediate Next Signal is Sell (higher) -> Sell (higher, no signals < buy_price in between)")
print()

total_buys = len(results_df)
print(f"Total Buy Signals (Executed): {total_buys}")
print()

# First higher sell statistics
print("1ST HIGHER SELL (immediate next signal after buy):")
print("-" * 80)
has_first_higher_sell = results_df['has_first_higher_sell'].sum()
print(f"  Buy signals with immediate next signal = Sell (higher than buy price): {has_first_higher_sell} ({has_first_higher_sell/total_buys*100:.2f}%)")

if has_first_higher_sell > 0:
    first_sell_pct = results_df[results_df['has_first_higher_sell']]['first_sell_pct_increase']
    print(f"  Average % increase: {first_sell_pct.mean():.4f}%")
    print(f"  Median % increase: {first_sell_pct.median():.4f}%")
    print(f"  Min % increase: {first_sell_pct.min():.4f}%")
    print(f"  Max % increase: {first_sell_pct.max():.4f}%")
print()

# Second higher sell statistics (conditional on first higher sell)
print("2ND HIGHER SELL (after 1st higher sell, no signals < buy_price in between):")
print("-" * 80)
has_second_higher_sell = results_df['has_second_higher_sell'].sum()
print(f"  Buy signals with 2nd sell higher than buy price: {has_second_higher_sell} ({has_second_higher_sell/total_buys*100:.2f}%)")

# Conditional probability: P(2nd higher sell | 1st higher sell)
if has_first_higher_sell > 0:
    conditional_prob = (has_second_higher_sell / has_first_higher_sell) * 100
    print(f"  Conditional probability (given 1st higher sell exists): {conditional_prob:.2f}%")
    print()
    
    # Cases where low price signal was found
    low_price_found = results_df[results_df['has_first_higher_sell'] & results_df['low_price_signal_found']]
    print(f"  Cases where low price signal (< buy_price) found before 2nd sell: {len(low_price_found)} ({len(low_price_found)/has_first_higher_sell*100:.2f}%)")
    
    if has_second_higher_sell > 0:
        second_sell_pct = results_df[results_df['has_second_higher_sell']]['second_sell_pct_increase']
        print(f"  Average % increase: {second_sell_pct.mean():.4f}%")
        print(f"  Median % increase: {second_sell_pct.median():.4f}%")
        print(f"  Min % increase: {second_sell_pct.min():.4f}%")
        print(f"  Max % increase: {second_sell_pct.max():.4f}%")
        
        # Signals between statistics
        signals_between = results_df[results_df['has_second_higher_sell']]['signals_between_count']
        print(f"  Average signals between 1st and 2nd sell: {signals_between.mean():.2f}")
        print(f"  Median signals between: {signals_between.median():.0f}")
print()

# Summary statistics table
print("=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print()

summary_data = {
    'Metric': [
        'Total Buy Signals',
        'Has 1st Higher Sell',
        'Has 2nd Higher Sell (no low signals)',
        'Low Price Signal Found (blocked 2nd sell)',
    ],
    'Count': [
        total_buys,
        has_first_higher_sell,
        has_second_higher_sell,
        len(low_price_found) if has_first_higher_sell > 0 else 0,
    ],
    'Percentage of Total': [
        100.0,
        has_first_higher_sell/total_buys*100 if total_buys > 0 else 0,
        has_second_higher_sell/total_buys*100 if total_buys > 0 else 0,
        len(low_price_found)/total_buys*100 if total_buys > 0 else 0,
    ],
    'Percentage of 1st Higher Sell': [
        '-',
        100.0,
        has_second_higher_sell/has_first_higher_sell*100 if has_first_higher_sell > 0 else 0,
        len(low_price_found)/has_first_higher_sell*100 if has_first_higher_sell > 0 else 0,
    ]
}

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))
print()

# Detailed analysis: Compare prices
if has_second_higher_sell > 0:
    print("=" * 80)
    print("PRICE COMPARISON (2nd sell vs 1st sell)")
    print("=" * 80)
    print()
    
    second_sell_df = results_df[results_df['has_second_higher_sell']].copy()
    second_sell_df['price_diff'] = second_sell_df['second_sell_price'] - second_sell_df['first_sell_price']
    second_sell_df['price_diff_pct'] = ((second_sell_df['second_sell_price'] - second_sell_df['first_sell_price']) / second_sell_df['first_sell_price']) * 100
    
    higher_than_first = (second_sell_df['second_sell_price'] > second_sell_df['first_sell_price']).sum()
    equal_to_first = (second_sell_df['second_sell_price'] == second_sell_df['first_sell_price']).sum()
    lower_than_first = (second_sell_df['second_sell_price'] < second_sell_df['first_sell_price']).sum()
    
    print(f"2nd sell higher than 1st sell: {higher_than_first} ({higher_than_first/has_second_higher_sell*100:.2f}%)")
    print(f"2nd sell equal to 1st sell: {equal_to_first} ({equal_to_first/has_second_higher_sell*100:.2f}%)")
    print(f"2nd sell lower than 1st sell: {lower_than_first} ({lower_than_first/has_second_higher_sell*100:.2f}%)")
    print()
    
    if higher_than_first > 0:
        higher_pct = second_sell_df[second_sell_df['second_sell_price'] > second_sell_df['first_sell_price']]['price_diff_pct']
        print(f"Average % increase (2nd vs 1st): {higher_pct.mean():.4f}%")
        print(f"Median % increase: {higher_pct.median():.4f}%")
    
    if lower_than_first > 0:
        lower_pct = second_sell_df[second_sell_df['second_sell_price'] < second_sell_df['first_sell_price']]['price_diff_pct']
        print(f"Average % decrease (2nd vs 1st): {lower_pct.mean():.4f}%")
        print(f"Median % decrease: {lower_pct.median():.4f}%")
    print()

# Save detailed results to CSV
output_file = 'consecutive_higher_sells_analysis.csv'
results_df.to_csv(output_file, index=False)
print(f"Detailed results saved to: {output_file}")
print("=" * 80)

