"""Script to adjust file timestamps by subtracting 5 hours from the hour component."""
import re
from pathlib import Path
from datetime import datetime, timedelta


def adjust_hour_in_filename(filename: str) -> str:
    """
    Adjust the hour component in filename by subtracting 5 hours.
    
    Format: YYYY-MM-DD_HH-MM-SS_originalname.ext
    Example: 2025-02-14_14-37-02_images_SPX-liqtest.png -> 2025-02-14_09-37-02_images_SPX-liqtest.png
    
    Args:
        filename: Original filename with timestamp
        
    Returns:
        New filename with adjusted hour, or original filename if pattern doesn't match
    """
    # Pattern to match: YYYY-MM-DD_HH-MM-SS_...
    pattern = r'^(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})_(.+)$'
    match = re.match(pattern, filename)
    
    if not match:
        # If pattern doesn't match, return original filename
        return filename
    
    date_str = match.group(1)  # YYYY-MM-DD
    hour_str = match.group(2)  # HH
    minute_str = match.group(3)  # MM
    second_str = match.group(4)  # SS
    rest = match.group(5)  # originalname.ext
    
    # Parse the hour
    try:
        hour = int(hour_str)
    except ValueError:
        return filename
    
    # Subtract 5 hours
    new_hour = hour - 5
    
    # Handle day rollover if hour becomes negative
    if new_hour < 0:
        new_hour += 24
        # Adjust the date by subtracting one day
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_obj = date_obj - timedelta(days=1)
            date_str = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            # If date parsing fails, just use the original date
            pass
    
    # Format the new hour as two digits
    new_hour_str = f"{new_hour:02d}"
    
    # Reconstruct the filename
    new_filename = f"{date_str}_{new_hour_str}-{minute_str}-{second_str}_{rest}"
    
    return new_filename


def rename_files_in_folder(folder_path: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Rename all files in a folder by adjusting their timestamps.
    
    Args:
        folder_path: Path to the folder containing files
        dry_run: If True, only print what would be renamed without actually renaming
        
    Returns:
        Tuple of (files_renamed, files_skipped)
    """
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Warning: {folder_path} does not exist or is not a directory")
        return 0, 0
    
    files_renamed = 0
    files_skipped = 0
    
    print(f"\nProcessing folder: {folder_path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'RENAME'}")
    print("-" * 60)
    
    # Get all files in the folder
    all_files = list(folder_path.iterdir())
    image_files = [f for f in all_files if f.is_file()]
    
    for file_path in image_files:
        old_name = file_path.name
        new_name = adjust_hour_in_filename(old_name)
        
        if old_name == new_name:
            # Filename doesn't match pattern or doesn't need adjustment
            files_skipped += 1
            continue
        
        new_path = file_path.parent / new_name
        
        # Check if target file already exists
        if new_path.exists():
            print(f"  SKIP: {old_name} -> {new_name} (target already exists)")
            files_skipped += 1
            continue
        
        if dry_run:
            print(f"  WOULD RENAME: {old_name} -> {new_name}")
        else:
            try:
                file_path.rename(new_path)
                print(f"  RENAMED: {old_name} -> {new_name}")
                files_renamed += 1
            except Exception as e:
                print(f"  ERROR renaming {old_name}: {e}")
                files_skipped += 1
    
    print(f"\nSummary for {folder_path.name}:")
    print(f"  Renamed: {files_renamed}")
    print(f"  Skipped: {files_skipped}")
    
    return files_renamed, files_skipped


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Adjust file timestamps by subtracting 5 hours from hour component"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming files"
    )
    parser.add_argument(
        "--folders",
        nargs="+",
        default=["spx-realtime-aws", "spx-realtime-aws-clean", "spx-clean-1perDay"],
        help="Folders to process (default: spx-realtime-aws spx-realtime-aws-clean spx-clean-1perDay)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("File Timestamp Adjustment Script")
    print("Subtracting 5 hours from hour component in filenames")
    print("=" * 60)
    
    total_renamed = 0
    total_skipped = 0
    
    for folder_name in args.folders:
        folder_path = Path(folder_name)
        renamed, skipped = rename_files_in_folder(folder_path, dry_run=args.dry_run)
        total_renamed += renamed
        total_skipped += skipped
    
    print("\n" + "=" * 60)
    print("Overall Summary:")
    print(f"  Total renamed: {total_renamed}")
    print(f"  Total skipped: {total_skipped}")
    print("=" * 60)
    
    if args.dry_run:
        print("\nThis was a DRY RUN. No files were actually renamed.")
        print("Run without --dry-run to perform the actual renaming.")


if __name__ == "__main__":
    main()

