import pandas as pd
import numpy as np

# Read the combined data
print("Reading combined_data.csv...")
df = pd.read_csv('combined_data.csv')

# Parse timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

# Normalize buy/sell column
df['buy/sell'] = df['buy/sell'].str.strip().str.capitalize()

# Read the analysis results
results_df = pd.read_csv('consecutive_higher_sells_analysis.csv')

# Get cases with second higher sell
second_sell_cases = results_df[results_df['has_second_higher_sell'] == True].copy()

print(f"Analyzing {len(second_sell_cases)} cases with 2nd higher sell...")
print()

third_sell_count = 0
third_sell_details = []

for idx, row in second_sell_cases.iterrows():
    buy_price = row['buy_price']
    buy_timestamp = pd.to_datetime(row['buy_timestamp'])
    second_sell_timestamp = pd.to_datetime(row['second_sell_timestamp'])
    
    # Find indices in the main dataframe
    buy_idx = df[df['timestamp'] == buy_timestamp].index[0]
    second_sell_idx = df[df['timestamp'] == second_sell_timestamp].index[0]
    
    found_third = False
    third_sell_price = None
    third_sell_timestamp = None
    
    # Look for third sell after second sell
    for j in range(second_sell_idx + 1, len(df)):
        next_row = df.iloc[j]
        
        # If we find a sell signal that's higher than buy_price, check if there are any low-price signals before it
        if next_row['buy/sell'] == 'Sell' and next_row['fPrice'] > buy_price:
            # Check all signals between second_sell and this potential third_sell
            has_low_between = False
            
            for k in range(second_sell_idx + 1, j):
                signal_between = df.iloc[k]
                # Check if any signal has price < buy_price
                if signal_between['fPrice'] < buy_price:
                    has_low_between = True
                    break
            
            # Only count this as third sell if there are NO low-price signals in between
            if not has_low_between:
                found_third = True
                third_sell_price = next_row['fPrice']
                third_sell_timestamp = next_row['timestamp']
                break
        
        # If we encounter a low-price signal before finding any third sell, stop looking
        elif next_row['fPrice'] < buy_price:
            break
    
    if found_third:
        third_sell_count += 1
        third_sell_details.append({
            'buy_timestamp': buy_timestamp,
            'buy_price': buy_price,
            'second_sell_price': row['second_sell_price'],
            'third_sell_price': third_sell_price,
            'third_sell_timestamp': third_sell_timestamp,
            'second_vs_first': third_sell_price > row['first_sell_price'],
            'third_vs_second': third_sell_price > row['second_sell_price'],
        })

print("=" * 80)
print("THIRD HIGHER SELL ANALYSIS")
print("=" * 80)
print()
print(f"Cases with 2nd higher sell: {len(second_sell_cases)}")
print(f"Cases with 3rd higher sell (no low signals between 2nd and 3rd): {third_sell_count} ({third_sell_count/len(second_sell_cases)*100:.2f}%)")
print()

if third_sell_count > 0:
    details_df = pd.DataFrame(third_sell_details)
    
    # Compare third sell vs first sell
    third_higher_than_first = details_df['second_vs_first'].sum()
    print(f"3rd sell price > 1st sell price: {third_higher_than_first} ({third_higher_than_first/third_sell_count*100:.2f}%)")
    
    # Compare third sell vs second sell
    third_higher_than_second = details_df['third_vs_second'].sum()
    print(f"3rd sell price > 2nd sell price: {third_higher_than_second} ({third_higher_than_second/third_sell_count*100:.2f}%)")
    print()
    
    # Price increases
    details_df['third_vs_buy_pct'] = ((details_df['third_sell_price'] - details_df['buy_price']) / details_df['buy_price']) * 100
    details_df['third_vs_second_pct'] = ((details_df['third_sell_price'] - details_df['second_sell_price']) / details_df['second_sell_price']) * 100
    
    print(f"Average % increase (3rd sell vs buy): {details_df['third_vs_buy_pct'].mean():.4f}%")
    print(f"Average % increase (3rd sell vs 2nd sell): {details_df['third_vs_second_pct'].mean():.4f}%")
    print()

print("=" * 80)

