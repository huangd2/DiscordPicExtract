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

## Project Structure

```
DiscordPicExtract/
├── main.py                 # Main script entry point
├── discord_downloader.py   # Core downloader implementation
├── deduplicate_images.py   # Duplicate detection and removal tool
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── .env                  # Your actual token (not in git)
├── spx-realtime-aws/     # Output directory (created automatically)
└── spx-realtime-aws-clean/ # Deduplicated images (created by deduplicate_images.py)
```

## License

Add your license information here.

