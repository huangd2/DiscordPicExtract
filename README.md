# DiscordPicExtract

A tool for extracting pictures from Discord channels with time-based filtering, and comprehensive SPX trading strategy backtest analysis.

## Projects in This Repository

This repository contains two main projects:

1. **Discord Image Extraction** - Download and process images from Discord channels
2. **SPX Trading Strategy Backtest** - Backtest analysis of trading strategies based on SPX signals

---

## Project 1: Discord Image Extraction

A tool for extracting pictures from Discord channels with time-based filtering.

### Description

This project allows you to extract images from Discord channels within a specified time frame. It downloads all images (from attachments, embeds, and message content) from a Discord channel and saves them to a local directory with organized filenames.

### Features

- Download images from Discord channels
- Filter by time frame (e.g., last 14 days)
- Extract images from message attachments, embeds, and URLs
- Skip already downloaded files
- Organized file naming with timestamps
- Rate limiting and error handling

### Important Warning

⚠️ **This tool uses Discord user tokens (self-bot), which violates Discord's Terms of Service.** Use at your own risk. This is intended for personal use only. Discord may suspend or ban accounts that use self-bots.

### Setup

#### Prerequisites

- Python 3.8 or higher
- A Discord account
- Access to the Discord channel you want to download from

#### Installation

