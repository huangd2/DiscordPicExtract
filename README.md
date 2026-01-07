# SPX Trading Strategy Backtest

A comprehensive backtest analysis of a trading strategy based on SPX (S&P 500) signals.

## Overview

This repository contains:
- Backtest implementation code
- Trading signals data
- Performance analysis and visualizations
- Comprehensive backtest report

## Strategy Description

The strategy executes trades based on Buy/Sell signals with the following rules:

1. **Buy Signal:** Purchase 1 share at `fPrice` when a Buy signal with `risk='low'` occurs
2. **Sell Signal:** Sell all held shares when a Sell signal with `risk='low'` or `risk='medium'` occurs
3. **Position Management:** Positions can carry over to the next trading day
4. **Capital Constraint:** Only buy if sufficient cash is available (starting capital: $10,000)

## Files

- `backtest_strategy.py` - Main backtest implementation
- `combined_data.csv` - Combined trading signals from all trading days
- `BACKTEST_REPORT.md` - Comprehensive analysis report with findings
- Visualization PNG files (6 charts)

## Results Summary

- **Initial Capital:** $10,000.00
- **Final Value:** $10,224.69
- **Return:** 2.25%
- **Total Trades:** 187
- **Win Rate:** 79.7%

## Usage

Run the backtest:

```bash
python backtest_strategy.py
```

This will:
1. Process all trading signals
2. Execute trades according to strategy rules
3. Calculate performance metrics
4. Generate visualizations
5. Print comprehensive statistics

## Requirements

- Python 3.x
- pandas
- matplotlib
- numpy

## See Also

See `BACKTEST_REPORT.md` for detailed analysis, findings, and visualizations.

