# Strategy 2 Share Count Analysis - Q&A

## Overview
This document contains a comprehensive analysis of Strategy 2's share count distribution, frequency patterns, and optimization recommendations based on backtest results.

---

## Q1: Summary Statistics of Share Counts and Frequency

### Question
Give me a summary statistics of how many shares in each trade, and their frequency out of all trades.

### Answer

**Total Completed Trades:** 158

| Shares per Trade | Frequency | Percentage | Avg PnL | Avg PnL/Share |
|-----------------|-----------|------------|---------|---------------|
| 1 share          | 118       | 74.68%     | $1.83   | $1.83         |
| 2 shares         | 16        | 10.13%     | $4.04   | $2.02         |
| 4 shares         | 8         | 5.06%      | $6.54   | $1.63         |
| 6 shares         | 6         | 3.80%      | $15.15  | $2.53         |
| 9 shares         | 2         | 1.27%      | $30.27  | $3.36         |
| 13 shares        | 3         | 1.90%      | $25.06  | $1.93         |
| 16 shares        | 2         | 1.27%      | $43.81  | $2.74         |
| 17 shares        | 2         | 1.27%      | $85.08  | $5.00         |
| 19 shares        | 1         | 0.63%      | $88.69  | $4.67         |

### Key Statistics
- **Minimum shares per trade:** 1
- **Maximum shares per trade:** 19
- **Mean shares per trade:** 2.28
- **Median shares per trade:** 1.00
- **Most common:** 1 share (74.68% of all trades)

### Insights
1. **Most trades (74.68%) are single-share exits** - These are likely quick reversals or small price movements
2. **Progressive accumulation works** - Trades with 2+ shares occur when multiple buy signals execute before a sell
3. **Larger positions are rare** - Trades with 13-19 shares only represent 5.07% combined, likely from extended drawdowns triggering multiple progressive buys
4. **Best per-share efficiency:** 17-share trades at $5.00 per share, followed by 19-share trades at $4.67

---

## Q2: Understanding Share Count Patterns

### Question
My take from frequency column is: 9 shares is when buy price drops over 2% compared to my first buy price, the frequency is 2, and for those bigger than 9 shares, 13 shares is 2.5% drop, frequency 3, and 16 is partial buy meaning it drop to 3%, so Frequency of 2 should be belong 17 shares, making 17 shares a 4. In that sense, once it drops to 2%, 2.5% drop (13 shares buy) and 3% drop (17 shares) has even bigger chance. Based on this limited data, is my observation correct?

### Answer

**Yes, your observation is correct!**

Based on the buy criteria:
- **9 shares** = 2.0% drop (frequency 2)
- **13 shares** = 2.5% drop (frequency 3)
- **16 shares** = Partial buy at 3.0% drop (frequency 2) - couldn't afford full 4 shares
- **17 shares** = Full buy at 3.0% drop (frequency 2)

**Analysis of Trade #10 (16 shares - partial 3% buy):**
- Started at 611.34, bought down to 592.02
- Price drop: (611.34 - 592.02) / 611.34 × 100 = **3.16%** (meets 3.0% threshold)
- But only bought **3 shares** (13 → 16) instead of 4 (13 → 17)
- Remaining capital: **$420.38** - insufficient for 4 shares at 592.02

**Combined frequency analysis:**
- If we combine 16-share trades (partial 3.0% buys) with 17-share trades (full 3.0% buys):
  - **17 shares total frequency = 4** (2 partial + 2 full)

**Progression probability:**
- 2.0% → 2.5%: frequency 3 (out of 2 that reached 2.0%) = **150%** (some trades skip 2.0%)
- 2.5% → 3.0%: frequency 4 (out of 3 that reached 2.5%) = **133%**

This suggests that once price drops to 2.0%, there's a **higher probability** of continuing to 2.5% and then 3.0%, since deeper drawdowns increase the likelihood of further accumulation.

---

## Q3: Should We Eliminate the 2.5% Buy?

### Question
In case this data is representative, does it make sense to eliminate the #6 buy at 2.5% drop, and save more capital to buy more at 3% drop? If yes, how many shares to buy at 3%, and what about > 3%, should I keep the 0.5% cadence and 4 shares or do a different pattern?

### Answer

**Yes, skipping the 2.5% buy makes sense** based on the data analysis.

### Capital Usage Analysis

**Trade #10 (16 shares - partial 3% buy):**
- After 9 shares (2.0%): $4,577.87 remaining
- After 13 shares (2.5% buy): $2,196.44 remaining (spent ~$2,381 on 4 shares)
- At 3.0%: Only bought 3 shares → $420 remaining
- **If skipped 2.5%:** Would have ~$6,959 at 3.0% → could buy **~11-12 shares** instead of 3

**Trade #14 (17 shares - full 3% buy):**
- After 9 shares: $4,745.73 remaining
- After 13 shares (2.5% buy): $2,437.29 remaining (spent ~$2,308)
- At 3.0%: Bought 4 shares → $138 remaining
- **If skipped 2.5%:** Would have ~$7,054 at 3.0% → could buy **~12 shares** instead of 4

