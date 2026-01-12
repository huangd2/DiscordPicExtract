# Strategy 4 vs Strategy 2: Comprehensive Comparison Report

## Executive Summary

This report compares **Strategy 4: Low Risk Accumulation Strategy - Progressive Exit with Trailing Stop-Loss** with **Strategy 2: Low Risk Accumulation Strategy - Progressive Buy** based on SPX (S&P 500) signals from February 14, 2025 to December 11, 2025.

**Key Findings:**
- **Strategy 2 outperforms** with 9.06% return vs 8.74% return (-0.32%)
- **Strategy 2 has perfect win rate** (100% vs 88.0%)
- **Strategy 4 provides stop-loss protection** but incurs losses when triggered
- **Strategy 4 has progressive exits** allowing profit-taking at multiple stages

---

## Strategy Differences

### Strategy 2: Progressive Buy (No Stop-Loss)

- **Buy Cadence:** 1, 1, 2, 2, 3, 4, 4 shares
- **Accumulation Range:** Up to 3.0% drop from first buy
- **Initial Position:** 1 share
- **Stop-Loss:** None
- **Exit:** Only when price > avg buy price (sell all shares)

### Strategy 4: Progressive Exit with Trailing Stop-Loss

- **Buy Cadence:** 3, 3, 6 shares
- **Accumulation Range:** Up to 1.0% drop from first buy
- **Initial Position:** 3 shares
- **Stop-Loss:** 1.5% drop from average buy price (before sells), first_sell_price (after 2nd sell)
- **Exit:** Progressive partial exits (50%, 25%, 25%) with trailing stop-loss

---

## Performance Comparison

### Capital & Performance

| Metric | Strategy 2 | Strategy 4 | Difference |
|--------|------------|------------|------------|
| Initial Capital | $10,000.00 | $10,000.00 | $0.00 |
| Final Portfolio Value | $10,906.50 | $10,874.28 | -$32.22 |
| Total P&L | $906.50 | $874.28 | -$32.22 |
| Return (%) | 9.06% | 8.74% | -0.32% |

**Analysis:** Strategy 2 outperforms Strategy 4 by $32.22 (0.32 percentage points). Strategy 2's ability to accumulate deeper (up to 3% drop) without stop-loss allows for better recovery and profit capture.

### Trading Activity

| Metric | Strategy 2 | Strategy 4 | Difference |
|--------|------------|------------|------------|
| Total Trades Executed | 158 | 117 | -41 |
| Average Trades per Day | 1.23 | 2.52 | +1.29 |
| Days with No Trades | 79 (38.2%) | 66 (31.9%) | -13 |

**Analysis:** Strategy 4 executes fewer completed trades (117 vs 158) but has higher average trades per day (2.52 vs 1.23) due to partial exits creating more trade actions per position.

### Trade Quality

| Metric | Strategy 2 | Strategy 4 | Difference |
|--------|------------|------------|------------|
| Win Rate (%) | 100.0% | 88.0% | -12.0% |
| Winning Trades | 158 | 103 | -55 |
| Losing Trades | 0 | 14 | +14 |
| Average P&L per Trade | $5.74 | $7.47 | +$1.73 |
| Average Winning Trade | $5.74 | $4.92 | -$0.82 |
| Average Losing Trade | $0.00 | -$54.46 | -$54.46 |

**Analysis:** 
- Strategy 2 achieves perfect win rate (100%) vs Strategy 4's 88.0%
- Strategy 4's average P&L per trade is higher ($7.47 vs $5.74) despite lower win rate
- Strategy 4's winning trades are smaller ($4.92 vs $5.74) due to partial exits
- Strategy 4 has 14 losing trades (all from stop-loss triggers)

### Stop-Loss Analysis

| Metric | Strategy 2 | Strategy 4 |
|--------|------------|------------|
| Stop-Loss Triggered | 0 | 34 (29.1%) |
| Average Stop-Loss Loss | N/A | -$20.80 |
| Stop-Loss Protection | None | Yes (1.5% from avg buy, trailing after 2nd sell) |

