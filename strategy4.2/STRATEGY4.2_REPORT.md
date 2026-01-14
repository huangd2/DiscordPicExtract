# Strategy 4.2: Progressive Exit (Even Thirds) with Avg Price Exit

## Overview

Strategy 4.2 is an enhanced version of Strategy 4.1 that modifies the stop-loss behavior after the first sell to provide better protection of partial profits. Instead of resetting the exit sequence when price drops below the average buy price, Strategy 4.2 exits the remaining position at the average buy price (breakeven), locking in the profit from the first sell.

## Key Features

- **Entry Strategy**: Same as Strategy 4.1 - Progressive accumulation with 3 initial shares, then 3 shares at 0.5% drop, and 6 shares at 1.0% drop
- **Exit Strategy**: Modified to sell in three equal portions (33% each) instead of 50%/25%/25%
- **Stop-Loss**: 
  - Before any sells: 1.5% drop from average buy price
  - After 1st sell: **NEW** - Exits at avg_buy_price if price drops below it (in addition to 1.5% stop-loss)
  - After 2nd sell: Uses first sell price as trailing stop-loss
- **Exit Conditions**: 
  - First sell: 33% when price > avg buy price
  - Second sell: 33% when price > avg buy price (no lower buy signals since last sell)
  - Third sell: Remaining 33% when price > avg buy price (no lower buy signals since last sell)

## Key Logic Modification

### After First Sell (`sell_stage == 1`)

**Strategy 4.1 Behavior:**
- Only checks 1.5% stop-loss from `avg_buy_price`
- If buy price < `avg_buy_price`, resets `sell_stage` to 0 and restarts exit sequence

**Strategy 4.2 Behavior:**
- Checks **BOTH**:
  1. 1.5% stop-loss from `avg_buy_price` (takes precedence)
  2. If price < `avg_buy_price`, exits remaining position at `avg_buy_price`
- Reset logic only works before any sells (`sell_stage == 0`)

### Code Implementation

```python
# Buy Signal Handling - After First Sell
elif sell_stage == 1:
    # After 1st sell: check both 1.5% stop-loss and avg_buy_price exit
    if f_price <= stop_loss_price:
        # 1.5% stop-loss triggered
        stop_loss_triggered = True
        stop_loss_execution_price = stop_loss_price
    elif f_price < avg_buy_price:
        # Price dropped below avg_buy_price - exit at avg_buy_price
        stop_loss_triggered = True
        stop_loss_execution_price = avg_buy_price

# Reset Logic - Only Before Any Sells
if sell_stage == 0 and f_price < avg_buy_price:
    # Reset sell stage to allow restarting the partial exit sequence
    sell_stage = 0
    # ... reset variables
```

## Performance Results

### Overall Performance
- **Initial Capital**: $10,000.00
- **Final Portfolio Value**: $10,928.21
- **Total P&L**: $928.21
- **Return**: 9.28%

### Trade Statistics
- **Total Trades Executed**: 148
- **Winning Trades**: 111 (75.0%)
- **Losing Trades**: 37 (25.0%)
- **Stop-Loss Triggered**: 59 (39.9%)
- **Average P&L per Trade**: $6.27
- **Average Winning Trade**: $5.45
- **Average Losing Trade**: -$17.95
- **Average Stop-Loss Trade**: -$10.13

### Cross-Day Performance
- **Total Cross-Day Trades**: 83
- **Cross-Day Wins**: 61 (73.5%)
- **Cross-Day Losses**: 22 (26.5%)
- **Cross-Day Total P&L**: -$106.64

### Daily Statistics
- **Total Trading Days**: 207
- **Days with Zero Position at End**: 94
- **Days with Position at End**: 113
- **Winning Days**: 134 (64.7%)
- **Losing Days**: 8 (3.9%)
- **Average Trades per Day**: 2.78

## Comparison: Strategy 4.1 vs Strategy 4.2

### Performance Comparison

