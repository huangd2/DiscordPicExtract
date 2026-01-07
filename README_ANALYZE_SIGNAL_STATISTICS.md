# Signal Statistics Analysis

This script analyzes trading signal statistics from CSV files in the SPXsignal folder, providing comprehensive insights into signal patterns and time-of-day distributions.

## Overview

The `analyze_signal_statistics.py` script processes all CSV files from `~/Desktop/SPXsignal/` and generates:
- Daily signal count statistics (overall, buy, sell)
- Time-of-day distribution histograms
- Comprehensive statistical summaries

## Prerequisites

- Python 3.8 or higher
- CSV files in `~/Desktop/SPXsignal/` directory (format: `YYYY-MM-DD.csv`)
- Required Python packages (install via `pip install -r requirements.txt`):
  - pandas
  - matplotlib
  - numpy

## CSV File Format

The script expects CSV files with the following columns:
- `signal#`: Signal number
- `timestamp`: Timestamp in format `YYYY-MM-DD HH:MM:SS` or `HH:MM:SS`
- `price`: Signal price
- `buy/sell`: Signal type (`Buy` or `Sell`)
- `fPrice`: (Optional) Fetched price from market data
- `risk`: (Optional) Risk level

## Usage

### Basic Usage

```bash
python analyze_signal_statistics.py
```

The script will:
1. Read all CSV files from `~/Desktop/SPXsignal/`
2. Parse timestamps and filter to trading hours (9:30 AM - 4:00 PM)
3. Calculate daily statistics
4. Generate three histogram plots
5. Print statistics to console

### Output Files

The script generates three PNG files in the workspace directory:

1. **`signal_time_distribution.png`**: Stacked bar chart showing buy (green, below x-axis) and sell (red, above x-axis) signals by time of day
2. **`buy_signal_time_distribution.png`**: Histogram of buy signal distribution by time of day
3. **`sell_signal_time_distribution.png`**: Histogram of sell signal distribution by time of day

## Statistics Calculated

### Overall Signals Per Day
- **Minimum**: Lowest number of total signals (buy + sell) in any single day
- **Maximum**: Highest number of total signals in any single day
- **Median**: Middle value of daily signal counts
- **Average**: Mean number of signals per day

### Buy Signals Per Day
- **Minimum**: Lowest number of buy signals in any single day
- **Maximum**: Highest number of buy signals in any single day
- **Median**: Middle value of daily buy signal counts
- **Average**: Mean number of buy signals per day

### Sell Signals Per Day
- **Minimum**: Lowest number of sell signals in any single day
- **Maximum**: Highest number of sell signals in any single day
- **Median**: Middle value of daily sell signal counts
- **Average**: Mean number of sell signals per day

## Example Output

### Console Statistics

```
================================================================================
SIGNAL STATISTICS
================================================================================

--------------------------------------------------------------------------------
OVERALL SIGNALS PER DAY (Buy + Sell)
--------------------------------------------------------------------------------
  Minimum:  5.0
  Maximum:  25.0
  Median:   12.0
  Average:  12.45
  Total days: 150

--------------------------------------------------------------------------------
BUY SIGNALS PER DAY
--------------------------------------------------------------------------------
  Minimum:  2.0
  Maximum:  15.0
  Median:   6.0
  Average:  6.23
  Total days: 150

--------------------------------------------------------------------------------
SELL SIGNALS PER DAY
--------------------------------------------------------------------------------
  Minimum:  1.0
  Maximum:  12.0
  Median:   5.0
  Average:  6.22
  Total days: 150

================================================================================
```

### Histogram Features

#### Signal Time Distribution (Overall)
- **X-axis**: Time of day (9:30 AM to 4:00 PM) in 15-minute bins
- **Y-axis**: Signal count
- **Buy signals**: Green bars extending downward (negative values, below x-axis)
- **Sell signals**: Red bars extending upward (positive values, above x-axis)
- **Separation**: X-axis (y=0) acts as the clear separation line
- **Labels**: Individual counts shown in each bar segment, total count at top