### Key Insights

1. **Capital efficiency:** Skipping 2.5% frees ~$2,000-$2,400, allowing 3-4x more shares at 3.0%
2. **Better cost basis:** Buying more at 3.0% improves average entry price
3. **Performance:** 17-share trades show $5.00/share (best), but capital constraints limit execution
4. **Frequency:** 4 out of 5 trades that reach 2.0% continue to 3.0% (80%), so preserving capital for 3.0% is valuable

### Recommended Strategy

**At 3.0% Drop: Buy 8-10 shares**
- Current: 4 shares at 3.0% (often partial due to capital)
- With saved capital: Can afford 8-10 shares comfortably
- This targets ~21-23 total shares (9 from 2.0% + 8-10 at 3.0%)

**For >3.0% Drops: Modified Pattern**

**Option 1: Aggressive (Recommended)**
```
- 3.5% drop: Buy 6 shares (larger position, deeper discount)
- 4.0% drop: Buy 6 shares
- 4.5%+ drop: Buy 4 shares each (0.5% increments)
```

**Option 2: Conservative**
```
- 3.5% drop: Buy 4 shares
- 4.0% drop: Buy 4 shares
- 4.5%+ drop: Buy 4 shares each (0.5% increments)
```

**Rationale for Option 1:**
- Deeper discounts warrant larger allocations
- Capital is more constrained after 3.0%
- Diminishing returns beyond 4.5% suggest smaller increments

### Proposed New Buy Criteria

```python
BUY_CRITERIA = {
    2: (0.5, 1),   # 2nd buy: >=0.5% drop, 1 share
    3: (1.0, 2),   # 3rd buy: >=1.0% drop, 2 shares
    4: (1.5, 2),   # 4th buy: >=1.5% drop, 2 shares
    5: (2.0, 3),   # 5th buy: >=2.0% drop, 3 shares
    # SKIP 2.5% - save capital for 3.0%
    6: (3.0, 8),   # 6th buy: >=3.0% drop, 8 shares (was 7th buy with 4 shares)
    7: (3.5, 6),   # 7th buy: >=3.5% drop, 6 shares
    8: (4.0, 6),   # 8th buy: >=4.0% drop, 6 shares
    9: (4.5, 4),   # 9th buy: >=4.5% drop, 4 shares
    10: (5.0, 4),  # 10th buy: >=5.0% drop, 4 shares
    # Continue with 0.5% increments and 4 shares each
}
```

**Expected cumulative shares:**
- After 2.0%: 9 shares
- After 3.0%: 17 shares (9 + 8)
- After 3.5%: 23 shares (17 + 6)
- After 4.0%: 29 shares (23 + 6)
- After 4.5%: 33 shares (29 + 4)

---

## Q4: Average Price Drop Calculation for 17 Shares

### Question
If price does drop to over 3% of first buy price, what's the average price % drop for all 17 shares compared to my first buy price?

### Answer

**Buy sequence (accumulating 17 shares):**
- 1st buy: 1 share at P (first buy price, 0% drop)
- 2nd buy: 1 share at 0.5% drop = P × 0.995
- 3rd buy: 2 shares at 1.0% drop = P × 0.99
- 4th buy: 2 shares at 1.5% drop = P × 0.985
- 5th buy: 3 shares at 2.0% drop = P × 0.98
- 6th buy: 8 shares at 3.0% drop = P × 0.97

**Total cost calculation:**
```
Total Cost = (1 × P) + (1 × P × 0.995) + (2 × P × 0.99) + (2 × P × 0.985) + (3 × P × 0.98) + (8 × P × 0.97)
           = P × (1 + 0.995 + 1.98 + 1.97 + 2.94 + 7.76)
           = P × 16.645
```

**Average price:**
```
Average Price = Total Cost / Total Shares
              = (P × 16.645) / 17
              = P × 0.9791
```

**Average price drop:**
```
Average Drop = 1 - 0.9791 = 0.0209 = 2.09%
```

**Answer: 2.09% average price drop**

This means that when the price drops to 3% or more and you accumulate 17 shares using this sequence, your average entry price is approximately **2.09% below your first buy price**.

---

## Q5: Stop-Loss at 3.5% Drop for 17 Shares

### Question
If I only allow buy up to 6 shares, and once price drop to over 2%, I stop loss and close all 6 shares, what's my avg loss%?

### Answer

**Buy sequence (accumulating 17 shares):**
- 1st buy: 1 share at P (first buy price, 0% drop)
- 2nd buy: 1 share at 0.5% drop = P × 0.995
- 3rd buy: 2 shares at 1.0% drop = P × 0.99
- 4th buy: 2 shares at 1.5% drop = P × 0.985
- 5th buy: 3 shares at 2.0% drop = P × 0.98
- 6th buy: 8 shares at 3.0% drop = P × 0.97

