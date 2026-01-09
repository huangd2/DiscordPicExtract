import pandas as pd

# Read the trades CSV
df = pd.read_csv('strategy3/strategy3_low_risk_accumulation_trades.csv')

# Filter for stop-loss trades only
stop_losses = df[df['buy/sell'] == 'Stop-Loss'].copy()

# Extract trade numbers (only rows with actual trade numbers)
stop_losses['trade_num'] = pd.to_numeric(stop_losses['trade #'], errors='coerce')
stop_losses = stop_losses[stop_losses['trade_num'].notna()].copy()
stop_losses = stop_losses.sort_values('trade_num')

print(f"Total stop-loss trades: {len(stop_losses)}")
print(f"\nStop-loss trade numbers: {sorted(stop_losses['trade_num'].astype(int).tolist())}")

# Find consecutive stop-loss trades
consecutive_pairs = []
prev_trade_num = None

for idx, row in stop_losses.iterrows():
    current_trade_num = int(row['trade_num'])
    if prev_trade_num is not None and current_trade_num == prev_trade_num + 1:
        consecutive_pairs.append((prev_trade_num, current_trade_num, row['timestamp']))
    prev_trade_num = current_trade_num

print(f"\nBack-to-back stop-loss pairs: {len(consecutive_pairs)}")

if consecutive_pairs:
    print("\nBack-to-back stop-loss trades:")
    for trade1, trade2, timestamp2 in consecutive_pairs:
        # Get details for both trades
        trade1_row = stop_losses[stop_losses['trade_num'] == trade1].iloc[0]
        trade2_row = stop_losses[stop_losses['trade_num'] == trade2].iloc[0]
        print(f"\n  Trade {trade1} -> Trade {trade2}")
        print(f"    Trade {trade1}: {trade1_row['timestamp']}, PnL: ${trade1_row['PnL']:.2f}")
        print(f"    Trade {trade2}: {trade2_row['timestamp']}, PnL: ${trade2_row['PnL']:.2f}")
else:
    print("\nNo back-to-back stop-loss trades found!")

