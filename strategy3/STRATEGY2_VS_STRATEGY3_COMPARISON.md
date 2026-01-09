# Strategy 2 vs Strategy 3: Comprehensive Comparison Report

## Executive Summary

This report compares **Strategy 2: Low Risk Accumulation Strategy - Progressive Buy** with **Strategy 3: Low Risk Accumulation Strategy - Progressive Buy with 1.5% Stop-Loss** based on SPX (S&P 500) signals from February 14, 2025 to December 11, 2025.

**Key Findings:**
- **Strategy 2 outperforms** with 9.06% return vs 7.12% return
- **Strategy 2 has perfect win rate** (100% vs 88.6%)
- **Strategy 3 provides stop-loss protection** but incurs losses when triggered
- **Strategy 3 is more active** (176 trades vs 158 trades)

---

## Strategy Differences

### Strategy 2: Progressive Buy (No Stop-Loss)

- **Buy Cadence:** 1, 1, 2, 2, 3, 4, 4 shares
- **Accumulation Range:** Up to 3.0% drop from first buy
- **Initial Position:** 1 share
- **Stop-Loss:** None
- **Exit:** Only when price > avg buy price

### Strategy 3: Progressive Buy with Stop-Loss

- **Buy Cadence:** 3, 3, 6 shares
- **Accumulation Range:** Up to 1.0% drop from first buy
- **Initial Position:** 3 shares
- **Stop-Loss:** 1.5% drop from first buy price
- **Exit:** Stop-loss OR when price > avg buy price

---

## Performance Comparison

### Capital & Performance

| Metric | Strategy 2 | Strategy 3 | Difference |
|--------|------------|------------|------------|
| Initial Capital | $10,000.00 | $10,000.00 | $0.00 |
| Final Portfolio Value | $10,906.50 | $10,712.49 | -$194.01 |
| Total P&L | $906.50 | $712.49 | -$194.01 |
| Return (%) | 9.06% | 7.12% | -1.94% |

**Analysis:** Strategy 2 outperforms Strategy 3 by $194.01 (1.94 percentage points). Strategy 2's ability to accumulate deeper (up to 3% drop) without stop-loss allows for better recovery and profit capture.

### Trading Activity

| Metric | Strategy 2 | Strategy 3 | Difference |
|--------|------------|------------|------------|
| Total Trades Executed | 158 | 176 | +18 |
| Average Trades per Day | 1.23 | 1.26 | +0.03 |
| Days with No Trades | 79 (38.2%) | 67 (32.4%) | -12 |

**Analysis:** Strategy 3 is more active with 18 additional trades (11.4% more). This is due to stop-loss triggers creating more trade opportunities, though some result in losses.

### Trade Quality

| Metric | Strategy 2 | Strategy 3 | Difference |
|--------|------------|------------|------------|
| Win Rate (%) | 100.0% | 88.6% | -11.4% |
| Winning Trades | 158 | 156 | -2 |
| Losing Trades | 0 | 20 | +20 |
| Average P&L per Trade | $5.74 | $4.05 | -$1.69 |
| Average Winning Trade | $5.74 | $10.04 | +$4.30 |
| Average Losing Trade | $0.00 | $-42.65 | -$42.65 |

**Analysis:** 
- Strategy 2 achieves perfect win rate (100%) vs Strategy 3's 88.6%
- Strategy 3's winning trades are larger ($10.04 vs $5.74) due to larger position sizes
- Strategy 3's losing trades average $-42.65 (all from stop-loss triggers)
- Strategy 2's average P&L per trade is higher ($5.74 vs $4.05)

### Stop-Loss Analysis

| Metric | Strategy 2 | Strategy 3 |
|--------|------------|------------|
| Stop-Loss Triggered | 0 | 20 (11.4%) |
| Average Stop-Loss Loss | N/A | $-42.65 |
| Back-to-Back Stop-Losses | N/A | 4 pairs (prevented) |

**Analysis:** Strategy 3's stop-loss mechanism triggered 20 times (11.4% of trades), limiting losses to an average of $42.65. The mechanism successfully prevents back-to-back stop-losses by skipping the buy signal that triggered the stop-loss.

### Cross-Day Trades

| Metric | Strategy 2 | Strategy 3 | Difference |
|--------|------------|------------|------------|
| Total Cross-Day Trades | 71 | 76 | +5 |
| Cross-Day Wins | 71 | 64 | -7 |
| Cross-Day Losses | 0 | 12 | +12 |
| Cross-Day Win Rate (%) | 100.0% | 84.2% | -15.8% |
| Cross-Day Total P&L | $763.21 | $452.16 | -$311.05 |
| Average P&L per Cross-Day Trade | $10.75 | $5.95 | -$4.80 |

**Analysis:** 
- Strategy 2 maintains perfect cross-day win rate (100%)
- Strategy 3's cross-day win rate is 84.2% (12 losses from stop-loss triggers)
- Strategy 2 generates significantly more P&L from cross-day trades ($763.21 vs $452.16)

### Position Holding

| Metric | Strategy 2 | Strategy 3 | Difference |
|--------|------------|------------|------------|
| Days with Zero Position at End | 108 (52.2%) | 115 (55.6%) | +7 |
| Days with Position at End | 99 (47.8%) | 92 (44.4%) | -7 |
| Days with Position Crossing to Next Day | 99 (47.8%) | 92 (44.4%) | -7 |

**Analysis:** Strategy 3 holds positions slightly less frequently due to stop-loss triggers closing positions earlier.

### Daily P&L Statistics

