"""
Analyze signal statistics from CSV files in SPXsignal folder.

This script reads all CSV files from ~/Desktop/SPXsignal/ and calculates:
- Daily signal counts (overall, buy, sell)
- Statistics: min, max, median, average
- Time-of-day distribution histograms (9:30 AM to 4:00 PM, 15-minute bins)

Usage:
    python analyze_signal_statistics.py
"""
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime, time

# =========================
# CONFIG
# =========================
DATA_DIR = Path.home() / "Desktop" / "SPXsignal"
DATE_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.csv$")

# Trading hours
TRADING_START = time(9, 30)  # 9:30 AM
TRADING_END = time(16, 0)     # 4:00 PM

# Bin size for histograms (15 minutes)
BIN_SIZE_MINUTES = 15


def parse_timestamp(timestamp_str: str, trading_date: str) -> pd.Timestamp:
    """
    Parse timestamp string, handling both full datetime and time-only formats.
    
    Args:
        timestamp_str: Timestamp string (YYYY-MM-DD HH:MM:SS or HH:MM:SS)
        trading_date: Date string in YYYY-MM-DD format (used if timestamp is time-only)
    
    Returns:
        Parsed pandas Timestamp or NaT if parsing fails
    """
    # First try parsing as full datetime
    parsed = pd.to_datetime(timestamp_str, format="%Y-%m-%d %H:%M:%S", errors='coerce')
    
    # If that fails, try combining with trading_date (for time-only format)
    if pd.isna(parsed):
        try:
            parsed = pd.to_datetime(
                f"{trading_date} {timestamp_str}",
                format="%Y-%m-%d %H:%M:%S",
                errors='coerce'
            )
        except:
            pass
    
    return parsed


def read_all_csv_files() -> pd.DataFrame:
    """
    Read all CSV files from SPXsignal folder and combine into a single DataFrame.
    
    Returns:
        DataFrame with columns: date, timestamp, buy/sell, time_of_day
    """
    if not DATA_DIR.exists():
        print(f"Error: Directory {DATA_DIR} does not exist")
        return pd.DataFrame()
    
    # Get all CSV files matching date pattern
    csv_files = sorted([f for f in os.listdir(DATA_DIR) if DATE_FILE_PATTERN.match(f)])
    
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return pd.DataFrame()
    
    print(f"Found {len(csv_files)} CSV files")
    print("Reading and parsing files...")
    
    all_data = []
    
    for fname in csv_files:
        file_path = DATA_DIR / fname
        trading_date = fname.replace(".csv", "")
        
        try:
            df = pd.read_csv(file_path)
            
            # Check required columns
            if "timestamp" not in df.columns or "buy/sell" not in df.columns:
                print(f"  Skipping {fname}: missing required columns")
                continue
            
            # Parse timestamps
            df['parsed_timestamp'] = df['timestamp'].apply(
                lambda x: parse_timestamp(str(x), trading_date)
            )
            
            # Filter out invalid timestamps
            df = df[df['parsed_timestamp'].notna()].copy()
            
            if len(df) == 0:
                print(f"  Skipping {fname}: no valid timestamps")
                continue
            
            # Extract time of day
            df['time_of_day'] = df['parsed_timestamp'].dt.time
            df['date'] = trading_date
            
            # Filter to trading hours
            df = df[
                (df['time_of_day'] >= TRADING_START) & 
                (df['time_of_day'] <= TRADING_END)
            ].copy()
            
            if len(df) > 0:
                all_data.append(df[['date', 'parsed_timestamp', 'buy/sell', 'time_of_day']])
                print(f"  Processed {fname}: {len(df)} signals")
            else:
                print(f"  Skipping {fname}: no signals in trading hours")
                
        except Exception as e:
            print(f"  Error processing {fname}: {e}")
            continue
    
    if not all_data:
        print("No valid data found in any CSV files")
        return pd.DataFrame()
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal signals loaded: {len(combined_df)}")
    
    return combined_df


