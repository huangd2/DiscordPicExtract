"""Main entry point for Discord Image Downloader."""
import asyncio
import sys
import re
import argparse
from pathlib import Path
from config import DISCORD_USER_TOKEN, validate_token, DEFAULT_DAYS
from discord_downloader import DiscordImageDownloader


async def main(channel_input=None, days=None, output_dir=None, guild_name=None):
    """Main function to run the Discord image downloader."""
    # Get token
    token = DISCORD_USER_TOKEN
    if not token:
        token = input("Enter your Discord user token: ").strip()
        if not token:
            print("Error: Discord token is required")
            sys.exit(1)

    # Get channel input
    if not channel_input:
        channel_input = input("Enter channel URL, ID, or name: ").strip()
        if not channel_input:
            print("Error: Channel URL, ID, or name is required")
            sys.exit(1)

    # Check if it's a Discord URL (extract channel ID directly)
    if not guild_name:
        url_pattern = re.compile(r"discord\.com/channels/\d+/(\d+)", re.IGNORECASE)
        if url_pattern.search(channel_input):
            # It's a URL, we can extract channel ID directly, no need for guild name
            pass
        else:
            # Check if it's a numeric ID
            try:
                int(channel_input)  # If it's a number, it's an ID
            except ValueError:
                # It's a name, need guild name
                guild_name = input(
                    "Enter guild/server name (required when using channel name): "
                ).strip()
                if not guild_name:
                    print("Error: Guild name is required when using channel name")
                    sys.exit(1)

    # Get days
    if days is None:
        days_input = input(f"Enter number of days to look back (default: {DEFAULT_DAYS}): ").strip()
        days = DEFAULT_DAYS
        if days_input:
            try:
                days = int(days_input)
                if days <= 0:
                    print("Error: Days must be a positive number")
                    sys.exit(1)
            except ValueError:
                print("Error: Invalid number of days")
                sys.exit(1)

    # Get output directory (optional)
    if output_dir is None:
        output_dir_input = input(
            "Enter output directory (press Enter for default: spx-realtime-aws): "
        ).strip()
        output_dir = Path("spx-realtime-aws")
        if output_dir_input:
            output_dir = Path(output_dir_input)
    else:
        output_dir = Path(output_dir)

    # Run downloader
    async with DiscordImageDownloader(token, output_dir) as downloader:
        # Resolve channel
        print(f"Resolving channel: {channel_input}")
        channel_id = await downloader.resolve_channel(channel_input, guild_name)
        if not channel_id:
            print(f"Error: Could not find channel '{channel_input}'")
            sys.exit(1)

        print(f"Found channel ID: {channel_id}")
        print(f"Output directory: {output_dir.absolute()}")

        # Download images
        await downloader.download_channel_images(channel_id, days)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from a Discord channel")
    parser.add_argument(
        "--channel",
        type=str,
        help="Channel URL, ID, or name"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Number of days to look back (default: {DEFAULT_DAYS})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="spx-realtime-aws",
        help="Output directory (default: spx-realtime-aws)"
    )
    parser.add_argument(
        "--guild",
        type=str,
        help="Guild/server name (required when using channel name)"
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(
            channel_input=args.channel,
            days=args.days,
            output_dir=args.output,
            guild_name=args.guild
        ))
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

