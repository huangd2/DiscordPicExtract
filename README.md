# DiscordPicExtract

A tool for extracting pictures from Discord channels with time-based filtering.

## Description

This project allows you to extract images from Discord channels within a specified time frame. It downloads all images (from attachments, embeds, and message content) from a Discord channel and saves them to a local directory with organized filenames.

## Features

- Download images from Discord channels
- Filter by time frame (e.g., last 14 days)
- Extract images from message attachments, embeds, and URLs
- Skip already downloaded files
- Organized file naming with timestamps
- Rate limiting and error handling

## Important Warning

⚠️ **This tool uses Discord user tokens (self-bot), which violates Discord's Terms of Service.** Use at your own risk. This is intended for personal use only. Discord may suspend or ban accounts that use self-bots.

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord account
- Access to the Discord channel you want to download from

### Installation

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

## Usage

### Basic Usage

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

### Example

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

## Configuration

You can modify default settings in `config.py`:
- `DEFAULT_DAYS`: Default number of days to look back (default: 14)
- `DEFAULT_OUTPUT_DIR`: Default output directory (default: `spx-realtime-aws`)
- `MAX_RETRIES`: Maximum retry attempts for failed requests (default: 3)
- `RATE_LIMIT_DELAY`: Delay between requests in seconds (default: 1)

## Troubleshooting

### "Could not find channel" Error
- Make sure you're using the correct channel ID or name
- If using channel name, ensure the guild name is correct
- Verify you have access to the channel

### Rate Limiting
- The script automatically handles rate limiting with delays
- If you encounter frequent rate limits, increase `RATE_LIMIT_DELAY` in `config.py`

### Token Issues
- Ensure your token is valid and not expired
- Make sure the token is correctly formatted in the `.env` file (no extra spaces or quotes)

### No Images Downloaded
- Check that the channel has messages with images in the specified time frame
- Verify the channel ID/name is correct
- Check that you have permission to view the channel

## Complete Workflow

This project provides a complete pipeline for downloading, cleaning, organizing, and extracting signals from Discord images:

