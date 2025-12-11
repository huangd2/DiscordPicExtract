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

## Project Structure

```
DiscordPicExtract/
├── main.py                 # Main script entry point
├── discord_downloader.py   # Core downloader implementation
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── .env                  # Your actual token (not in git)
└── spx-realtime-aws/     # Output directory (created automatically)
```

## License

Add your license information here.

