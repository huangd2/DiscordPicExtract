# Buy Signal Confidence Analysis Report

## Executive Summary

This report analyzes buy signals and their profitability across three distinct patterns:
1. **Buy → Sell** (immediate sell signal)
2. **Buy → Buy → Sell** (one buy signal before sell)
3. **Buy → Buy → Buy → Sell** (two buy signals before sell)

**Key Finding:** Out of 1,232 total buy signals, **515 cases (41.8%)** result in profitable sell opportunities within the next 3 signals, where the sell price is higher than the initial buy price.

---

## Table of Contents

1. [Overall Statistics](#overall-statistics)
2. [Pattern 1: Buy → Sell Analysis](#pattern-1-buy--sell-analysis)
3. [Pattern 2: Buy → Buy → Sell Analysis](#pattern-2-buy--buy--sell-analysis)
4. [Pattern 3: Buy → Buy → Buy → Sell Analysis](#pattern-3-buy--buy--buy--sell-analysis)
5. [Profit Duration Analysis](#profit-duration-analysis)
6. [Duration Distribution](#duration-distribution)
7. [Conclusions](#conclusions)

---

## Overall Statistics

### Total Buy Signals Analyzed
- **Total Buy Signals:** 1,232
- **Total Sell Signals:** 1,129
- **Total Signals:** 2,361

### Profitability Summary
- **Buy → Sell (Higher):** 267 cases (21.67%)
- **Buy → Buy → Sell (Higher):** 147 cases (11.93%)
- **Buy → Buy → Buy → Sell (Higher):** 101 cases (8.20%)
- **Total Profitable Cases:** 515 cases (41.8%)

---

## Pattern 1: Buy → Sell Analysis

### Pattern Occurrence
- **Buy signals with immediate next sell signal:** 297 (24.11%)
- **Buy signals with sell at higher price:** 267 (21.67%)
- **Success rate (when immediate sell exists):** 89.90%

### Profit Statistics
- **Average % increase:** 0.31%
- **Median % increase:** 0.20%
- **Min % increase:** 0.0016%
- **Max % increase:** 2.26%
- **Std Dev:** 0.33%

### Detailed Statistics
| Metric | Value |
|--------|-------|
| Mean % | 0.3129% |
| Median % | 0.1991% |
| Min % | 0.0016% |
| Max % | 2.2626% |
| Std Dev % | 0.3309% |
| 25th Percentile % | 0.0884% |
| 75th Percentile % | 0.4097% |

---

## Pattern 2: Buy → Buy → Sell Analysis

### Pattern Occurrence
- **Buy signals with Buy→Buy→Sell pattern:** 176 (14.29%)
- **Buy signals with sell at higher price:** 147 (11.93%)
- **Success rate (when pattern exists):** 83.52%

### Second Buy vs First Buy
- **Average % change:** 0.0080% (essentially flat)
- **Median % change:** -0.0197% (slightly lower)
- **Range:** -2.98% to +3.39%
- **Second buy higher than first:** 78 (44.32%)
- **Second buy lower than first:** 97 (55.11%)
- **Second buy same as first:** 1 (0.57%)

### Profit Statistics (Sell vs First Buy)
- **Average % increase:** 0.46%
- **Median % increase:** 0.30%
- **Min % increase:** 0.0024%
- **Max % increase:** 3.73%
- **Std Dev:** 0.50%

### Detailed Statistics
| Metric | Value |
|--------|-------|
| Mean % | 0.4621% |
| Median % | 0.2959% |
| Min % | 0.0024% |
| Max % | 3.7268% |
| Std Dev % | 0.5019% |
| 25th Percentile % | 0.1323% |
| 75th Percentile % | 0.5759% |

### Second Buy Analysis (Profitable Patterns Only)
- **Average % change:** 0.08%
- **Median % change:** 0.00%

---

## Pattern 3: Buy → Buy → Buy → Sell Analysis

### Pattern Occurrence
- **Buy signals with Buy→Buy→Buy→Sell pattern:** 130 (10.55%)
- **Buy signals with sell at higher price:** 101 (7.77%)
- **Success rate (when pattern exists):** 77.69%

### Second Buy vs First Buy
- **Average % change:** -0.0588% (slightly lower)
- **Median % change:** -0.0263% (slightly lower)
- **Range:** -0.90% to +0.76%
- **Second buy higher than first:** 54 (41.54%)
- **Second buy lower than first:** 75 (57.69%)
- **Second buy same as first:** 1 (0.77%)

### Third Buy vs First Buy
- **Average % change:** -0.0522% (slightly lower)
- **Median % change:** -0.0391% (slightly lower)
- **Range:** -3.08% to +2.97%
- **Third buy higher than first:** 50 (38.46%)
- **Third buy lower than first:** 80 (61.54%)

### Profit Statistics (Sell vs First Buy)
- **Average % increase:** 0.49%
- **Median % increase:** 0.30%
- **Min % increase:** 0.0089%
- **Max % increase:** 3.30%
- **Std Dev:** 0.53%

### Detailed Statistics
| Metric | Value |
|--------|-------|
| Mean % | 0.4885% |
| Median % | 0.2974% |
| Min % | 0.0089% |
| Max % | 3.3005% |
| Std Dev % | 0.5315% |
| 25th Percentile % | 0.1654% |
| 75th Percentile % | 0.6734% |

### Additional Buy Analysis (Profitable Patterns Only)
- **Second Buy Average % change:** -0.03%
- **Second Buy Median % change:** -0.006%
- **Third Buy Average % change:** 0.07%
- **Third Buy Median % change:** -0.002%

---

## Profit Duration Analysis

### Overall Statistics (All 515 Profitable Cases)

#### Duration Statistics (Minutes)
- **Mean:** 532.31 minutes (8.87 hours)
- **Median:** 80.02 minutes (1.33 hours)
- **Min:** 2.00 minutes
- **Max:** 5,399.30 minutes (89.99 hours)
- **Std Dev:** 970.92 minutes
- **25th Percentile:** 36.18 minutes
- **75th Percentile:** 1,087.81 minutes (18.13 hours)

#### Duration Statistics (Hours)
- **Mean:** 8.87 hours
- **Median:** 1.33 hours
- **Min:** 0.03 hours
- **Max:** 89.99 hours
- **Std Dev:** 16.18 hours

### Statistics by Pattern

#### Pattern 1: Buy → Sell (267 cases)
| Metric | Value |
|--------|-------|
| Mean Duration | 267.23 minutes (4.45 hours) |
| Median Duration | 42.15 minutes (0.70 hours) |
| Min Duration | 2.00 minutes |
| Max Duration | 5,399.30 minutes (89.99 hours) |
| Std Dev | 737.11 minutes |
| 25th Percentile | 22.01 minutes |
| 75th Percentile | 72.00 minutes |
| Mean Profit | 0.31% |
| Median Profit | 0.20% |

#### Pattern 2: Buy → Buy → Sell (147 cases)
| Metric | Value |
|--------|-------|
| Mean Duration | 763.24 minutes (12.72 hours) |
| Median Duration | 140.00 minutes (2.33 hours) |
| Min Duration | 11.00 minutes |
| Max Duration | 4,060.32 minutes (67.67 hours) |
| Std Dev | 1,095.33 minutes |
| 25th Percentile | 82.39 minutes |
| 75th Percentile | 1,133.69 minutes (18.89 hours) |
| Mean Profit | 0.46% |
| Median Profit | 0.30% |

#### Pattern 3: Buy → Buy → Buy → Sell (101 cases)
| Metric | Value |
|--------|-------|
| Mean Duration | 896.97 minutes (14.95 hours) |
| Median Duration | 246.00 minutes (4.10 hours) |
| Min Duration | 40.05 minutes |
| Max Duration | 4,116.03 minutes (68.60 hours) |
| Std Dev | 1,117.23 minutes |
| 25th Percentile | 131.00 minutes |
| 75th Percentile | 1,194.70 minutes (19.91 hours) |
| Mean Profit | 0.49% |
| Median Profit | 0.30% |

---

## Duration Distribution

### Overall Distribution (All Patterns)

| Duration Range | Count | Percentage |
|----------------|-------|------------|
| 0-15 minutes | 41 | 7.96% |
| 15-30 minutes | 54 | 10.49% |
| 30-60 minutes | 105 | 20.39% |
| 1-2 hours | 112 | 21.75% |
| 2-4 hours | 57 | 11.07% |
| 4-8 hours | 3 | 0.58% |
| 8+ hours | 143 | 27.77% |

**Key Insight:** Approximately **60% of profitable cases occur within 2 hours** of the initial buy signal.

### Distribution by Pattern

#### Pattern 1: Buy → Sell
| Duration Range | Count | Percentage |
|----------------|-------|------------|
| 0-15 min | 40 | 14.98% |
| 15-30 min | 51 | 19.10% |
| 30-60 min | 80 | 29.96% |
| 1-2 hours | 56 | 20.97% |
| 2-4 hours | 5 | 1.87% |
| 4-8 hours | 0 | 0.00% |
| 8+ hours | 35 | 13.11% |

**Key Insight:** **64% of Pattern 1 profitable cases occur within 1 hour.**

#### Pattern 2: Buy → Buy → Sell
| Duration Range | Count | Percentage |
|----------------|-------|------------|
| 0-15 min | 1 | 0.68% |
| 15-30 min | 3 | 2.04% |
| 30-60 min | 21 | 14.29% |
| 1-2 hours | 41 | 27.89% |
| 2-4 hours | 21 | 14.29% |
| 4-8 hours | 0 | 0.00% |
| 8+ hours | 60 | 40.82% |

**Key Insight:** **41% of Pattern 2 profitable cases take 8+ hours** (likely spanning multiple trading days).

#### Pattern 3: Buy → Buy → Buy → Sell
| Duration Range | Count | Percentage |
|----------------|-------|------------|
| 0-15 min | 0 | 0.00% |
| 15-30 min | 0 | 0.00% |
| 30-60 min | 4 | 3.96% |
| 1-2 hours | 15 | 14.85% |
| 2-4 hours | 31 | 30.69% |
| 4-8 hours | 3 | 2.97% |
| 8+ hours | 48 | 47.52% |

**Key Insight:** **Nearly half (47.5%) of Pattern 3 profitable cases take 8+ hours.**

---

## Summary Table

| Pattern | Count | Mean Duration (min) | Median Duration (min) | Min Duration (min) | Max Duration (min) | Mean Profit % | Median Profit % |
|---------|-------|---------------------|----------------------|---------------------|-------------------|---------------|-----------------|
| Buy→Sell | 267 | 267.23 | 42.15 | 2.00 | 5,399.30 | 0.3129% | 0.1991% |
| Buy→Buy→Sell | 147 | 763.24 | 140.00 | 11.00 | 4,060.32 | 0.4621% | 0.2959% |
| Buy→Buy→Buy→Sell | 101 | 896.97 | 246.00 | 40.05 | 4,116.03 | 0.4885% | 0.2974% |

---

## Key Insights

### Profitability
1. **41.8% of buy signals** result in profitable sell opportunities within the next 3 signals
2. **Pattern 1 (Buy→Sell)** has the highest success rate (89.90%) when an immediate sell exists
3. **Patterns with more buys** tend to have slightly higher average profits (0.46-0.49% vs 0.31%)

### Duration
1. **Median time to profit is ~1.3 hours** overall, but varies significantly by pattern
2. **Pattern 1 is fastest:** Median of 42 minutes, with 64% occurring within 1 hour
3. **Patterns with more buys take longer:** Median durations increase from 42 min → 140 min → 246 min
4. **~60% of profitable cases occur within 2 hours** of the initial buy signal
5. **~28% of cases take 8+ hours**, likely spanning multiple trading days

### Price Movement
1. **Second and third buys are often slightly lower** than the first buy (median around -0.02% to -0.04%)
2. **Even with lower subsequent buys**, the patterns remain profitable in most cases
3. **The sell signal typically occurs at a higher price** than the first buy, regardless of intermediate buy prices

---

## Conclusions

1. **Confidence Level:** If you buy at a buy signal, you have a **41.8% chance** that the first sell signal appearing within the next 3 signals will be at a higher price, allowing you to profit.

2. **Time to Profit:** The median time to realize profit is **1.3 hours**, with the fastest pattern (Buy→Sell) having a median of **42 minutes**.

3. **Pattern Selection:** 
   - For **faster profits**: Pattern 1 (Buy→Sell) offers the quickest turnaround
   - For **higher profits**: Patterns 2 and 3 offer slightly better average returns (0.46-0.49% vs 0.31%)

4. **Risk Consideration:** Approximately **58.2% of buy signals** do not result in profitable sell opportunities within the next 3 signals, indicating the importance of risk management and position sizing.

---

## Data Files

The following CSV files contain detailed results for further analysis:
- `buy_sell_confidence_analysis.csv` - Detailed buy signal confidence analysis
- `buy_buy_sell_pattern_analysis.csv` - Buy→Buy→Sell pattern analysis
- `buy_buy_buy_sell_pattern_analysis.csv` - Buy→Buy→Buy→Sell pattern analysis
- `profit_duration_analysis.csv` - Duration analysis for all profitable cases

---

## Analysis Scripts

The following Python scripts were used to generate this analysis:
- `analyze_buy_sell_confidence.py` - Analyzes immediate sell signals after buy signals
- `analyze_buy_buy_sell_pattern.py` - Analyzes Buy→Buy→Sell patterns
- `analyze_buy_buy_buy_sell_pattern.py` - Analyzes Buy→Buy→Buy→Sell patterns
- `analyze_profit_duration.py` - Analyzes duration to profit for all profitable cases

---

*Report generated from analysis of combined_data.csv containing 2,361 signals across multiple trading days.*

