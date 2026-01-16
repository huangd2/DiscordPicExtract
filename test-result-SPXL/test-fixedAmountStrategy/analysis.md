# SPXL Test Results (Fixed Dollar Amounts)

This folder contains SPXL backtest outputs for strategies 2 through 4.2 using fixed-dollar buy sizing:
first three buys sized at $1500, $1500, and $3000.

Included:
- Strategy comparison report (`strategy_comparison_report.md`)
- Equity curve and daily P&L comparisons (`equity_curve_comparison.png`, `daily_pnl_comparison.png`)
- Per-strategy statistics (`strategy*_statistics.csv`)
- Per-strategy trades (`strategy*_trades.csv`)

## Why fixed-amount can be better
- Consistent risk per entry: dollar exposure stays stable across price changes.
- Better comparability: performance reflects signal quality more than price level.
- Reduced leverage drift: avoids unintentionally increasing exposure when price drops.
