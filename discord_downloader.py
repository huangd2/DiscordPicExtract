"""Core Discord image downloader implementation."""
import asyncio
import aiohttp
import aiofiles
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Dict
import re
from urllib.parse import urlparse

from config import (
    DISCORD_USER_TOKEN,
    DISCORD_API_BASE,
    DISCORD_CDN_BASE,
    get_output_dir,
    MAX_RETRIES,
    RETRY_DELAY,
    RATE_LIMIT_DELAY,
)


class DiscordImageDownloader:
    """Downloads images from a Discord channel within a specified time frame."""

    def __init__(self, token: str, output_dir: Optional[Path] = None):
        """
        Initialize the downloader.

        Args:
            token: Discord user token
            output_dir: Directory to save images (default: spx-realtime-aws)
        """
        self.token = token
        self.output_dir = output_dir or get_output_dir()
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {self.output_dir.absolute()}")
        self.session: Optional[aiohttp.ClientSession] = None
        self.downloaded_count = 0
        self.skipped_count = 0
        self.error_count = 0

    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            "Authorization": self.token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _make_request(
        self, method: str, url: str, **kwargs
    ) -> Optional[Dict]:
        """Make an HTTP request with retry logic and rate limiting."""
        for attempt in range(MAX_RETRIES):
            try:
                await asyncio.sleep(RATE_LIMIT_DELAY)
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 429:  # Rate limited
                        retry_after = int(
                            response.headers.get("Retry-After", RETRY_DELAY * 2)
                        )
                        print(f"Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        continue

                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        response.raise_for_status()

            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                raise
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                print(f"Error making request to {url}: {e}")
                return None

        return None

    async def get_guild_id(self, guild_name: str) -> Optional[int]:
        """Get guild ID from guild name."""
        url = f"{DISCORD_API_BASE}/users/@me/guilds"
        guilds = await self._make_request("GET", url)
        if not guilds:
            return None

        for guild in guilds:
            if guild.get("name") == guild_name:
                return int(guild["id"])
        return None

    async def get_channel_id(
        self, guild_id: int, channel_name: str
    ) -> Optional[int]:
        """Get channel ID from channel name within a guild."""
        url = f"{DISCORD_API_BASE}/guilds/{guild_id}/channels"
        channels = await self._make_request("GET", url)
        if not channels:
            return None

        for channel in channels:
            if channel.get("name") == channel_name:
                return int(channel["id"])
        return None

    def parse_discord_url(self, url: str) -> Optional[int]:
        """Extract channel ID from Discord URL."""
        # Pattern: https://discord.com/channels/{guild_id}/{channel_id}
        pattern = re.compile(
            r"discord\.com/channels/\d+/(\d+)",
            re.IGNORECASE
        )
        match = pattern.search(url)
        if match:
            return int(match.group(1))
        return None

    def parse_channel_input(self, channel_input: str) -> Optional[int]:
        """Parse channel input (can be URL, ID, or name)."""
        # Try to parse as Discord URL first
        channel_id = self.parse_discord_url(channel_input)
        if channel_id:
            return channel_id
        
        # Try to parse as ID
        try:
            return int(channel_input)
        except ValueError:
            return None

    async def resolve_channel(
        self, channel_input: str, guild_name: Optional[str] = None
    ) -> Optional[int]:
        """
        Resolve channel from input (ID or name).

        Args:
            channel_input: Channel ID (as string) or channel name
            guild_name: Guild name if channel_input is a name

        Returns:
            Channel ID or None if not found
        """
        # Try as ID first
        channel_id = self.parse_channel_input(channel_input)
        if channel_id:
            # Verify channel exists
            url = f"{DISCORD_API_BASE}/channels/{channel_id}"
            channel = await self._make_request("GET", url)
            if channel:
                return channel_id
            return None

        # Try as name (requires guild_name)
        if guild_name:
            guild_id = await self.get_guild_id(guild_name)
            if guild_id:
                channel_id = await self.get_channel_id(guild_id, channel_input)
                return channel_id

        return None

    def extract_image_urls(self, message: Dict) -> List[str]:
        """Extract all image URLs from a message."""
        image_urls = []

        # Check attachments
        for attachment in message.get("attachments", []):
            url = attachment.get("url")
            content_type = attachment.get("content_type", "")
            if url and (
                content_type.startswith("image/")
                or url.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
            ):
                image_urls.append(url)

        # Check embeds
        for embed in message.get("embeds", []):
            # Embed image
            if "image" in embed and "url" in embed["image"]:
                image_urls.append(embed["image"]["url"])
            # Embed thumbnail
            if "thumbnail" in embed and "url" in embed["thumbnail"]:
                image_urls.append(embed["thumbnail"]["url"])

        # Check message content for image URLs
        content = message.get("content", "")
        url_pattern = re.compile(
            r"https?://(?:cdn\.)?discord(?:app)?\.com/attachments/\d+/\d+/[^\s]+\.(?:png|jpg|jpeg|gif|webp)",
            re.IGNORECASE,
        )
        found_urls = url_pattern.findall(content)
        image_urls.extend(found_urls)

        return image_urls

    def get_filename(self, url: str, message_timestamp: str) -> str:
        """Generate a filename for the downloaded image."""
        # Parse URL to get original filename
        parsed = urlparse(url)
        original_filename = Path(parsed.path).name

        # If no extension, try to get from URL or default to .png
        if "." not in original_filename:
            original_filename = f"{original_filename}.png"

        # Parse message timestamp
        try:
            dt = datetime.fromisoformat(message_timestamp.replace("Z", "+00:00"))
        except:
            dt = datetime.now(timezone.utc)

        # Format: YYYY-MM-DD_HH-MM-SS_originalname.ext
        timestamp_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp_str}_{original_filename}"

        return filename

    async def download_image(self, url: str, filepath: Path) -> bool:
        """Download a single image."""
        if filepath.exists():
            self.skipped_count += 1
            return False

        try:
            # Ensure the directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    async with aiofiles.open(filepath, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    self.downloaded_count += 1
                    return True
                else:
                    self.error_count += 1
                    return False
        except asyncio.TimeoutError:
            self.error_count += 1
            return False
        except Exception as e:
            self.error_count += 1
            return False

    async def fetch_messages(
        self, channel_id: int, days: int, before: Optional[str] = None
    ) -> List[Dict]:
        """Fetch messages from a channel."""
        url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
        params = {"limit": 100}
        if before:
            params["before"] = before

        messages = await self._make_request("GET", url, params=params)
        return messages or []

    async def download_channel_images(
        self, channel_id: int, days: int = 365
    ) -> None:
        """
        Download all images from a channel within the last N days.

        Args:
            channel_id: Discord channel ID
            days: Number of days to look back
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        print(f"Downloading images from the last {days} days (since {cutoff_date.strftime('%Y-%m-%d %H:%M:%S UTC')})")

        all_messages = []
        before = None
        has_more = True

        # Fetch all messages in the time range
        while has_more:
            messages = await self.fetch_messages(channel_id, days, before)
            if not messages:
                break

            for message in messages:
                # Parse message timestamp
                timestamp_str = message.get("timestamp", "")
                try:
                    msg_date = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                except:
                    continue

                # Stop if we've gone past the cutoff date
                if msg_date < cutoff_date:
                    has_more = False
                    break

                all_messages.append(message)

            # Set before to the last message ID for pagination
            if messages:
                before = messages[-1]["id"]
            else:
                has_more = False

            # Small delay to avoid rate limiting (increased for safety)
            await asyncio.sleep(1.0)

        print(f"Found {len(all_messages)} messages to process")
        print(f"Starting download to: {self.output_dir.absolute()}\n")

        # Extract all image URLs first
        all_image_urls = []
        for message in all_messages:
            image_urls = self.extract_image_urls(message)
            timestamp = message.get("timestamp", "")
            for url in image_urls:
                filename = self.get_filename(url, timestamp)
                all_image_urls.append((url, filename, timestamp))

        total_images = len(all_image_urls)
        print(f"Found {total_images} images to download\n")

        # Download images with progress reporting
        for idx, (url, filename, timestamp) in enumerate(all_image_urls, 1):
            filepath = self.output_dir / filename
            was_skipped = filepath.exists()
            try:
                success = await self.download_image(url, filepath)
                if success:
                    print(f"[{idx}/{total_images}] Downloaded: {filename}")
                elif was_skipped:
                    if idx % 100 == 0:  # Only print every 100 skipped files to reduce spam
                        print(f"[{idx}/{total_images}] Skipped (exists): {filename}")
            except KeyboardInterrupt:
                print(f"\n\nDownload interrupted by user at {idx}/{total_images}")
                print(f"Last file: {filename}")
                raise
            except Exception as e:
                print(f"[{idx}/{total_images}] ERROR downloading {filename}: {e}")
                self.error_count += 1
                # Add delay after error to avoid rapid failures
                await asyncio.sleep(2)
                # Continue with next file instead of stopping
                continue

        # Print summary
        print(f"\nDownload complete!")
        print(f"  Downloaded: {self.downloaded_count}")
        print(f"  Skipped (already exists): {self.skipped_count}")
        print(f"  Errors: {self.error_count}")