#### Buy/Sell Signal Time Distributions
- **X-axis**: Time of day (9:30 AM to 4:00 PM) in 15-minute bins
- **Y-axis**: Signal count
- **Bins**: 15-minute intervals (9:30, 9:45, 10:00, ..., 3:45, 4:00)
- **Labels**: Count values displayed on each bar

## How It Works

### 1. Data Loading
- Scans `~/Desktop/SPXsignal/` for CSV files matching pattern `YYYY-MM-DD.csv`
- Reads each CSV file and extracts signal data
- Handles both full datetime (`YYYY-MM-DD HH:MM:SS`) and time-only (`HH:MM:SS`) timestamp formats

### 2. Timestamp Processing
- Parses timestamps, combining time-only values with date from filename
- Filters to trading hours: 9:30 AM to 4:00 PM (US EST)
- Extracts time-of-day for histogram binning

### 3. Statistics Calculation
- Groups signals by date
- Separates buy and sell signals
- Calculates min, max, median, and average for each category

### 4. Histogram Generation
- Creates 15-minute time bins from 9:30 AM to 4:00 PM
- Counts signals in each bin
- Generates visualizations with appropriate colors and labels

## Time Bins

The histograms use 15-minute bins covering the trading day:
- 9:30 AM - 9:45 AM
- 9:45 AM - 10:00 AM
- 10:00 AM - 10:15 AM
- ...
- 3:45 PM - 4:00 PM

Total: 26 bins covering the full trading session

## Configuration

You can modify the following constants in the script:

```python
DATA_DIR = Path.home() / "Desktop" / "SPXsignal"  # CSV file directory
TRADING_START = time(9, 30)  # Trading day start (9:30 AM)
TRADING_END = time(16, 0)     # Trading day end (4:00 PM)
BIN_SIZE_MINUTES = 15        # Histogram bin size
```

## Troubleshooting

### "No CSV files found"
- Verify that `~/Desktop/SPXsignal/` directory exists
- Check that CSV files are named in `YYYY-MM-DD.csv` format
- Ensure you have read permissions for the directory

### "No valid timestamps"
- Check that CSV files contain a `timestamp` column
- Verify timestamp format matches expected patterns
- Ensure timestamps are within trading hours (9:30 AM - 4:00 PM)

### "No data to analyze"
- Verify CSV files contain signal data
- Check that `buy/sell` column exists and contains valid values
- Ensure at least some signals fall within trading hours

### Empty Histograms
- Check that signals exist in the time range being analyzed
- Verify timestamp parsing is working correctly
- Ensure signals are properly categorized as Buy or Sell

## Integration with Workflow

This script is part of the complete signal extraction and analysis pipeline:

1. **Download images** from Discord → `spx-realtime-aws/`
2. **Remove duplicates** → `spx-realtime-aws-clean/`
3. **Extract signals** → `Desktop/SPXsignal/{date}.csv` (see [README_EXTRACT_SIGNALS.md](README_EXTRACT_SIGNALS.md))
4. **Fetch prices** → Add `fPrice` column (see [README_FETCH_SPX_PRICES.md](README_FETCH_SPX_PRICES.md))
5. **Merge risk levels** → Add `risk` column (see [README_EXTRACT_RISK.md](README_EXTRACT_RISK.md))
6. **Analyze statistics** → This script ✨

## Example Visualizations

### Signal Time Distribution
The overall signal distribution chart shows buy and sell signals side-by-side with the x-axis as the separation line. This visualization helps identify:
- Peak trading activity times
- Buy vs sell signal patterns throughout the day
- Time periods with higher signal frequency

### Buy/Sell Distributions
Individual histograms for buy and sell signals help identify:
- Preferred times for buy signals
- Preferred times for sell signals
- Patterns in signal timing
- Potential market behavior insights

## Notes

- The script filters signals to trading hours (9:30 AM - 4:00 PM) automatically
- Timestamps are parsed flexibly to handle different CSV formats
- Statistics are calculated only for days with valid signal data
- Histograms use 15-minute bins for detailed time-of-day analysis
- The overall signal histogram uses a unique visualization with buy signals below and sell signals above the x-axis