def calculate_daily_statistics(df: pd.DataFrame) -> dict:
    """
    Calculate daily signal counts and statistics.
    
    Args:
        df: DataFrame with signal data
    
    Returns:
        Dictionary with statistics for overall, buy, and sell signals
    """
    # Group by date
    daily_counts = df.groupby('date').size()
    
    # Buy signals per day
    buy_df = df[df['buy/sell'].str.upper().str.strip() == 'BUY']
    buy_daily = buy_df.groupby('date').size()
    
    # Sell signals per day
    sell_df = df[df['buy/sell'].str.upper().str.strip() == 'SELL']
    sell_daily = sell_df.groupby('date').size()
    
    # Calculate statistics
    stats = {
        'overall': {
            'counts': daily_counts,
            'min': daily_counts.min(),
            'max': daily_counts.max(),
            'median': daily_counts.median(),
            'average': daily_counts.mean()
        },
        'buy': {
            'counts': buy_daily,
            'min': buy_daily.min() if len(buy_daily) > 0 else 0,
            'max': buy_daily.max() if len(buy_daily) > 0 else 0,
            'median': buy_daily.median() if len(buy_daily) > 0 else 0,
            'average': buy_daily.mean() if len(buy_daily) > 0 else 0
        },
        'sell': {
            'counts': sell_daily,
            'min': sell_daily.min() if len(sell_daily) > 0 else 0,
            'max': sell_daily.max() if len(sell_daily) > 0 else 0,
            'median': sell_daily.median() if len(sell_daily) > 0 else 0,
            'average': sell_daily.mean() if len(sell_daily) > 0 else 0
        }
    }
    
    return stats


def create_time_bins():
    """
    Create 15-minute time bins from 9:30 AM to 4:00 PM.
    
    Returns:
        List of time objects representing bin start times
    """
    bins = []
    current_hour = 9
    current_minute = 30
    
    while current_hour < 16 or (current_hour == 16 and current_minute == 0):
        bins.append(time(current_hour, current_minute))
        current_minute += BIN_SIZE_MINUTES
        if current_minute >= 60:
            current_minute = 0
            current_hour += 1
    
    return bins


def time_to_minutes(t: time) -> int:
    """
    Convert time to minutes since midnight.
    
    Args:
        t: time object
    
    Returns:
        Minutes since midnight
    """
    return t.hour * 60 + t.minute


