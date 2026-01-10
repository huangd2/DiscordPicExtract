# Consecutive Higher Sells Analysis - Strategy 4 Development

## Overview

This analysis examines the probability of seeing consecutive sell signals at higher prices than an executed buy, with the goal of preserving upside gain by waiting for better exit opportunities.

## Pattern Definition

**Pattern Analyzed:** 
- Buy (executed) → Immediate Next Signal is Sell (higher than buy) → Another Sell (higher than buy, **verified no signals < buy_price in between**)

## Key Findings

### 1. First Higher Sell (Immediate Next Signal)

- **21.67%** of executed buys (267 out of 1,232) have the immediate next signal as a Sell that's higher than the buy price
- Average % increase: **0.31%**
- Median % increase: **0.20%**
- Range: 0.00% to 2.26%

### 2. Second Higher Sell (Conditional Probability)

**Given that the immediate next signal is a Sell higher than the buy price:**

- **74.91% chance** (200 out of 267 cases) of seeing another Sell that's also higher than the buy price
- **Verified:** No signals in between have a price lower than the buy price
- Average % increase from buy to second sell: **0.47%**
- Median % increase: **0.33%**

**Breakdown:**
- **200 cases (74.91%)**: Found second higher sell with NO low-price signals between first and second sell
- **66 cases (24.72%)**: Found a low-price signal (< buy_price) before any second sell, blocking the pattern
- **1 case (0.37%)**: No second sell found and no low-price signal encountered (likely end of data)

### 3. Second Sell vs First Sell Price Comparison

Out of the **200 cases** with a second higher sell:

- **158 cases (79.00%)**: Second sell price > First sell price
- **2 cases (1.00%)**: Second sell price = First sell price  
- **40 cases (20.00%)**: Second sell price < First sell price

**Key Insight:** When a second higher sell appears (with no low-price signals between), it tends to be higher than the first sell about **4 out of 5 times**.

### 4. Third Higher Sell (Extended Pattern)

Out of the **200 cases** with a second higher sell:

- **175 cases (87.50%)** have a third sell that's also higher than the buy price
- **Verified:** No signals between the second and third sell have a price lower than the buy price

**Third Sell Price Analysis:**
- **144 out of 175 (82.29%)**: Third sell price > First sell price
- **122 out of 175 (69.71%)**: Third sell price > Second sell price
- Average % increase from buy to third sell: **0.57%**
- Average % increase from second sell to third sell: **0.08%**

## Summary Statistics

| Metric | Count | Percentage of Total | Percentage of 1st Higher Sell |
|--------|-------|---------------------|-------------------------------|
| Total Buy Signals | 1,232 | 100.00% | - |
| Has 1st Higher Sell | 267 | 21.67% | 100.0% |
| Has 2nd Higher Sell (no low signals) | 200 | 16.23% | 74.91% |
| Low Price Signal Found (blocked 2nd sell) | 66 | 5.36% | 24.72% |

## Strategy Implications

### For Strategy 4 Development:

1. **Entry Signal:** When a buy is executed and the immediate next signal is a Sell at a higher price, this creates an opportunity.

2. **Exit Strategy - First Sell:**
   - **21.67%** of buys will have an immediate higher sell opportunity
   - Average gain: **0.31%**

3. **Exit Strategy - Second Sell (Recommended):**
   - **74.91%** conditional probability of seeing a second higher sell
   - **79%** chance the second sell will be at a higher price than the first sell
   - Average gain: **0.47%** (vs 0.31% for first sell)
   - **Risk:** 24.72% chance a low-price signal appears before second sell

4. **Exit Strategy - Third Sell (Aggressive):**
   - **87.50%** conditional probability (from second sell cases)
   - **69.71%** chance the third sell will be higher than the second sell
   - Average gain: **0.57%** (vs 0.47% for second sell)
   - **Risk:** 12.50% chance a low-price signal appears before third sell

### Risk Management:

- **Key Risk:** Low-price signals (< buy_price) appearing between sells
- **Mitigation:** Monitor all signals between sells; if any signal has price < buy_price, consider exiting at the current sell rather than waiting for the next one
- **Success Rate:** The pattern shows strong continuation (87.5% → 74.9% → 87.5% probabilities)

## Data Files

- **Detailed Results:** `consecutive_higher_sells_analysis.csv`
- **Analysis Script:** `analyze_consecutive_higher_sells.py`
- **Third Sell Analysis:** `analyze_third_sell.py`

## Methodology

1. Load all signals from `combined_data.csv`
2. Sort signals chronologically by timestamp
3. For each executed buy signal:
   - Check if immediate next signal is a Sell higher than buy price
   - If yes, look for second Sell higher than buy price
   - Verify no signals between first and second sell have price < buy_price
   - Continue pattern for third sell analysis
4. Calculate conditional probabilities and statistics

## Conclusion

The analysis demonstrates a strong pattern of consecutive higher sells when:
- The immediate next signal after a buy is a higher sell
- No low-price signals appear between consecutive sells

**Recommended Strategy 4 Approach:**
- Wait for the second higher sell when the first higher sell appears immediately after buy
- This preserves **74.91%** of upside opportunities with **79%** chance of better pricing
- Consider third sell only if no low-price signals appear between second and third sell

---

*Analysis Date: Generated from consecutive_higher_sells_analysis.csv*
*Total Signals Analyzed: 2,361 (1,232 buys, 1,129 sells)*

