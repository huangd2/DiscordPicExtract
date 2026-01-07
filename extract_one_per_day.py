"""Script to extract the last picture of every day from the clean folder."""
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def parse_timestamp_from_filename(filename: str) -> Optional[datetime]:
    """Parse timestamp from filename format: YYYY-MM-DD_HH-MM-SS_originalname.ext"""
    try:
        # Extract the timestamp part (first 19 characters: YYYY-MM-DD_HH-MM-SS)
        timestamp_str = filename[:19]
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        return dt
    except (ValueError, IndexError):
        return None


def parse_date_from_filename(filename: str) -> Optional[str]:
    """Parse date from filename format: YYYY-MM-DD_HH-MM-SS_originalname.ext"""
    try:
        # Extract the date part (first 10 characters: YYYY-MM-DD)
        date_str = filename[:10]
        # Validate it's a valid date format
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except (ValueError, IndexError):
        return None


def find_last_image_per_day(source_dir: Path) -> Dict[str, Path]:
    """
    Find the last image (by timestamp) for each day that has images.
    
    Args:
        source_dir: Directory containing images
        
    Returns:
        Dictionary mapping date strings (YYYY-MM-DD) to the path of the last image of that day
    """
    print(f"Scanning images in: {source_dir.absolute()}")
    
    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    image_files = [
        f for f in source_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    print(f"Found {len(image_files)} image files")
    
    # Group files by date
    files_by_date: Dict[str, List[Path]] = {}
    files_without_date: List[Path] = []
    
    for image_file in image_files:
        date_str = parse_date_from_filename(image_file.name)
        if date_str:
            if date_str not in files_by_date:
                files_by_date[date_str] = []
            files_by_date[date_str].append(image_file)
        else:
            files_without_date.append(image_file)
    
    print(f"Grouped images into {len(files_by_date)} dates")
    if files_without_date:
        print(f"Warning: {len(files_without_date)} files could not be parsed for date")
    
    # Find the last image (by timestamp) for each date
    last_image_per_day: Dict[str, Path] = {}
    
    for date_str, date_files in files_by_date.items():
        # Parse timestamps and find the latest one
        files_with_timestamps = []
        for file in date_files:
            timestamp = parse_timestamp_from_filename(file.name)
            if timestamp:
                files_with_timestamps.append((timestamp, file))
            else:
                # If we can't parse timestamp, use file modification time as fallback
                files_with_timestamps.append((datetime.fromtimestamp(file.stat().st_mtime), file))
        
        if files_with_timestamps:
            # Sort by timestamp (latest last)
            files_with_timestamps.sort(key=lambda x: x[0])
            # Get the last one (latest timestamp)
            last_image_per_day[date_str] = files_with_timestamps[-1][1]
    
    print(f"Found last image for {len(last_image_per_day)} days")
    
    return last_image_per_day


def extract_one_per_day(source_dir: Path, output_dir: Path) -> None:
    """
    Extract the last picture of every day from the source directory.
    
    Args:
        source_dir: Directory containing images (clean folder)
        output_dir: Directory to save one image per day
    """
    if not source_dir.exists():
        print(f"Error: Source directory does not exist: {source_dir}")
        return
    
    if not source_dir.is_dir():
        print(f"Error: Source path is not a directory: {source_dir}")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}")
    
    # Find last image per day
    last_images = find_last_image_per_day(source_dir)
    
    if not last_images:
        print("\nNo images found with valid dates.")
        return
    
    
    # Copy images to output directory
    print(f"\nCopying {len(last_images)} images (one per day) to {output_dir.name}...")
    copied_count = 0
    
    # Sort by date for better output
    sorted_dates = sorted(last_images.keys())
    
    for date_str in sorted_dates:
        image_file = last_images[date_str]
        dest_file = output_dir / image_file.name
        try:
            shutil.copy2(image_file, dest_file)
            copied_count += 1
            if copied_count % 10 == 0:
                print(f"  Copied {copied_count} files...")
        except Exception as e:
            print(f"  Error copying {image_file.name}: {e}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("Extraction Summary:")
    print(f"  Total days with images: {len(last_images)}")
    print(f"  Images copied: {copied_count}")
    print(f"  Date range: {sorted_dates[0]} to {sorted_dates[-1]}")
    print(f"{'='*60}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract the last picture of every day from the clean folder"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Source directory containing images (default: checks 'clean' then 'spx-realtime-aws-clean')"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="spx-clean-1perDay",
        help="Output directory for one image per day (default: spx-clean-1perDay)"
    )
    
    args = parser.parse_args()
    
    # Determine source directory
    if args.source:
        source_dir = Path(args.source)
    else:
        # Try "clean" first, then "spx-realtime-aws-clean"
        clean_dir = Path("clean")
        spx_clean_dir = Path("spx-realtime-aws-clean")
        
        if clean_dir.exists() and clean_dir.is_dir():
            source_dir = clean_dir
            print(f"Using 'clean' folder as source")
        elif spx_clean_dir.exists() and spx_clean_dir.is_dir():
            source_dir = spx_clean_dir
            print(f"Using 'spx-realtime-aws-clean' folder as source")
        else:
            print(f"Error: Neither 'clean' nor 'spx-realtime-aws-clean' directory found.")
            print(f"Please specify --source or create one of these directories.")
            return
    
    output_dir = Path(args.output)
    
    extract_one_per_day(source_dir, output_dir)


if __name__ == "__main__":
    main()