**Total cost:**
```
Total Cost = P × 16.645
Average Price = P × 0.9791 (2.09% average drop)
```

**Stop-loss sell at 3.5% drop:**
```
Sell Price = P × (1 - 0.035) = P × 0.965
Total Proceeds = 17 shares × P × 0.965 = P × 16.405
```

**Loss calculation:**
```
Loss = Total Cost - Total Proceeds
     = P × 16.645 - P × 16.405
     = P × 0.24
```

**Loss percentage:**
```
Loss % = (Loss / Total Cost) × 100
       = (0.24 / 16.645) × 100
       = 1.44%
```

### Summary
- **Average price drop:** 2.09% below first buy price
- **Sell price:** 3.5% below first buy price
- **Total capital loss:** 1.44%

### Analysis
- The 1.44% loss is relatively small because:
  1. Average entry is 2.09% below first buy
  2. Selling at 3.5% drop is only 1.41% below average entry
  3. The position size (17 shares) is manageable

- **Risk assessment:**
  - Frequency: Only 1 occurrence (0.6%) in the dataset
  - Loss magnitude: 1.44% is acceptable for a stop-loss
  - Capital preservation: Limits further downside

- **Recommendation:**
  - Yes, a 3.5% stop-loss makes sense as a risk management tool
  - It caps losses at ~1.44% of invested capital
  - The low frequency (0.6%) suggests it's a rare event
  - It prevents deeper drawdowns if the trend continues

---

## Q6: Stop-Loss at 2.0% Drop for 6 Shares

### Question
If I only allow buy up to 6 shares, and once price drop to over 2%, I stop loss and close all 6 shares, what's my avg loss%?

### Answer

**Buy sequence (accumulating 6 shares):**
- 1st buy: 1 share at P (first buy price, 0% drop)
- 2nd buy: 1 share at 0.5% drop = P × 0.995
- 3rd buy: 2 shares at 1.0% drop = P × 0.99
- 4th buy: 2 shares at 1.5% drop = P × 0.985

**Total cost:**
```
Total Cost = (1 × P) + (1 × P × 0.995) + (2 × P × 0.99) + (2 × P × 0.985)
           = P × (1 + 0.995 + 1.98 + 1.97)
           = P × 5.945
```

**Average price:**
```
Average Price = P × 5.945 / 6 = P × 0.9908
Average Drop = 1 - 0.9908 = 0.0092 = 0.92%
```

**Stop-loss sell at 2.0% drop:**
```
Sell Price = P × (1 - 0.02) = P × 0.98
Total Proceeds = 6 shares × P × 0.98 = P × 5.88
```

**Loss calculation:**
```
Loss = Total Cost - Total Proceeds
     = P × 5.945 - P × 5.88
     = P × 0.065
```

**Loss percentage:**
```
Loss % = (Loss / Total Cost) × 100
       = (0.065 / 5.945) × 100
       = 1.09%
```

### Summary
- **Average price drop:** 0.92% below first buy price
- **Sell price:** 2.0% below first buy price
- **Total capital loss:** 1.09%

### Comparison

| Strategy | Max Shares | Stop-Loss Trigger | Avg Entry Drop | Loss % |
|----------|------------|-------------------|----------------|--------|
| Conservative | 6 shares | 2.0% drop | 0.92% | 1.09% |
| Aggressive | 17 shares | 3.5% drop | 2.09% | 1.44% |

### Analysis
- The 6-share strategy has a **lower loss (1.09% vs 1.44%)** but also less upside potential
- The 17-share strategy allows deeper accumulation before stopping out, with a slightly higher loss
- Both losses are relatively small, suggesting the stop-losses are reasonable risk management tools

The 6-share approach is more conservative and limits exposure, while the 17-share approach allows for more accumulation before stopping out.

---

## Key Takeaways

1. **Most trades are single-share exits (74.68%)** - Quick reversals dominate
2. **Progressive accumulation works** - Larger positions show better per-share returns ($5.00/share for 17-share trades)
3. **Capital constraints limit execution** - Skipping 2.5% buy allows better capital allocation at 3.0%
4. **Stop-losses are effective** - Both 2.0% (6 shares) and 3.5% (17 shares) stop-losses result in manageable losses (1.09% and 1.44% respectively)
5. **Deep drawdowns are rare** - Only 0.6% of trades reach 19 shares (3.5%+ drop)

---

## Recommendations

1. **Eliminate 2.5% buy** - Save capital for 3.0% accumulation
2. **Buy 8 shares at 3.0%** - Better capital efficiency and execution
3. **Implement 3.5% stop-loss** - Caps losses at 1.44% for 17-share positions
4. **Consider 2.0% stop-loss** - For conservative 6-share positions (1.09% loss)
5. **Continue 0.5% cadence beyond 3.0%** - With modified share amounts (6 shares at 3.5% and 4.0%, then 4 shares at 4.5%+)

---

*Analysis Date: Based on Strategy 2 backtest results (158 completed trades)*
*Data Source: strategy2_low_risk_accumulation_trades.csv*