1. **Download images** from Discord channel → `spx-realtime-aws/`
2. **Remove duplicates** → `spx-realtime-aws-clean/`
3. **Extract one image per day** → `spx-clean-1perDay/`
4. **Extract buy/sell signals** → `Desktop/SPXsignal/{date}.csv` (see [Signal Extraction](#signal-extraction))

### Step-by-Step Workflow

#### Step 1: Download Images from Discord

```bash
python main.py
```

This downloads all images from the specified Discord channel to `spx-realtime-aws/` directory.

#### Step 2: Remove Duplicate Images

```bash
python deduplicate_images.py --source spx-realtime-aws --output spx-realtime-aws-clean
```

This creates a clean version in `spx-realtime-aws-clean/` with duplicates removed.

#### Step 3: Extract One Image Per Day

```bash
python extract_one_per_day.py --source spx-realtime-aws-clean --output spx-clean-1perDay
```

This extracts the last image of each day to `spx-clean-1perDay/` directory.

#### Step 4: Extract Buy/Sell Signals (Optional)

```bash
python extract_signals.py --folder spx-realtime-aws-clean --date 2025-02-14
```

This extracts buy/sell signals from chart images and saves to `Desktop/SPXsignal/{date}.csv`.

For detailed documentation, see [README_EXTRACT_SIGNALS.md](README_EXTRACT_SIGNALS.md).

#### Step 5: Quality Check (Optional)

```bash
python check_unique_dates.py
```

This verifies that all three folders have the same date coverage.

## Duplicate Image Detection

The project includes a deduplication tool (`deduplicate_images.py`) to identify and remove duplicate images from downloaded collections.

### Features

- **Content-based duplicate detection**: Uses perceptual hashing (pHash) to identify visually identical images
- **Date-restricted comparison**: Only compares images from the same date to avoid false positives
- **File size verification**: Combines hash and file size to ensure accurate duplicate detection
- **Timestamp analysis**: Provides detailed statistics on duplicate patterns

### Usage

```bash
python deduplicate_images.py --source spx-realtime-aws --output spx-realtime-aws-clean
```

**Arguments:**
- `--source`: Source directory containing images (default: `spx-realtime-aws`)
- `--output`: Output directory for unique images (default: `spx-realtime-aws-clean`)

### Duplicate Detection Logic

The deduplication algorithm uses a two-stage approach:

1. **Date Grouping**: Images are first grouped by date (extracted from filename format `YYYY-MM-DD_HH-MM-SS_...`)
   - Only images from the same date are compared
   - This prevents false positives where different images from different dates might have similar content

2. **Duplicate Identification**: Within each date group, duplicates are identified using:
   - **Perceptual Hash (pHash)**: Calculates a hash based on image content
   - **File Size**: Additional verification to ensure files are truly identical
   - Files are considered duplicates only if they have **both** the same hash **and** the same file size

3. **Selection Strategy**: For each duplicate group, the file with the earliest timestamp is kept, and all others are marked for removal.

### Output Statistics

The script provides comprehensive statistics:

#### Deduplication Summary
- Total images scanned
- Unique images copied
- Duplicates skipped
- Number of duplicate groups found

#### Timestamp Difference Statistics

For quality checking purposes, the script analyzes the time differences between removed duplicates and their kept counterparts:

- **Total pairs calculated**: Number of duplicate pairs analyzed
- **Mean difference**: Average time difference between duplicates
- **Median difference**: Middle value of time differences
- **Standard deviation**: Measure of variation in time differences
- **Minimum/Maximum difference**: Range of time differences observed
- **Percentiles** (25th, 75th, 90th, 95th): Distribution of time differences

#### Outlier Detection

Files with timestamp differences above the 95th percentile are listed separately, sorted by difference (largest first). This helps identify:
- Unusual duplicate patterns
- Potential server issues causing delayed re-uploads
- Cases where duplicates occurred with longer time gaps

### Example Output

```
============================================================
Deduplication Summary:
  Total images scanned: 3937
  Unique images copied: 2375
  Duplicates skipped: 1562
  Duplicate groups found: 1512
============================================================

======================================================================
Timestamp Difference Statistics (Removed vs Kept Duplicates)
======================================================================
Total pairs calculated:     1,562
Mean difference:            1.1m (63.2s)
Median difference:          1.0m (60.0s)
Standard deviation:         13.6s
Minimum difference:         36.0s
Maximum difference:         3.1m (186.0s)
25th percentile:           59.0s
75th percentile:           62.0s
90th percentile:           75.0s
95th percentile:           91.0s
======================================================================

Files with timestamp difference above 95th percentile (1.5m (91.0s)):
Total: 76 files
...
```

### Quality Check Insights

The timestamp statistics help identify:
- **Typical duplicate pattern**: Most duplicates occur ~1 minute apart (median: 60 seconds)
- **Server issues**: Consistent ~1 minute gaps suggest automated retry mechanisms
- **Outliers**: Files with differences >95th percentile may indicate different issues
- **Data integrity**: Ensures no unique images are incorrectly removed

## Extract One Image Per Day

The `extract_one_per_day.py` script extracts the last (most recent) image for each unique date from a source directory.

### Usage

```bash
python extract_one_per_day.py --source spx-realtime-aws-clean --output spx-clean-1perDay
```

**Arguments:**
- `--source`: Source directory containing images (default: `spx-realtime-aws-clean`)
- `--output`: Output directory for one-per-day images (default: `spx-clean-1perDay`)

### How It Works

1. Scans all images in the source directory
2. Groups images by date (extracted from filename: `YYYY-MM-DD_HH-MM-SS_...`)
3. For each date, selects the image with the latest timestamp
4. Copies the selected images to the output directory

### Example Output

```
Scanning images in: spx-realtime-aws-clean
Found 2375 image files
Grouped images into 207 dates
Extracting last image per day...
  Processing 2025-02-14: 12 images, selected 2025-02-14_20-31-00_images_SPX-liqtest.png
  Processing 2025-02-18: 8 images, selected 2025-02-18_20-55-48_images_SPX-liqtest.png
  ...
Extracted 207 images (one per day)
Results saved to: spx-clean-1perDay
```

## Quality Check

The `check_unique_dates.py` script verifies date coverage across all three folders.

### Usage

```bash
python check_unique_dates.py
```

This script:
- Counts unique dates in each folder (`spx-realtime-aws`, `spx-realtime-aws-clean`, `spx-clean-1perDay`)
- Compares date coverage between folders
- Identifies any missing dates

### Example Output

```
======================================================================
Unique Dates Analysis
======================================================================

Analyzing: spx-realtime-aws
  Found 207 unique dates
  Date range: 2025-02-14 to 2025-12-11

Analyzing: spx-realtime-aws-clean
  Found 207 unique dates
  Date range: 2025-02-14 to 2025-12-11

Analyzing: spx-clean-1perDay
  Found 207 unique dates
  Date range: 2025-02-14 to 2025-12-11

======================================================================
Summary:
======================================================================
  spx-realtime-aws              :  207 unique dates
  spx-realtime-aws-clean         :  207 unique dates
  spx-clean-1perDay              :  207 unique dates
======================================================================
```

## Timestamp Quality Check and Adjustment

The `quality_check_timestamps.py` script provides comprehensive quality checking and interactive timestamp adjustment capabilities for downloaded images.

### Features

- **Quality Check**: Identifies files with timestamps outside US EST trading hours (09:30:00 to 16:00:00)
- **Date Analysis**: Lists all dates when outside trading hours occurred
- **Gap Detection**: Identifies missing dates between first and last outside trading hour timestamps (only counting dates with files)
- **Time Distribution**: Creates a histogram plot showing the distribution of timestamps outside trading hours
- **Interactive Adjustment**: Allows period-based timestamp adjustments with user prompts
- **Post-Adjustment Verification**: Automatically re-checks all folders after adjustments

### Usage

#### Basic Quality Check

```bash
python quality_check_timestamps.py
```

Or check a specific folder:

```bash
python quality_check_timestamps.py --folder spx-realtime-aws
```

#### Interactive Timestamp Adjustment

After running the quality check, the script will prompt you to adjust timestamps if any files are found outside trading hours:

1. **Choose to adjust**: Answer "Yes" or "No" when prompted
2. **Specify periods**: Enter how many time periods need adjustment
3. **For each period**:
   - Enter start date (format: `yyyy-mm-dd`)
   - Enter end date (format: `yyyy-mm-dd`)
   - Enter hours to add (can be negative to subtract)
4. **Automatic application**: Adjustments are applied to all 3 folders automatically
5. **Verification**: Post-adjustment quality check runs automatically

### Example Output

#### Quality Check Results

```
============================================================
Quality Check: Timestamps Outside Trading Hours
Checking folder: spx-realtime-aws-clean
Trading hours: 09:30:00 to 16:00:00 (US EST)
============================================================

Displaying first 5 and last 5 of 315 file(s) outside trading hours:
------------------------------------------------------------
First 5 files:
  2025-03-10_08-38-27_images_SPX-liqtest.png (time: 08:38:27)
  2025-03-10_08-52-30_images_SPX-liqtest.png (time: 08:52:30)
  2025-03-10_09-14-30_images_SPX-liqtest.png (time: 09:14:30)
  2025-03-11_08-36-25_images_SPX-liqtest.png (time: 08:36:25)
  2025-03-11_09-04-27_images_SPX-liqtest.png (time: 09:04:27)

... (305 files omitted) ...

Last 5 files:
  2025-10-24_09-27-48_images_SPX-liqtest.png (time: 09:27:48)
  2025-10-27_09-18-54_images_SPX-liqtest.png (time: 09:18:54)
  2025-10-28_08-56-51_images_SPX-liqtest.png (time: 08:56:51)
  2025-10-29_09-20-50_images_SPX-liqtest.png (time: 09:20:50)
  2025-10-30_09-18-54_images_SPX-liqtest.png (time: 09:18:54)
------------------------------------------------------------

Dates when outside trading hours occurred (160 unique date(s)):
------------------------------------------------------------
  2025-03-10
  2025-03-11
  ...
  2025-10-30
------------------------------------------------------------

Missing dates between first (2025-03-10) and last (2025-10-30) outside trading hour timestamps:
Found 4 date(s) with files but no outside trading hour timestamps:
------------------------------------------------------------
  2025-06-05
  2025-10-08
  2025-10-21
  2025-10-23
------------------------------------------------------------

This indicates the outside trading hours occurred in MULTIPLE periods (not continuous).

============================================================
QUALITY CHECK REMINDER
============================================================
IMPORTANT: Please manually check timestamps on dates around the first and last
outside trading hour occurrences for quality assurance purposes.

First date with outside trading hours: 2025-03-10
Last date with outside trading hours: 2025-10-30

Please manually verify timestamps on:
  - A few days BEFORE the first date (around 2025-03-07 to 2025-03-10)
  - A few days AFTER the last date (around 2025-10-30 to 2025-11-02)

REASON: The timestamps represent when signals occurred. If signals don't occur
until later in the day, timezone issues might not be visible in the data.
Manual verification of dates around the boundaries helps ensure no timezone
adjustment issues were missed due to signal timing.
============================================================

Distribution of timestamps outside trading hours by hour of day (EST):
------------------------------------------------------------
  08:00 - 187 file(s)
  09:00 - 128 file(s)
------------------------------------------------------------

Saved time-of-day distribution plot to: outside_trading_hours_distribution.png

Total: 315 file(s) outside trading hours
Total: 160 unique date(s) with files outside trading hours
Total: 2 hour bucket(s) with files outside trading hours
Total: 4 missing date(s) in the period range
============================================================
```

#### Distribution Plot

The script generates a histogram plot saved as `outside_trading_hours_distribution.png` showing the distribution of timestamps outside trading hours by hour of day.

#### Interactive Adjustment Example

```
============================================================
Timestamp Adjustment
============================================================

Do you want to adjust timestamps? (Yes/No): Yes

How many periods need to change? 2

--- Period 1 ---
Period 1 start date (yyyy-mm-dd): 2025-03-10
Period 1 end date (yyyy-mm-dd): 2025-03-15
Add how many hours? (can be negative to subtract): -5

Adjusting timestamps for period 1:
  Date range: 2025-03-10 to 2025-03-15
  Hours to add: -5
  Folders: spx-realtime-aws, spx-realtime-aws-clean, spx-clean-1perDay
  spx-realtime-aws: 45 renamed, 3892 skipped
  spx-realtime-aws-clean: 23 renamed, 2352 skipped
  spx-clean-1perDay: 0 renamed, 207 skipped

Period 1 summary: 68 files renamed across all folders

--- Period 2 ---
Period 2 start date (yyyy-mm-dd): 2025-10-25
Period 2 end date (yyyy-mm-dd): 2025-10-30
Add how many hours? (can be negative to subtract): -3
...

============================================================
Timestamp adjustment completed!
============================================================

============================================================
Post-Adjustment Quality Check
============================================================
Running quality check on all 3 folders to verify adjustments...

Checking folder: spx-realtime-aws
------------------------------------------------------------
  ⚠ spx-realtime-aws: 7 file(s) outside trading hours
     7 unique date(s) with files outside trading hours

Checking folder: spx-realtime-aws-clean
------------------------------------------------------------
  ⚠ spx-realtime-aws-clean: 7 file(s) outside trading hours
     7 unique date(s) with files outside trading hours

Checking folder: spx-clean-1perDay
------------------------------------------------------------
  ✓ spx-clean-1perDay: All files are within trading hours

============================================================
Post-Adjustment Summary
============================================================
spx-realtime-aws:
  Files outside trading hours: 7
  Unique dates: 7
  Dates: 2025-05-14, 2025-06-16, 2025-07-03, 2025-07-10, 2025-07-30, 2025-09-24, 2025-10-24

spx-realtime-aws-clean:
  Files outside trading hours: 7
  Unique dates: 7
  Dates: 2025-05-14, 2025-06-16, 2025-07-03, 2025-07-10, 2025-07-30, 2025-09-24, 2025-10-24

spx-clean-1perDay:
  Files outside trading hours: 0
  Unique dates: 0

Overall Summary:
  Total files outside trading hours across all folders: 14
  Total unique dates with files outside trading hours: 7
  All dates: 2025-05-14, 2025-06-16, 2025-07-03, 2025-07-10, 2025-07-30, 2025-09-24, 2025-10-24
============================================================
```

### What It Checks

1. **Trading Hours Compliance**: Identifies files with timestamps before 09:30:00 or after 16:00:00 (US EST)
2. **Date Coverage**: Lists all unique dates when outside trading hours occurred
3. **Gap Analysis**: Finds missing dates (with files) between first and last outside trading hour timestamps
4. **Time Distribution**: Creates a histogram showing when outside trading hours occur most frequently

### Adjustment Features

- **Period-based**: Adjust multiple time periods independently
- **Date Range**: Specify start and end dates for each period
- **Hour Adjustment**: Add or subtract hours (use negative numbers to subtract)
- **Automatic Application**: Applies to all 3 folders simultaneously
- **Day Rollover Handling**: Automatically handles hour adjustments that cross midnight
- **Safety Checks**: Skips files if target filename already exists

### Use Cases

- **Timezone Correction**: Fix timestamps that are offset due to timezone issues
- **Quality Assurance**: Verify all timestamps are within expected trading hours
- **Data Validation**: Identify patterns in timestamp issues
- **Selective Adjustment**: Adjust specific date ranges that need correction

## Timestamp Adjustment Tools

### Bulk Timestamp Adjustment

The `adjust_timestamps.py` script provides a simple way to adjust timestamps across all files by subtracting a fixed number of hours.

#### Usage

```bash
python adjust_timestamps.py
```

Or with custom folders:

```bash
python adjust_timestamps.py --folders spx-realtime-aws spx-realtime-aws-clean spx-clean-1perDay
```

**Dry Run Mode** (preview changes without applying):

```bash
python adjust_timestamps.py --dry-run
```

#### Example

This script was used to subtract 5 hours from all timestamps to correct a timezone offset:

```bash
python adjust_timestamps.py
```

**Output:**
```
============================================================
File Timestamp Adjustment Script
Subtracting 5 hours from hour component in filenames
============================================================

Processing folder: spx-realtime-aws
Mode: RENAME
------------------------------------------------------------
  RENAMED: 2025-02-14_14-37-02_images_SPX-liqtest.png -> 2025-02-14_09-37-02_images_SPX-liqtest.png
  RENAMED: 2025-02-14_14-59-00_images_SPX-liqtest.png -> 2025-02-14_09-59-00_images_SPX-liqtest.png
  ...
Summary for spx-realtime-aws:
  Renamed: 3937
  Skipped: 0

...

============================================================
Overall Summary:
  Total renamed: 6519
  Total skipped: 0
============================================================
```

### Specific Timestamp Adjustment

The `adjust_specific_timestamp.py` script allows targeted adjustments for specific dates and time conditions. This script is typically used for one-off corrections.

**Note**: This script is designed for manual, case-by-case adjustments and should be modified for each specific use case.

## Project Structure

```
DiscordPicExtract/
├── main.py                    # Main script entry point
├── discord_downloader.py       # Core downloader implementation
├── deduplicate_images.py       # Duplicate detection and removal tool
├── extract_one_per_day.py     # Extract last image per day
├── check_unique_dates.py      # Quality check for date coverage
├── quality_check_timestamps.py # Timestamp quality check and adjustment
├── adjust_timestamps.py        # Bulk timestamp adjustment tool
├── adjust_specific_timestamp.py # Specific timestamp adjustment (manual use)
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .env.example               # Example environment file
├── .env                       # Your actual token (not in git)
├── spx-realtime-aws/          # Downloaded images (created automatically)
├── spx-realtime-aws-clean/    # Deduplicated images (created by deduplicate_images.py)
├── spx-clean-1perDay/         # One image per day (created by extract_one_per_day.py)
└── outside_trading_hours_distribution.png # Distribution plot (generated by quality_check_timestamps.py)
```

## License

Add your license information here.