1. Clone or download this repository:
   ```bash
   cd DiscordPicExtract
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Discord user token:
   - Copy `.env.example` to `.env` (or create a new `.env` file)
   - Get your Discord user token (see instructions below)
   - Add your token to the `.env` file:
     ```
     DISCORD_USER_TOKEN=your_token_here
     ```

### Getting Your Discord User Token

**Method 1: Browser Developer Tools**
1. Open Discord in your web browser (discord.com)
2. Press `F12` to open Developer Tools
3. Go to the **Network** tab
4. Send a message in any Discord channel
5. Find a request to `discord.com/api` in the network list
6. Click on it and check the **Headers** section
7. Look for the `Authorization` header - the value after "Authorization: " is your token

**Method 2: Application Data (Advanced)**
- The token is stored in your Discord application data, but accessing it directly is more complex and varies by OS.

⚠️ **Keep your token secret!** Never share it or commit it to version control. The `.env` file is already in `.gitignore`.

### Usage

#### Basic Usage

Run the script:
```bash
python main.py
```

The script will prompt you for:
1. **Discord token** (if not in `.env` file)
2. **Channel ID or name** - You can use either:
   - Channel ID (numeric, e.g., `123456789012345678`)
   - Channel name (requires guild name, e.g., `spx-realtime-aws`)
3. **Guild/Server name** (only if using channel name instead of ID)
4. **Number of days** to look back (default: 14)
5. **Output directory** (default: `spx-realtime-aws`)

#### Example

```
Enter your Discord user token: [token from .env or enter manually]
Enter channel ID or name: spx-realtime-aws
Enter guild/server name: 数学家炒美股
Enter number of days to look back (default: 14): 14
Enter output directory (press Enter for default: spx-realtime-aws): 
```

### Finding Channel ID

To find a channel ID:
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on the channel name
3. Click "Copy ID"

### Output

Images are saved to the specified directory (default: `spx-realtime-aws/`) with filenames in the format:
```
YYYY-MM-DD_HH-MM-SS_originalname.ext
```

For example: `2024-01-15_14-30-25_signal.png`

The script will:
- Skip files that already exist
- Show progress as it downloads
- Display a summary at the end (downloaded, skipped, errors)

### Configuration

You can modify default settings in `config.py`:
- `DEFAULT_DAYS`: Default number of days to look back (default: 14)
- `DEFAULT_OUTPUT_DIR`: Default output directory (default: `spx-realtime-aws`)
- `MAX_RETRIES`: Maximum retry attempts for failed requests (default: 3)
- `RATE_LIMIT_DELAY`: Delay between requests in seconds (default: 1)

### Complete Workflow

This project provides a complete pipeline for downloading, cleaning, organizing, and extracting signals from Discord images:

1. **Download images** from Discord channel → `spx-realtime-aws/`
2. **Remove duplicates** → `spx-realtime-aws-clean/`
3. **Extract one image per day** → `spx-clean-1perDay/`
4. **Extract buy/sell signals** → `Desktop/SPXsignal/{date}.csv` (see [Signal Extraction](#signal-extraction))

For detailed documentation on each step, see:
- [README_EXTRACT_SIGNALS.md](README_EXTRACT_SIGNALS.md)
- [README_EXTRACT_TRIANGLES_WITH_RISK.md](README_EXTRACT_TRIANGLES_WITH_RISK.md)
- [README_FETCH_SPX_PRICES.md](README_FETCH_SPX_PRICES.md)
- [README_ANALYZE_SIGNAL_STATISTICS.md](README_ANALYZE_SIGNAL_STATISTICS.md)

---

## Project 2: SPX Trading Strategy Backtest

A comprehensive backtest analysis of a trading strategy based on SPX (S&P 500) signals.

### Overview

This project contains:
- Backtest implementation code
- Trading signals data
- Performance analysis and visualizations
- Comprehensive backtest report

### Strategy Description

The strategy executes trades based on Buy/Sell signals with the following rules:

1. **Buy Signal:** Purchase 1 share at `fPrice` when a Buy signal with `risk='low'` occurs
2. **Sell Signal:** Sell all held shares when a Sell signal with `risk='low'` or `risk='medium'` occurs
3. **Position Management:** Positions can carry over to the next trading day
4. **Capital Constraint:** Only buy if sufficient cash is available (starting capital: $10,000)

### Files

- `backtest_strategy.py` - Main backtest implementation
- `combined_data.csv` - Combined trading signals from all trading days
- `BACKTEST_REPORT.md` - Comprehensive analysis report with findings
- Visualization PNG files (6 charts)

### Results Summary

- **Initial Capital:** $10,000.00
- **Final Value:** $10,224.69
- **Return:** 2.25%
- **Total Trades:** 187
- **Win Rate:** 79.7%

### Usage

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

### Requirements

- Python 3.x
- pandas
- matplotlib
- numpy

### See Also

See `BACKTEST_REPORT.md` for detailed analysis, findings, and visualizations.

---

## Project Structure

```
DiscordPicExtract/
├── main.py                    # Main Discord downloader entry point
├── discord_downloader.py       # Core downloader implementation
├── deduplicate_images.py       # Duplicate detection and removal tool
├── extract_one_per_day.py     # Extract last image per day
├── check_unique_dates.py      # Quality check for date coverage
├── quality_check_timestamps.py # Timestamp quality check and adjustment
├── adjust_timestamps.py        # Bulk timestamp adjustment tool
├── adjust_specific_timestamp.py # Specific timestamp adjustment (manual use)
├── extract_signals.py          # Extract buy/sell signals from images
├── extract_triangles_with_risk.py # Extract triangle patterns with risk levels
├── fetch_spx_prices.py         # Fetch SPX prices from Polygon.io API
├── analyze_signal_statistics.py # Analyze signal patterns and statistics
├── backtest_strategy.py        # SPX trading strategy backtest
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── BACKTEST_REPORT.md         # Comprehensive backtest analysis report
├── README_EXTRACT_SIGNALS.md  # Signal extraction documentation
├── README_EXTRACT_TRIANGLES_WITH_RISK.md # Triangle extraction documentation
├── README_FETCH_SPX_PRICES.md # SPX price fetching documentation
├── README_ANALYZE_SIGNAL_STATISTICS.md # Signal statistics documentation
├── .env.example               # Example environment file
├── .env                       # Your actual token (not in git)
├── spx-realtime-aws/          # Downloaded images (created automatically)
├── spx-realtime-aws-clean/    # Deduplicated images (created by deduplicate_images.py)
├── spx-clean-1perDay/         # One image per day (created by extract_one_per_day.py)
└── [various PNG visualization files]
```

## License

Add your license information here.
