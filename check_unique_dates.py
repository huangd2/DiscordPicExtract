"""Script to check unique dates in all three folders."""
from pathlib import Path
from typing import Set, Optional
from datetime import datetime


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


def get_unique_dates(folder_path: Path, silent: bool = False) -> Set[str]:
    """
    Get all unique dates from image files in a folder.
    
    Args:
        folder_path: Path to the folder to analyze
        silent: If True, suppress warning messages
        
    Returns:
        Set of unique date strings (YYYY-MM-DD)
    """
    if not folder_path.exists() or not folder_path.is_dir():
        return set()
    
    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    image_files = [
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    # Extract unique dates
    unique_dates = set()
    files_without_date = 0
    
    for image_file in image_files:
        date_str = parse_date_from_filename(image_file.name)
        if date_str:
            unique_dates.add(date_str)
        else:
            files_without_date += 1
    
    if files_without_date > 0 and not silent:
        print(f"  Warning: {files_without_date} files in {folder_path.name} could not be parsed for date")
    
    return unique_dates


def check_unique_dates_quality(
    folder1: Path = None,
    folder2: Path = None,
    folder3: Path = None
) -> dict:
    """
    Quality check function to count unique dates in the three folders.
    Called after folders are created and populated with pictures.
    Computes and displays the unique date counts for each folder.
    
    Args:
        folder1: Path to first folder (default: spx-realtime-aws)
        folder2: Path to second folder (default: spx-realtime-aws-clean)
        folder3: Path to third folder (default: spx-clean-1perDay)
        
    Returns:
        Dictionary with folder names as keys and number of unique dates as values.
        Example: {
            'spx-realtime-aws': 207,
            'spx-realtime-aws-clean': 207,
            'spx-clean-1perDay': 207
        }
    """
    # Default folders if not provided
    if folder1 is None:
        folder1 = Path("spx-realtime-aws")
    if folder2 is None:
        folder2 = Path("spx-realtime-aws-clean")
    if folder3 is None:
        folder3 = Path("spx-clean-1perDay")
    
    folders = [folder1, folder2, folder3]
    
    print("="*70)
    print("Quality Check: Unique Dates in Folders")
    print("="*70)
    print()
    
    # Get unique dates for each folder and display results
    results = {}
    for folder in folders:
        print(f"Computing unique dates for: {folder.name}")
        unique_dates = get_unique_dates(folder, silent=True)
        count = len(unique_dates)
        results[folder.name] = count
        print(f"  -> Found {count} unique dates")
        if unique_dates:
            sorted_dates = sorted(unique_dates)
            print(f"  -> Date range: {sorted_dates[0]} to {sorted_dates[-1]}")
        print()
    
    # Print summary
    print("="*70)
    print("Summary:")
    print("="*70)
    for folder_name, count in results.items():
        print(f"  {folder_name:30s}: {count:4d} unique dates")
    print("="*70)
    print()
    
    return results


def main():
    """Main function to check unique dates in all three folders."""
    folders = [
        Path("spx-realtime-aws"),
        Path("spx-realtime-aws-clean"),
        Path("spx-clean-1perDay")
    ]
    
    print("="*70)
    print("Unique Dates Analysis")
    print("="*70)
    print()
    
    results = {}
    
    for folder in folders:
        print(f"Analyzing: {folder.name}")
        unique_dates = get_unique_dates(folder)
        results[folder.name] = unique_dates
        print(f"  Found {len(unique_dates)} unique dates")
        if unique_dates:
            sorted_dates = sorted(unique_dates)
            print(f"  Date range: {sorted_dates[0]} to {sorted_dates[-1]}")
        print()
    
    # Print summary
    print("="*70)
    print("Summary:")
    print("="*70)
    for folder_name, dates in results.items():
        print(f"  {folder_name:30s}: {len(dates):4d} unique dates")
    
    # Find dates that are in one folder but not others
    print()
    print("="*70)
    print("Date Coverage Comparison:")
    print("="*70)
    
    all_dates = set()
    for dates in results.values():
        all_dates.update(dates)
    
    if all_dates:
        sorted_all_dates = sorted(all_dates)
        print(f"Total unique dates across all folders: {len(all_dates)}")
        print(f"Overall date range: {sorted_all_dates[0]} to {sorted_all_dates[-1]}")
        print()
        
        # Check which dates are missing from each folder
        for folder_name, dates in results.items():
            missing = all_dates - dates
            if missing:
                sorted_missing = sorted(missing)
                print(f"{folder_name}: Missing {len(missing)} dates")
                if len(missing) <= 20:
                    print(f"  Missing dates: {', '.join(sorted_missing)}")
                else:
                    print(f"  Missing dates (first 20): {', '.join(sorted_missing[:20])}...")
            else:
                print(f"{folder_name}: Contains all dates")
            print()


if __name__ == "__main__":
    main()