def create_stacked_histogram(df: pd.DataFrame, title: str, filename: str):
    """
    Create a bar chart showing buy (green, negative/below x-axis) and sell (red, positive/above x-axis) signals.
    The x-axis acts as the separation line between buy and sell.
    
    Args:
        df: DataFrame with signal data (should contain both buy and sell)
        title: Plot title
        filename: Output filename
    """
    if len(df) == 0:
        print(f"  Warning: No data for stacked histogram, skipping")
        return
    
    # Separate buy and sell signals
    buy_df = df[df['buy/sell'].str.upper().str.strip() == 'BUY']
    sell_df = df[df['buy/sell'].str.upper().str.strip() == 'SELL']
    
    # Get time bins
    time_bins = create_time_bins()
    
    # Create bin edges in minutes
    bin_edges_minutes = [time_to_minutes(t) for t in time_bins]
    bin_edges_minutes.append(time_to_minutes(TRADING_END))
    
    # Convert times to minutes for binning and count signals in each bin
    if len(buy_df) > 0:
        buy_minutes = buy_df['time_of_day'].apply(time_to_minutes)
        buy_counts, _ = np.histogram(buy_minutes, bins=bin_edges_minutes)
    else:
        buy_counts = np.zeros(len(time_bins))
    
    if len(sell_df) > 0:
        sell_minutes = sell_df['time_of_day'].apply(time_to_minutes)
        sell_counts, _ = np.histogram(sell_minutes, bins=bin_edges_minutes)
    else:
        sell_counts = np.zeros(len(time_bins))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Bin centers for x-axis positioning
    bin_centers = [(bin_edges_minutes[i] + bin_edges_minutes[i+1]) / 2 for i in range(len(bin_edges_minutes)-1)]
    bin_width = bin_edges_minutes[1] - bin_edges_minutes[0]
    
    # Make buy counts negative (below x-axis) and sell counts positive (above x-axis)
    buy_counts_neg = -buy_counts.astype(float)
    sell_counts_pos = sell_counts.astype(float)
    
    # Create bars
    # Buy signals (green, negative, below x-axis)
    ax.bar(bin_centers, buy_counts_neg, width=bin_width*0.8, label='Buy', color='green', alpha=0.7, edgecolor='black')
    
    # Sell signals (red, positive, above x-axis)
    ax.bar(bin_centers, sell_counts_pos, width=bin_width*0.8, label='Sell', color='red', alpha=0.7, edgecolor='black')
    
    # Add horizontal line at y=0 to emphasize separation
    ax.axhline(y=0, color='black', linewidth=1.5, linestyle='-', zorder=0)
    
    # Format x-axis labels
    bin_labels = [t.strftime('%H:%M') for t in time_bins]
    ax.set_xticks(bin_centers)
    ax.set_xticklabels(bin_labels, rotation=45, ha='right')
    
    # Labels and title
    ax.set_xlabel('Time of Day', fontsize=12)
    ax.set_ylabel('Signal Count', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='upper right')
    
    # Set y-axis to show symmetric range if needed
    buy_max = abs(buy_counts_neg.min()) if len(buy_counts_neg) > 0 and buy_counts_neg.min() < 0 else 0
    sell_max = sell_counts_pos.max() if len(sell_counts_pos) > 0 and sell_counts_pos.max() > 0 else 0
    max_abs = max(buy_max, sell_max)
    if max_abs > 0:
        ax.set_ylim(-max_abs * 1.1, max_abs * 1.1)
    
    # Add value labels on bars
    for i, (buy_count, sell_count) in enumerate(zip(buy_counts, sell_counts)):
        # Label for buy (at middle of buy bar, which is negative)
        if buy_count > 0:
            ax.text(bin_centers[i], buy_counts_neg[i] / 2, f'{int(buy_count)}', 
                   ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        # Label for sell (at middle of sell bar, which is positive)
        if sell_count > 0:
            ax.text(bin_centers[i], sell_counts_pos[i] / 2, f'{int(sell_count)}', 
                   ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"  Saved histogram: {filename}")
    plt.close()


def create_histogram(df: pd.DataFrame, signal_type: str, title: str, filename: str):
    """
    Create a histogram of signal distribution by time of day.
    
    Args:
        df: DataFrame with signal data
        signal_type: 'all', 'buy', or 'sell'
        title: Plot title
        filename: Output filename
    """
    if len(df) == 0:
        print(f"  Warning: No data for {signal_type} signals, skipping histogram")
        return
    
    # Get time bins
    time_bins = create_time_bins()
    
    # Convert times to minutes since midnight for binning
    df_minutes = df['time_of_day'].apply(time_to_minutes)
    
    # Create bin edges in minutes
    bin_edges_minutes = [time_to_minutes(t) for t in time_bins]
    # Add the end time (4:00 PM = 960 minutes)
    bin_edges_minutes.append(time_to_minutes(TRADING_END))
    
    # Create histogram
    fig, ax = plt.subplots(figsize=(14, 6))
    counts, bins, patches = ax.hist(df_minutes, bins=bin_edges_minutes, edgecolor='black', alpha=0.7)
    
    # Format x-axis labels
    bin_labels = [t.strftime('%H:%M') for t in time_bins]
    # Use bin centers for labels
    bin_centers = [(bin_edges_minutes[i] + bin_edges_minutes[i+1]) / 2 for i in range(len(bin_edges_minutes)-1)]
    ax.set_xticks(bin_centers)
    ax.set_xticklabels(bin_labels, rotation=45, ha='right')
    
    # Labels and title
    ax.set_xlabel('Time of Day', fontsize=12)
    ax.set_ylabel('Signal Count', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (count, patch) in enumerate(zip(counts, patches)):
        if count > 0:
            ax.text(patch.xy[0] + patch.get_width()/2, count + max(counts)*0.01,
                   f'{int(count)}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"  Saved histogram: {filename}")
    plt.close()


def print_statistics(stats: dict):
    """
    Print statistics to console in formatted tables.
    
    Args:
        stats: Dictionary with statistics data
    """
    print("\n" + "=" * 80)
    print("SIGNAL STATISTICS")
    print("=" * 80)
    
    # Overall signals
    print("\n" + "-" * 80)
    print("OVERALL SIGNALS PER DAY (Buy + Sell)")
    print("-" * 80)
    print(f"  Minimum:  {stats['overall']['min']:.1f}")
    print(f"  Maximum:  {stats['overall']['max']:.1f}")
    print(f"  Median:   {stats['overall']['median']:.1f}")
    print(f"  Average:  {stats['overall']['average']:.2f}")
    print(f"  Total days: {len(stats['overall']['counts'])}")
    
    # Buy signals
    print("\n" + "-" * 80)
    print("BUY SIGNALS PER DAY")
    print("-" * 80)
    print(f"  Minimum:  {stats['buy']['min']:.1f}")
    print(f"  Maximum:  {stats['buy']['max']:.1f}")
    print(f"  Median:   {stats['buy']['median']:.1f}")
    print(f"  Average:  {stats['buy']['average']:.2f}")
    print(f"  Total days: {len(stats['buy']['counts'])}")
    
    # Sell signals
    print("\n" + "-" * 80)
    print("SELL SIGNALS PER DAY")
    print("-" * 80)
    print(f"  Minimum:  {stats['sell']['min']:.1f}")
    print(f"  Maximum:  {stats['sell']['max']:.1f}")
    print(f"  Median:   {stats['sell']['median']:.1f}")
    print(f"  Average:  {stats['sell']['average']:.2f}")
    print(f"  Total days: {len(stats['sell']['counts'])}")
    
    print("\n" + "=" * 80)


def main():
    """Main function to run the analysis."""
    print("=" * 80)
    print("SIGNAL STATISTICS ANALYSIS")
    print("=" * 80)
    print(f"Data directory: {DATA_DIR}")
    print(f"Trading hours: {TRADING_START.strftime('%H:%M')} - {TRADING_END.strftime('%H:%M')}")
    print(f"Histogram bin size: {BIN_SIZE_MINUTES} minutes")
    print("=" * 80)
    
    # Read all CSV files
    df = read_all_csv_files()
    
    if len(df) == 0:
        print("No data to analyze. Exiting.")
        return
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats = calculate_daily_statistics(df)
    
    # Print statistics
    print_statistics(stats)
    
    # Create histograms
    print("\nGenerating histograms...")
    
    # Overall signals histogram (stacked: buy in green at bottom, sell in red on top)
    create_stacked_histogram(
        df,
        'Signal Time Distribution (Buy and Sell)',
        'signal_time_distribution.png'
    )
    
    # Buy signals histogram
    buy_df = df[df['buy/sell'].str.upper().str.strip() == 'BUY']
    create_histogram(
        buy_df,
        'buy',
        'Buy Signal Time Distribution',
        'buy_signal_time_distribution.png'
    )
    
    # Sell signals histogram
    sell_df = df[df['buy/sell'].str.upper().str.strip() == 'SELL']
    create_histogram(
        sell_df,
        'sell',
        'Sell Signal Time Distribution',
        'sell_signal_time_distribution.png'
    )
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nOutput files:")
    print("  - signal_time_distribution.png")
    print("  - buy_signal_time_distribution.png")
    print("  - sell_signal_time_distribution.png")
    print("=" * 80)


if __name__ == "__main__":
    main()

