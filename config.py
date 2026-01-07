"""Configuration management for Discord Image Downloader."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Configuration
DISCORD_USER_TOKEN = os.getenv("DISCORD_USER_TOKEN", "")

# Default Settings
DEFAULT_DAYS = 365
DEFAULT_OUTPUT_DIR = Path("spx-realtime-aws")

# Discord API Configuration
DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_CDN_BASE = "https://cdn.discordapp.com"

# Rate Limiting
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
RATE_LIMIT_DELAY = 1.5  # seconds between requests (increased for safety with large downloads)

def get_output_dir() -> Path:
    """Get the output directory, creating it if it doesn't exist."""
    output_dir = Path(DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def validate_token() -> bool:
    """Validate that a Discord token is provided."""
    return bool(DISCORD_USER_TOKEN)

