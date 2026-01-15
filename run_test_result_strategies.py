"""
Run strategies 2, 3, 4, 4.1, and 4.2 on test-result/combined_data.csv
and save outputs + comparison artifacts into test-result.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
TEST_RESULT_DIR = SCRIPT_DIR / "test-result"
TEST_COMBINED = TEST_RESULT_DIR / "combined_data.csv"
ROOT_COMBINED = SCRIPT_DIR / "combined_data.csv"
BACKUP_COMBINED = SCRIPT_DIR / "combined_data.backup.csv"


STRATEGY_SCRIPTS = [
    "strategy2_low_risk_accumulation.py",
    "strategy3_low_risk_accumulation.py",
    "strategy4_progressive_exit.py",
    "strategy4_progressive_exit_even_thirds.py",
    "strategy4_progressive_exit_even_thirds_v2.py",
]


STRATEGY_OUTPUTS = {
    "Strategy 2": {
        "trades": SCRIPT_DIR / "strategy2" / "strategy2_low_risk_accumulation_trades.csv",
        "stats": SCRIPT_DIR / "strategy2" / "strategy2_statistics.csv",
    },
    "Strategy 3": {
        "trades": SCRIPT_DIR / "strategy3" / "strategy3_low_risk_accumulation_trades.csv",
        "stats": SCRIPT_DIR / "strategy3" / "strategy3_statistics.csv",
    },
    "Strategy 4": {
        "trades": SCRIPT_DIR / "strategy4" / "strategy4_progressive_exit_trades.csv",
        "stats": SCRIPT_DIR / "strategy4" / "strategy4_statistics.csv",
    },
    "Strategy 4.1": {
        "trades": SCRIPT_DIR / "strategy4" / "strategy4_progressive_exit_even_thirds_trades.csv",
        "stats": SCRIPT_DIR / "strategy4" / "strategy4_even_thirds_statistics.csv",
    },
    "Strategy 4.2": {
        "trades": SCRIPT_DIR / "strategy4.2" / "strategy4_progressive_exit_even_thirds_v2_trades.csv",
        "stats": SCRIPT_DIR / "strategy4.2" / "strategy4_v2_statistics.csv",
    },
}


def ensure_test_data() -> None:
    if not TEST_COMBINED.exists():
        raise FileNotFoundError(f"Missing test combined data: {TEST_COMBINED}")
    TEST_RESULT_DIR.mkdir(parents=True, exist_ok=True)


def swap_in_test_combined() -> None:
    if ROOT_COMBINED.exists():
        shutil.copy2(ROOT_COMBINED, BACKUP_COMBINED)
    shutil.copy2(TEST_COMBINED, ROOT_COMBINED)


def restore_combined() -> None:
    if BACKUP_COMBINED.exists():
        shutil.copy2(BACKUP_COMBINED, ROOT_COMBINED)
        BACKUP_COMBINED.unlink()


def run_strategies() -> None:
    for script in STRATEGY_SCRIPTS:
        script_path = SCRIPT_DIR / script
        print(f"Running {script_path.name}...")
        subprocess.run(["python", str(script_path)], check=True)


def copy_outputs_to_test_result() -> None:
    for strategy, outputs in STRATEGY_OUTPUTS.items():
        for key, path in outputs.items():
            if not path.exists():
                raise FileNotFoundError(f"Expected output missing: {path}")
            dest = TEST_RESULT_DIR / path.name
            shutil.copy2(path, dest)
            print(f"Copied {strategy} {key}: {dest.name}")


def load_combined_data() -> pd.DataFrame:
    df = pd.read_csv(TEST_COMBINED)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_daily_pnl(trades_csv: Path, trading_days: List[pd.Timestamp]) -> List[float]:
    trades_df = pd.read_csv(trades_csv)
    trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"])
    trades_df["date"] = trades_df["timestamp"].dt.date
    trades_df["PnL"] = pd.to_numeric(trades_df["PnL"], errors="coerce")
    daily_pnl = trades_df.groupby("date")["PnL"].sum()
    return [float(daily_pnl.get(day, 0.0)) for day in trading_days]


def compute_forced_close(
    trades_csv: Path,
    initial_capital: float = 10000.0,
) -> Tuple[float, float, Optional[float]]:
    trades_df = pd.read_csv(trades_csv)
    trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"])
    trades_df = trades_df.sort_values("timestamp").reset_index(drop=True)

    trades_df["position"] = pd.to_numeric(trades_df["position"], errors="coerce")
    trades_df["avgPrice"] = pd.to_numeric(trades_df["avgPrice"], errors="coerce")
    trades_df["remaining capital"] = pd.to_numeric(trades_df["remaining capital"], errors="coerce")

    current_cash = initial_capital
    current_position = 0
    current_avg_price = None
    last_sell_price = None

    for _, row in trades_df.iterrows():
        if pd.notna(row.get("remaining capital")):
            current_cash = float(row["remaining capital"])
        if pd.notna(row.get("position")):
            current_position = int(row["position"])
        if pd.notna(row.get("avgPrice")):
            current_avg_price = float(row["avgPrice"])

        action = str(row.get("buy/sell", ""))
        if action.startswith("Sell"):
            last_sell_price = float(row["fPrice"]) if pd.notna(row.get("fPrice")) else last_sell_price

        if str(row.get("trade #", "")).strip():
            if current_position == 0:
                current_avg_price = None
                last_sell_price = None

    if current_position > 0:
        close_price = last_sell_price if last_sell_price is not None else current_avg_price
        if close_price is None:
            close_price = float(trades_df.iloc[-1]["fPrice"])
        final_value = current_cash + (current_position * close_price)
    else:
        final_value = current_cash
        close_price = None

    total_pnl = final_value - initial_capital
    return final_value, total_pnl, close_price


def compute_equity_curve(
    trades_csv: Path,
    combined_df: pd.DataFrame,
    trading_days: List[pd.Timestamp],
    initial_capital: float = 10000.0,
) -> List[float]:
    trades_df = pd.read_csv(trades_csv)
    trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"])
    trades_df = trades_df.sort_values("timestamp").reset_index(drop=True)

    combined_last_prices = (
        combined_df.groupby("date")["fPrice"].last().to_dict()
    )

    equity_curve = []
    current_cash = initial_capital
    current_position = 0
    action_idx = 0

    for day in trading_days:
        day_signals = combined_df[combined_df["date"] == day]
        if day_signals.empty:
            equity_curve.append(current_cash)
            continue

        end_of_day_time = day_signals["timestamp"].max()

        while action_idx < len(trades_df) and trades_df.loc[action_idx, "timestamp"] <= end_of_day_time:
            row = trades_df.loc[action_idx]
            if pd.notna(row.get("remaining capital")):
                current_cash = float(row["remaining capital"])
            if pd.notna(row.get("position")):
                current_position = int(row["position"])
            action_idx += 1

        last_price = float(combined_last_prices.get(day, 0.0))
        equity = current_cash + (current_position * last_price if current_position > 0 else 0.0)
        equity_curve.append(equity)

    if current_position > 0:
        _, _, close_price = compute_forced_close(trades_csv, initial_capital=initial_capital)
        if close_price is not None:
            equity_curve[-1] = current_cash + (current_position * close_price)

    return equity_curve


def plot_daily_pnl_comparison(trading_days: List[pd.Timestamp], pnl_by_strategy: Dict[str, List[float]]) -> None:
    strategies = list(pnl_by_strategy.keys())
    all_values = [val for values in pnl_by_strategy.values() for val in values]
    min_val = min(all_values) if all_values else 0.0
    max_val = max(all_values) if all_values else 0.0
    padding = (max_val - min_val) * 0.05 if max_val != min_val else 10.0
    ylim = (min_val - padding, max_val + padding)

    fig, axes = plt.subplots(len(strategies), 1, figsize=(16, 3.2 * len(strategies)), sharex=True)
    if len(strategies) == 1:
        axes = [axes]

    for ax, strategy in zip(axes, strategies):
        pnl_values = pnl_by_strategy[strategy]
        colors = ["green" if v >= 0 else "red" for v in pnl_values]
        ax.bar(range(len(trading_days)), pnl_values, color=colors, alpha=0.75, edgecolor="black")
        ax.set_title(strategy)
        ax.set_ylabel("Daily P&L ($)")
        ax.axhline(y=0, color="black", linewidth=1)
        ax.set_ylim(*ylim)
        ax.grid(True, alpha=0.3, axis="y")

    axes[-1].set_xlabel("Trading Day Index")
    fig.suptitle("Daily P&L Comparison (Same Y-Axis Range)", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    output_path = TEST_RESULT_DIR / "daily_pnl_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {output_path}")


def plot_equity_curve_overlay(trading_days: List[pd.Timestamp], equity_by_strategy: Dict[str, List[float]]) -> None:
    plt.figure(figsize=(16, 8))
    for strategy, equity_values in equity_by_strategy.items():
        plt.plot(range(len(trading_days)), equity_values, linewidth=2, label=strategy)

    plt.axhline(y=10000.0, color="gray", linestyle="--", linewidth=1, label="Initial Capital")
    plt.xlabel("Trading Day Index")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Equity Curve Comparison (Overlay)", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    output_path = TEST_RESULT_DIR / "equity_curve_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {output_path}")


def build_stats_report() -> None:
    report_lines = [
        "# Strategy Comparison Report (Test Result)",
        "",
        "Final value is adjusted using the Strategy 4.1 final close rule:",
        "close any remaining position at last sell price if any sells occurred,",
        "otherwise close at avg buy price.",
        "",
        "| Strategy | Final Value | Total P&L | Return (%) | Trades | Win Rate (%) | Avg P&L / Trade | Days No Trades | Stop-Loss Trades |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for strategy, outputs in STRATEGY_OUTPUTS.items():
        stats_df = pd.read_csv(outputs["stats"])
        stats_map = dict(zip(stats_df["Metric"], stats_df["Value"]))
        final_value, total_pnl, _ = compute_forced_close(outputs["trades"])
        return_pct = (final_value / 10000.0 - 1) * 100

        def get_metric(name: str, default: str = "N/A") -> str:
            return str(stats_map.get(name, default))

        report_lines.append(
            f"| {strategy} | "
            f"${final_value:,.2f} | "
            f"${total_pnl:,.2f} | "
            f"{return_pct:.2f} | "
            f"{get_metric('Total Trades Executed')} | "
            f"{get_metric('Win Rate (%)')} | "
            f"{get_metric('Average P&L per Trade')} | "
            f"{get_metric('Days with No Trades')} | "
            f"{get_metric('Stop-Loss Triggered')} |"
        )

    report_path = TEST_RESULT_DIR / "strategy_comparison_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Saved {report_path}")


def main() -> None:
    ensure_test_data()
    swap_in_test_combined()
    try:
        run_strategies()
        copy_outputs_to_test_result()

        combined_df = load_combined_data()
        trading_days = list(combined_df["date"].unique())

        pnl_by_strategy = {
            name: compute_daily_pnl(outputs["trades"], trading_days)
            for name, outputs in STRATEGY_OUTPUTS.items()
        }

        equity_by_strategy = {
            name: compute_equity_curve(outputs["trades"], combined_df, trading_days)
            for name, outputs in STRATEGY_OUTPUTS.items()
        }

        plot_daily_pnl_comparison(trading_days, pnl_by_strategy)
        plot_equity_curve_overlay(trading_days, equity_by_strategy)
        build_stats_report()
    finally:
        restore_combined()


if __name__ == "__main__":
    main()