**Analysis:** Strategy 4's stop-loss mechanism triggered 34 times (29.1% of trades), limiting losses to an average of $20.80. Strategy 2 has no stop-loss protection but achieves perfect win rate through price-filtered sell logic.

### Cross-Day Trades

| Metric | Strategy 2 | Strategy 4 | Difference |
|--------|------------|------------|------------|
| Total Cross-Day Trades | 71 | 76 | +5 |
| Cross-Day Wins | 71 | 65 | -6 |
| Cross-Day Losses | 0 | 11 | +11 |
| Cross-Day Win Rate (%) | 100.0% | 85.5% | -14.5% |
| Cross-Day Total P&L | $763.21 | -$268.13 | -$1,031.34 |
| Average P&L per Cross-Day Trade | $10.75 | -$3.53 | -$14.28 |

**Analysis:** 
- Strategy 2 maintains perfect cross-day win rate (100%) vs Strategy 4's 85.5%
- Strategy 2 generates significantly more P&L from cross-day trades ($763.21 vs -$268.13)
- Strategy 4's cross-day trades are negative overall, indicating challenges with partial exits in overnight positions

### Position Holding

| Metric | Strategy 2 | Strategy 4 | Difference |
|--------|------------|------------|------------|
| Days with Zero Position at End | 108 (52.2%) | 87 (42.0%) | -21 |
| Days with Position at End | 99 (47.8%) | 120 (58.0%) | +21 |
| Days with Position Crossing to Next Day | 99 (47.8%) | 118 (57.0%) | +19 |

**Analysis:** Strategy 4 holds positions longer (58.0% vs 47.8% days with position at end) due to the partial exit mechanism allowing positions to remain open longer.

### Daily P&L Statistics

| Metric | Strategy 2 | Strategy 4 | Difference |
|--------|------------|------------|------------|
| Winning Days | 128 (61.8%) | 128 (61.8%) | 0 |
| Losing Days | 0 (0.0%) | 13 (6.3%) | +13 |
| Zero P&L Days | 79 (38.2%) | 66 (31.9%) | -13 |
| Mean Winning Day P&L | $7.08 | $12.18 | +$5.10 |
| Median Winning Day P&L | $1.98 | $6.35 | +$4.37 |
| Max Winning Day P&L | $160.43 | $162.64 | +$2.21 |

**Analysis:**
- Strategy 2 has zero losing days vs Strategy 4's 13 losing days (6.3%)
- Strategy 4's winning days are more profitable on average ($12.18 vs $7.08) due to larger positions
- Strategy 4's maximum winning day is slightly higher ($162.64 vs $160.43)

### Risk Analysis

| Metric | Strategy 2 | Strategy 4 |
|--------|------------|------------|
| Big Losing Days (>$50) | 0 | 6 |
| Largest Single-Day Loss | N/A | -$122.06 |
| Stop-Loss Protection | None | Yes (1.5% from avg buy, trailing after 2nd sell) |

**Analysis:** Strategy 2 has zero big losing days due to price-filtered sell logic. Strategy 4 has 6 big losing days, all associated with stop-loss triggers from cross-day positions.

---

## Detailed Analysis

### Why Strategy 2 Outperforms

1. **Perfect Win Rate:** Strategy 2's price-filtered sell logic ensures positions are only closed when profitable, achieving 100% win rate.

2. **Deeper Accumulation:** Strategy 2 can accumulate up to 3% drop vs Strategy 4's 1% limit, providing better dollar-cost averaging opportunities.

3. **No Stop-Loss Interference:** Strategy 2's approach allows for recovery from temporary dips without stop-loss cutting trades short.

4. **Better Cross-Day Performance:** Strategy 2's 100% cross-day win rate vs Strategy 4's 85.5% shows that overnight positions can be profitable without stop-loss protection.

### Why Strategy 4 Has Stop-Losses

1. **Tighter Accumulation Range:** Strategy 4 limits accumulation to 1% drop, so stop-loss at 1.5% triggers more frequently.

2. **Larger Initial Positions:** Strategy 4 starts with 3 shares vs 1 share, increasing exposure per trade.