| Metric | Strategy 4.1 | Strategy 4.2 | Difference |
|--------|--------------|--------------|------------|
| **Final Portfolio Value** | $10,973.27 | $10,928.21 | -$45.06 (-0.41%) |
| **Total P&L** | $973.27 | $928.21 | -$45.06 |
| **Return %** | 9.73% | 9.28% | -0.45% |
| **Total Trades** | 100 | 148 | +48 (+48%) |
| **Win Rate** | 89.0% | 75.0% | -14.0% |
| **Losing Trades** | 11 | 37 | +26 (+236%) |
| **Stop-Loss Triggered** | 30 (30.0%) | 59 (39.9%) | +29 (+96.7%) |
| **Avg P&L per Trade** | $9.73 | $6.27 | -$3.46 (-35.6%) |
| **Avg Winning Trade** | $7.78 | $5.45 | -$2.33 (-29.9%) |
| **Avg Losing Trade** | -$59.37 | -$17.95 | +$41.42 (+69.8%) |
| **Avg Stop-Loss Trade** | -$19.37 | -$10.13 | +$9.24 (+47.7%) |
| **Cross-Day Trades** | 65 | 83 | +18 (+27.7%) |
| **Cross-Day Win Rate** | 87.7% | 73.5% | -14.2% |
| **Cross-Day Total P&L** | $30.99 | -$106.64 | -$137.63 |
| **Days with Position** | 132 | 113 | -19 (-14.4%) |

### Key Differences

#### 1. **More Frequent Exits (48% More Trades)**
- Strategy 4.2 exits positions earlier when price drops below `avg_buy_price` after the first sell
- More opportunities to re-enter positions
- Higher transaction frequency

#### 2. **Lower Win Rate (75% vs 89%)**
- Strategy 4.2 exits at `avg_buy_price` (breakeven) more often
- Some positions that might have recovered are exited early
- More trades closed at breakeven or small losses

#### 3. **Smaller Average Losses (-$17.95 vs -$59.37)**
- Strategy 4.2 exits earlier at `avg_buy_price` instead of waiting for 1.5% stop-loss
- Better risk management
- Average losing trade is 70% smaller

#### 4. **Lower Overall Return (9.28% vs 9.73%)**
- More frequent exits at breakeven reduce overall profitability
- Some positions that would have recovered in Strategy 4.1 are exited early
- The protective exit prevents some losses but also prevents some recoveries

#### 5. **More Stop-Loss Triggers (39.9% vs 30.0%)**
- Strategy 4.2 has two exit conditions after first sell:
  1. 1.5% stop-loss (same as 4.1)
  2. Price < `avg_buy_price` exit (new)
- More defensive exits
- Better protection of partial profits

### Trade-offs

#### Strategy 4.1 Advantages:
- ✅ Higher overall return (9.73% vs 9.28%)
- ✅ Higher win rate (89% vs 75%)
- ✅ Better cross-day performance
- ✅ Fewer trades (less transaction costs in real trading)
- ✅ More "forgiving" - gives trades time to recover

#### Strategy 4.2 Advantages:
- ✅ Better risk management (smaller average losses)
- ✅ More protective of partial profits
- ✅ More consistent exits (less variance)
- ✅ Exits at breakeven prevent larger losses
- ✅ More defensive approach

## Recommendations

### Use Strategy 4.1 When:
- You want **higher returns** and can tolerate larger losses
- Markets have **higher volatility** and good recovery potential
- You prefer giving trades **time to recover**
- You want **fewer transactions**

### Use Strategy 4.2 When:
- You prioritize **risk management** and protecting partial profits
- Markets have **limited recovery potential**
- You want **more consistent, defensive exits**
- You prefer **smaller losses** over maximum returns

## Conclusion

**Strategy 4.1** is more profitable but takes more risk by allowing positions to reset and potentially recover. It's better for markets with higher volatility and recovery potential, and for traders willing to accept larger losses for higher returns.

**Strategy 4.2** is more conservative and protective, exiting earlier to lock in partial profits. It's better for risk-averse traders, markets with less recovery potential, and when protecting capital and partial profits is the priority.

The choice between them depends on **risk tolerance** and **market conditions**. Strategy 4.2 sacrifices some upside potential for better downside protection, making it a more defensive approach suitable for risk-averse trading scenarios.

## Files Generated

- `strategy4_progressive_exit_even_thirds_v2_trades.csv` - All trade actions (599 actions)
- `strategy4_v2_statistics.csv` - Detailed performance statistics
- `equity_curve.png` - Portfolio value over time
- `trade_win_loss.png` - Win/loss distribution
- `daily_pnl_over_time.png` - Daily P&L timeline
- `daily_pnl_histogram.png` - Daily P&L distribution
- `daily_positions.png` - Position state visualization
- `trades_per_day_histogram.png` - Trade frequency distribution

## Implementation Details

The strategy is implemented in `strategy4_progressive_exit_even_thirds_v2.py` and can be run with:

```bash
python strategy4_progressive_exit_even_thirds_v2.py
```

All results are saved to the `strategy4.2/` directory.

