# SPXL Test Results (Fixed Shares)

This folder contains SPXL backtest outputs for strategies 2 through 4.2 using the original fixed-share buy sizing.

Included:
- Strategy comparison report (`strategy_comparison_report.md`)
- Equity curve and daily P&L comparisons (`equity_curve_comparison.png`, `daily_pnl_comparison.png`)
- Per-strategy statistics (`strategy*_statistics.csv`)
- Per-strategy trades (`strategy*_trades.csv`)

## Notes
Fixed-share sizing buys a constant number of shares per signal, which makes the effective dollar exposure vary with price.
This can under- or over-size positions as SPXL price changes, especially in a leveraged instrument where volatility is higher.