| Metric | Strategy 2 | Strategy 3 | Difference |
|--------|------------|------------|------------|
| Winning Days | 128 (61.8%) | 124 (59.9%) | -4 |
| Losing Days | 0 (0.0%) | 16 (7.7%) | +16 |
| Zero P&L Days | 79 (38.2%) | 67 (32.4%) | -12 |
| Mean Winning Day P&L | $7.08 | $12.10 | +$5.02 |
| Median Winning Day P&L | $1.98 | $6.39 | +$4.41 |
| Max Winning Day P&L | $160.43 | $140.60 | -$19.83 |

**Analysis:**
- Strategy 2 has zero losing days vs Strategy 3's 16 losing days (7.7%)
- Strategy 3's winning days are more profitable on average ($12.10 vs $7.08) due to larger positions
- Strategy 2's maximum winning day is higher ($160.43 vs $140.60)

### Risk Analysis

| Metric | Strategy 2 | Strategy 3 |
|--------|------------|------------|
| Big Losing Days (>$50) | 0 | 7 |
| Largest Single-Day Loss | N/A | $-83.09 |
| Stop-Loss Protection | None | Yes (1.5%) |

**Analysis:** Strategy 2 has zero big losing days due to price-filtered sell logic. Strategy 3 has 7 big losing days, all associated with stop-loss triggers from cross-day positions.

---

## Detailed Analysis

### Why Strategy 2 Outperforms

1. **No Stop-Loss Interference:** Strategy 2's price-filtered sell logic ensures positions are only closed when profitable, allowing for recovery from temporary dips.

2. **Deeper Accumulation:** Strategy 2 can accumulate up to 3% drop vs Strategy 3's 1% limit, providing better dollar-cost averaging opportunities.

3. **Perfect Win Rate:** Strategy 2's 100% win rate means every trade is profitable, maximizing capital efficiency.

4. **Better Cross-Day Performance:** Strategy 2's 100% cross-day win rate vs Strategy 3's 84.2% shows that overnight positions can be profitable without stop-loss protection.

### Why Strategy 3 Has Stop-Losses

1. **Tighter Accumulation Range:** Strategy 3 limits accumulation to 1% drop, so stop-loss at 1.5% triggers more frequently.

2. **Larger Initial Positions:** Strategy 3 starts with 3 shares vs 1 share, increasing exposure per trade.

3. **Stop-Loss Protection:** The 1.5% stop-loss is designed to limit losses, but in this backtest period, it triggered 20 times, reducing overall returns.

### Trade-Offs

**Strategy 2 Advantages:**
- Higher returns (9.06% vs 7.12%)
- Perfect win rate (100% vs 88.6%)
- Zero losing days
- Better cross-day performance
- No stop-loss interference

**Strategy 2 Disadvantages:**
- No stop-loss protection (potential for larger losses in adverse markets)
- Smaller initial positions (1 share vs 3 shares)
- Requires deeper price drops for accumulation

**Strategy 3 Advantages:**
- Stop-loss protection limits losses
- Larger initial positions (better capital utilization)
- Tighter accumulation range (less exposure)
- Prevents back-to-back stop-losses

**Strategy 3 Disadvantages:**
- Lower returns (7.12% vs 9.06%)
- Lower win rate (88.6% vs 100%)
- Has losing days (16 vs 0)
- Stop-loss can cut profitable trades short

---

## Market Condition Analysis

### Current Backtest Period (Feb-Dec 2025)

During this period, Strategy 2's approach of allowing deeper accumulation without stop-loss proved superior:
- Market conditions allowed for recovery from temporary dips
- Price-filtered sell logic prevented losses effectively
- Stop-loss protection was not necessary and actually reduced returns

### When Strategy 3 Might Be Better

Strategy 3's stop-loss protection would be more valuable in:
- **High volatility markets** with larger price swings
- **Trending down markets** where recovery is less likely
- **Risk-averse scenarios** where limiting losses is prioritized over maximizing returns
- **Larger position sizes** where stop-loss protection becomes critical

---

## Recommendations

### For Maximum Returns (Current Market Conditions)
**Choose Strategy 2:**
- Higher returns (9.06% vs 7.12%)
- Perfect win rate
- Zero losing days
- Better capital efficiency

### For Risk Management (Volatile/Down Markets)
**Choose Strategy 3:**
- Stop-loss protection limits losses
- Controlled risk exposure
- Prevents catastrophic losses
- Suitable for risk-averse investors

### Hybrid Approach
Consider a **dynamic strategy** that:
- Uses Strategy 2 in stable/upward trending markets
- Switches to Strategy 3 in volatile/downward trending markets
- Adjusts stop-loss threshold based on market volatility
- Monitors stop-loss trigger frequency to optimize risk/reward

---

## Conclusions

1. **Strategy 2 is superior** for the current backtest period, generating 9.06% return with perfect win rate and zero losing days.

2. **Strategy 3 provides risk protection** through stop-loss mechanism, but at the cost of lower returns (7.12%) and 20 losing trades.

3. **Market conditions matter:** Strategy 2's approach works well when markets allow recovery from dips. Strategy 3's stop-loss protection would be more valuable in adverse market conditions.

4. **Trade-off analysis:** Strategy 2 prioritizes returns and win rate, while Strategy 3 prioritizes risk management and loss limitation.

5. **Optimal strategy selection** depends on:
   - Market conditions (volatility, trend direction)
   - Risk tolerance
   - Capital size
   - Investment objectives

---

## Technical Details

- **Data Period:** February 14, 2025 - December 11, 2025
- **Total Trading Days:** 207
- **Comparison Script:** `compare_strategy2_vs_strategy3.py`
- **Strategy 2 Report:** `strategy2/STRATEGY2_LOW_RISK_ACCUMULATION_REPORT.md`
- **Strategy 3 Report:** `strategy3/STRATEGY3_LOW_RISK_ACCUMULATION_REPORT.md`

---

*Comparison report generated on: December 2025*