3. **Progressive Exit Mechanism:** Partial exits create more opportunities for stop-loss triggers as positions are held longer.

4. **Trailing Stop-Loss:** After partial exits, the trailing stop-loss can trigger more frequently.

### Trade-Offs

**Strategy 2 Advantages:**
- Higher returns (9.06% vs 8.74%)
- Perfect win rate (100% vs 88.0%)
- Zero losing days
- Better cross-day performance
- No stop-loss interference
- Deeper accumulation range

**Strategy 2 Disadvantages:**
- No stop-loss protection (potential for larger losses in adverse markets)
- Smaller initial positions (1 share vs 3 shares)
- Requires deeper price drops for accumulation

**Strategy 4 Advantages:**
- Stop-loss protection limits losses
- Progressive profit-taking
- Trailing stop-loss protection
- Larger initial positions (better capital utilization)
- Average buy price stop-loss provides dynamic risk management

**Strategy 4 Disadvantages:**
- Lower returns (8.74% vs 9.06%)
- Lower win rate (88.0% vs 100%)
- Has losing days (13 vs 0)
- Negative cross-day P&L (-$268.13 vs $763.21)
- Stop-loss can cut profitable trades short

---

## Market Condition Analysis

### Current Backtest Period (Feb-Dec 2025)

During this period, Strategy 2's approach of allowing deeper accumulation without stop-loss proved superior:
- Market conditions allowed for recovery from temporary dips
- Price-filtered sell logic prevented losses effectively
- Stop-loss protection was not necessary and actually reduced returns
- Deeper accumulation range (3% vs 1%) provided better opportunities

### When Strategy 4 Might Be Better

Strategy 4's stop-loss protection and progressive exits would be more valuable in:
- **High volatility markets** with larger price swings
- **Trending down markets** where recovery is less likely
- **Risk-averse scenarios** where limiting losses is prioritized over maximizing returns
- **Larger position sizes** where stop-loss protection becomes critical

---

## Recommendations

### For Maximum Returns (Current Market Conditions)
**Choose Strategy 2:**
- Higher returns (9.06% vs 8.74%)
- Perfect win rate
- Zero losing days
- Better cross-day performance
- Deeper accumulation range

### For Risk Management (Volatile/Down Markets)
**Choose Strategy 4:**
- Stop-loss protection limits losses
- Progressive profit-taking
- Trailing stop-loss protection
- Controlled risk exposure
- Suitable for risk-averse investors

### Hybrid Approach
Consider a **dynamic strategy** that:
- Uses Strategy 2 in stable/upward trending markets
- Switches to Strategy 4 in volatile/downward trending markets
- Adjusts accumulation range and stop-loss threshold based on market volatility
- Monitors stop-loss trigger frequency to optimize risk/reward

---

## Conclusions

1. **Strategy 2 is superior** for the current backtest period, generating 9.06% return with perfect win rate and zero losing days, outperforming Strategy 4 by 0.32 percentage points.

2. **Strategy 4 provides risk protection** through stop-loss mechanism and progressive exits, but at the cost of lower returns (8.74%) and 14 losing trades.

3. **Market conditions matter:** Strategy 2's approach works well when markets allow recovery from dips. Strategy 4's stop-loss protection would be more valuable in adverse market conditions.

4. **Trade-off analysis:** Strategy 2 prioritizes returns and win rate, while Strategy 4 prioritizes risk management and progressive profit-taking.

5. **Optimal strategy selection** depends on:
   - Market conditions (volatility, trend direction)
   - Risk tolerance
   - Preference for stop-loss protection
   - Capital size
   - Investment objectives

---

## Technical Details

- **Data Period:** February 14, 2025 - December 11, 2025
- **Total Trading Days:** 207
- **Comparison Script:** Manual comparison based on statistics CSV files
- **Strategy 2 Report:** `strategy2/STRATEGY2_LOW_RISK_ACCUMULATION_REPORT.md`
- **Strategy 4 Report:** `strategy4/STRATEGY4_PROGRESSIVE_EXIT_REPORT.md`

---

*Comparison report generated on: December 2025*

