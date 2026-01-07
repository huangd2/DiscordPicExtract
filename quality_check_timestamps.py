"""Quality check script to verify file timestamps are within expected US EST trading hours."""
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Set, Dict


def parse_timestamp_from_filename(filename: str) -> Optional[datetime]:
    """Parse timestamp from filename format: YYYY-MM-DD_HH-MM-SS_originalname.ext"""
    try:
        # Extract the timestamp part (first 19 characters: YYYY-MM-DD_HH-MM-SS)
        timestamp_str = filename[:19]
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        return dt
    except (ValueError, IndexError):
        return None


def is_outside_trading_hours(timestamp: datetime) -> bool:
    """
    Check if timestamp is outside US EST trading hours (09:30:00 to 16:00:00).
    
    Args:
        timestamp: Datetime object to check
        
    Returns:
        True if timestamp is before 09:30:00 or after 16:00:00, False otherwise
    """
    time_only = timestamp.time()
    # Trading hours: 09:30:00 to 16:00:00
    start_time = datetime.strptime("09:30:00", "%H:%M:%S").time()
    end_time = datetime.strptime("16:00:00", "%H:%M:%S").time()
    
    return time_only < start_time or time_only > end_time


def quality_check_timestamps(folder_path: Path, silent: bool = False) -> Optional[Tuple[List[str], Set[str], Dict[int, int], List[str]]]:
    """
    Check files in folder for timestamps outside US EST trading hours (09:30:00 to 16:00:00).
    Displays filenames to screen: first 5 and last 5 if >= 10 files, all if < 10 files.
    Also extracts and displays all unique dates when outside trading hours occurred,
    computes a distribution of timestamps outside trading hours, and checks for missing dates
    between first and last outside trading hour timestamps.
    
    Args:
        folder_path: Path to the folder containing files to check
        silent: If True, suppress most output (only show errors)
        
    Returns:
        None if no files found outside trading hours, otherwise tuple of:
        (list of file names, set of dates, hour distribution dict, list of missing dates)
    """
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: {folder_path} does not exist or is not a directory")
        return None
    
    files_outside_hours: List[str] = []
    all_dates_with_files: Set[str] = set()  # All dates that have files in the folder
    
    # Get all files in the folder
    all_files = list(folder_path.iterdir())
    image_files = [f for f in all_files if f.is_file()]
    
    for file_path in image_files:
        filename = file_path.name
        timestamp = parse_timestamp_from_filename(filename)
        
        if timestamp is None:
            # Skip files that don't match the expected format
            continue
        
        # Track all dates that have files (regardless of trading hours)
        date_str = timestamp.strftime("%Y-%m-%d")
        all_dates_with_files.add(date_str)
        
        if is_outside_trading_hours(timestamp):
            files_outside_hours.append(filename)
    
    if not files_outside_hours:
        return None
    
    # Extract unique dates and hour distribution from files outside trading hours
    dates_outside_hours: Set[str] = set()
    hour_distribution: Dict[int, int] = {}
    times_outside_hours: List[datetime] = []
    for filename in files_outside_hours:
        timestamp = parse_timestamp_from_filename(filename)
        if not timestamp:
            continue
        # Date for date list
        date_str = timestamp.strftime("%Y-%m-%d")
        dates_outside_hours.add(date_str)
        # Hour bucket for distribution
        hour = timestamp.hour
        hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        # Full timestamp (used for plotting by time of day)
        times_outside_hours.append(timestamp)
    
    # Sort dates for display
    sorted_dates = sorted(dates_outside_hours)
    
    # Display filenames according to requirements
    if not silent:
        num_files = len(files_outside_hours)
        if num_files < 10:
            # Print all filenames if less than 10
            print(f"\nDisplaying all {num_files} file(s) outside trading hours:")
            print("-" * 60)
            for filename in files_outside_hours:
                timestamp = parse_timestamp_from_filename(filename)
                if timestamp:
                    time_str = timestamp.strftime("%H:%M:%S")
                    print(f"  {filename} (time: {time_str})")
        else:
            # Print first 5 and last 5 if >= 10 files
            print(f"\nDisplaying first 5 and last 5 of {num_files} file(s) outside trading hours:")
            print("-" * 60)
            print("First 5 files:")
            for filename in files_outside_hours[:5]:
                timestamp = parse_timestamp_from_filename(filename)
                if timestamp:
                    time_str = timestamp.strftime("%H:%M:%S")
                    print(f"  {filename} (time: {time_str})")
            print(f"\n... ({num_files - 10} files omitted) ...\n")
            print("Last 5 files:")
            for filename in files_outside_hours[-5:]:
                timestamp = parse_timestamp_from_filename(filename)
                if timestamp:
                    time_str = timestamp.strftime("%H:%M:%S")
                    print(f"  {filename} (time: {time_str})")
        
        print("-" * 60)
        
        # Display dates when outside trading hours occurred
        print(f"\nDates when outside trading hours occurred ({len(sorted_dates)} unique date(s)):")
        print("-" * 60)
        for date_str in sorted_dates:
            print(f"  {date_str}")
        print("-" * 60)
    
    # Check for missing dates between first and last outside trading hour timestamps
    # Only count dates that actually have files in the folder (trading days with pictures)
    missing_dates: List[str] = []
    if len(sorted_dates) > 1:
        first_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
        last_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
        
        # Generate all dates in the range
        current_date = first_date
        while current_date <= last_date:
            date_str = current_date.strftime("%Y-%m-%d")
            # Only check dates that have files in the folder
            # If a date has files but no outside trading hours, it's a missing date
            if date_str in all_dates_with_files and date_str not in dates_outside_hours:
                missing_dates.append(date_str)
            current_date += timedelta(days=1)
    
        # Display missing dates if any (only dates that have files but no outside trading hours)
        if missing_dates:
            print(f"\nMissing dates between first ({sorted_dates[0]}) and last ({sorted_dates[-1]}) outside trading hour timestamps:")
            print(f"Found {len(missing_dates)} date(s) with files but no outside trading hour timestamps:")
            print("-" * 60)
            for date_str in missing_dates:
                print(f"  {date_str}")
            print("-" * 60)
            print(f"\nThis indicates the outside trading hours occurred in MULTIPLE periods (not continuous).")
        else:
            if len(sorted_dates) > 1:
                print(f"\nNo missing dates found between first ({sorted_dates[0]}) and last ({sorted_dates[-1]}) outside trading hour timestamps.")
                print("(Only counting dates that have files in the folder)")
                print("This indicates the outside trading hours occurred in ONE CONTINUOUS period.")
            else:
                print(f"\nOnly one date found with outside trading hours, so no gap analysis needed.")
    
    # Quality check reminder (only show in non-silent mode)
    if not silent and sorted_dates:
        first_date_obj = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
        last_date_obj = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
        
        # Calculate a few days before first and after last
        days_to_check = 3
        check_before_start = (first_date_obj - timedelta(days=days_to_check)).strftime("%Y-%m-%d")
        check_after_end = (last_date_obj + timedelta(days=days_to_check)).strftime("%Y-%m-%d")
        
        print("\n" + "=" * 60)
        print("QUALITY CHECK REMINDER")
        print("=" * 60)
        print("IMPORTANT: Please manually check timestamps on dates around the first and last")
        print("outside trading hour occurrences for quality assurance purposes.")
        print()
        print(f"First date with outside trading hours: {sorted_dates[0]}")
        print(f"Last date with outside trading hours: {sorted_dates[-1]}")
        print()
        print(f"Please manually verify timestamps on:")
        print(f"  - A few days BEFORE the first date (around {check_before_start} to {sorted_dates[0]})")
        print(f"  - A few days AFTER the last date (around {sorted_dates[-1]} to {check_after_end})")
        print()
        print("REASON: The timestamps represent when signals occurred. If signals don't occur")
        print("until later in the day, timezone issues might not be visible in the data.")
        print("Manual verification of dates around the boundaries helps ensure no timezone")
        print("adjustment issues were missed due to signal timing.")
        print("=" * 60)
    
    # Display hour-of-day distribution summary
    if not silent:
        print("\nDistribution of timestamps outside trading hours by hour of day (EST):")
        print("-" * 60)
        for hour in sorted(hour_distribution.keys()):
            print(f"  {hour:02d}:00 - {hour_distribution[hour]} file(s)")
        print("-" * 60)
        
        # Try to create a histogram plot of times outside trading hours
        try:
            plot_output_path = Path("outside_trading_hours_distribution.png")
            plot_time_distribution(times_outside_hours, plot_output_path)
            print(f"\nSaved time-of-day distribution plot to: {plot_output_path}")
        except Exception as e:
            print(f"\nWarning: Could not generate distribution plot: {e}")
    
    return (files_outside_hours, dates_outside_hours, hour_distribution, missing_dates)


def adjust_hour_in_filename_for_date_range(
    filename: str, start_date: str, end_date: str, hours_to_add: int
) -> Optional[str]:
    """
    Adjust the hour component in filename by adding hours, only if the file's date is within the range.
    
    Format: YYYY-MM-DD_HH-MM-SS_originalname.ext
    
    Args:
        filename: Original filename with timestamp
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (inclusive)
        hours_to_add: Number of hours to add (can be negative to subtract)
        
    Returns:
        New filename with adjusted hour if date is in range, None if not in range, or original if pattern doesn't match
    """
    # Pattern to match: YYYY-MM-DD_HH-MM-SS_...
    pattern = r'^(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})_(.+)$'
    match = re.match(pattern, filename)
    
    if not match:
        return None
    
    date_str = match.group(1)  # YYYY-MM-DD
    hour_str = match.group(2)  # HH
    minute_str = match.group(3)  # MM
    second_str = match.group(4)  # SS
    rest = match.group(5)  # originalname.ext
    
    # Check if date is in range
    try:
        file_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if not (start_date_obj <= file_date <= end_date_obj):
            return None  # Date not in range, don't adjust
    except ValueError:
        return None
    
    # Parse the hour
    try:
        hour = int(hour_str)
    except ValueError:
        return None
    
    # Add hours
    new_hour = hour + hours_to_add
    
    # Handle day rollover
    days_to_adjust = 0
    if new_hour < 0:
        days_to_adjust = (new_hour - 23) // 24  # Negative days
        new_hour = ((new_hour % 24) + 24) % 24
    elif new_hour >= 24:
        days_to_adjust = new_hour // 24
        new_hour = new_hour % 24
    
    # Adjust the date if needed
    if days_to_adjust != 0:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_obj = date_obj + timedelta(days=days_to_adjust)
            date_str = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None
    
    # Format the new hour as two digits
    new_hour_str = f"{new_hour:02d}"
    
    # Reconstruct the filename
    new_filename = f"{date_str}_{new_hour_str}-{minute_str}-{second_str}_{rest}"
    
    return new_filename


def adjust_timestamps_in_folder(
    folder_path: Path, start_date: str, end_date: str, hours_to_add: int
) -> Tuple[int, int]:
    """
    Adjust timestamps in a folder for files within a date range.
    
    Args:
        folder_path: Path to the folder containing files
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (inclusive)
        hours_to_add: Number of hours to add (can be negative to subtract)
        
    Returns:
        Tuple of (files_renamed, files_skipped)
    """
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Warning: {folder_path} does not exist or is not a directory")
        return 0, 0
    
    files_renamed = 0
    files_skipped = 0
    
    # Get all files in the folder
    all_files = list(folder_path.iterdir())
    image_files = [f for f in all_files if f.is_file()]
    
    for file_path in image_files:
        old_name = file_path.name
        new_name = adjust_hour_in_filename_for_date_range(old_name, start_date, end_date, hours_to_add)
        
        if new_name is None:
            # File not in date range or doesn't match pattern
            files_skipped += 1
            continue
        
        if old_name == new_name:
            # No change needed
            files_skipped += 1
            continue
        
        new_path = file_path.parent / new_name
        
        # Check if target file already exists
        if new_path.exists():
            print(f"  SKIP: {old_name} -> {new_name} (target already exists)")
            files_skipped += 1
            continue
        
        try:
            file_path.rename(new_path)
            files_renamed += 1
        except Exception as e:
            print(f"  ERROR renaming {old_name}: {e}")
            files_skipped += 1
    
    return files_renamed, files_skipped


def plot_time_distribution(timestamps: List[datetime], output_path: Path) -> None:
    """
    Plot a histogram of times of day for timestamps outside trading hours.
    
    Args:
        timestamps: List of datetime objects representing timestamps outside trading hours
        output_path: Path to save the plot image (e.g., PNG)
    """
    if not timestamps:
        return
    
    # Import matplotlib lazily so the script still works if it's not installed
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError(
            "matplotlib is required to generate the distribution plot. "
            "Install it with 'pip install matplotlib'."
        ) from e
    
    # Convert timestamps to fractional hours (0-24)
    hours: List[float] = []
    for ts in timestamps:
        t = ts.time()
        frac_hour = t.hour + t.minute / 60.0 + t.second / 3600.0
        hours.append(frac_hour)
    
    plt.figure(figsize=(10, 5))
    plt.hist(
        hours,
        bins=range(0, 25),  # 24 bins, one per hour
        edgecolor="black",
        alpha=0.75,
    )
    plt.title("Distribution of Timestamps Outside Trading Hours (US EST)")
    plt.xlabel("Hour of Day (0–24, EST)")
    plt.ylabel("Number of Files")
    plt.xlim(0, 24)
    plt.xticks(range(0, 25, 1))
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Quality check: Find files with timestamps outside US EST trading hours (09:30:00 to 16:00:00)"
    )
    parser.add_argument(
        "--folder",
        type=str,
        default="spx-realtime-aws-clean",
        help="Folder to check (default: spx-realtime-aws-clean)"
    )
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder)
    
    print("=" * 60)
    print("Quality Check: Timestamps Outside Trading Hours")
    print(f"Checking folder: {folder_path}")
    print("Trading hours: 09:30:00 to 16:00:00 (US EST)")
    print("=" * 60)
    
    result = quality_check_timestamps(folder_path)
    
    if result is None:
        print("\n[OK] All files are within trading hours (09:30:00 to 16:00:00)")
        print("No files found outside the expected time range.")
    else:
        files_outside, dates_outside, hour_distribution, missing_dates = result
        print(f"\nTotal: {len(files_outside)} file(s) outside trading hours")
        print(f"Total: {len(dates_outside)} unique date(s) with files outside trading hours")
        print(f"Total: {len(hour_distribution)} hour bucket(s) with files outside trading hours")
        if missing_dates:
            print(f"Total: {len(missing_dates)} missing date(s) in the period range")
    
    print("=" * 60)
    
    # Interactive timestamp adjustment
    if result is not None:
        print("\n" + "=" * 60)
        print("Timestamp Adjustment")
        print("=" * 60)
        
        while True:
            user_input = input("\nDo you want to adjust timestamps? (Yes/No): ").strip().lower()
            if user_input in ['yes', 'y']:
                break
            elif user_input in ['no', 'n']:
                print("Timestamp adjustment skipped.")
                return result
            else:
                print("Please enter 'Yes' or 'No'")
        
        # Get number of periods
        while True:
            try:
                num_periods = int(input("\nHow many periods need to change? "))
                if num_periods > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Process each period
        folders_to_adjust = ["spx-realtime-aws", "spx-realtime-aws-clean", "spx-clean-1perDay"]
        
        for period_num in range(1, num_periods + 1):
            print(f"\n--- Period {period_num} ---")
            
            # Get start date
            while True:
                start_date = input(f"Period {period_num} start date (yyyy-mm-dd): ").strip()
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Invalid date format. Please use yyyy-mm-dd (e.g., 2025-03-10)")
            
            # Get end date
            while True:
                end_date = input(f"Period {period_num} end date (yyyy-mm-dd): ").strip()
                try:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    if end_date_obj >= start_date_obj:
                        break
                    else:
                        print("End date must be >= start date.")
                except ValueError:
                    print("Invalid date format. Please use yyyy-mm-dd (e.g., 2025-03-10)")
            
            # Get hours to add
            while True:
                try:
                    hours_to_add = int(input(f"Add how many hours? (can be negative to subtract): "))
                    break
                except ValueError:
                    print("Please enter a valid integer.")
            
            print(f"\nAdjusting timestamps for period {period_num}:")
            print(f"  Date range: {start_date} to {end_date}")
            print(f"  Hours to add: {hours_to_add}")
            print(f"  Folders: {', '.join(folders_to_adjust)}")
            
            # Apply adjustment to all 3 folders
            total_renamed = 0
            total_skipped = 0
            
            for folder_name in folders_to_adjust:
                folder_path = Path(folder_name)
                renamed, skipped = adjust_timestamps_in_folder(
                    folder_path, start_date, end_date, hours_to_add
                )
                total_renamed += renamed
                total_skipped += skipped
                print(f"  {folder_name}: {renamed} renamed, {skipped} skipped")
            
            print(f"\nPeriod {period_num} summary: {total_renamed} files renamed across all folders")
        
        print("\n" + "=" * 60)
        print("Timestamp adjustment completed!")
        print("=" * 60)
        
        # Run quality check again on all 3 folders to verify adjustments
        print("\n" + "=" * 60)
        print("Post-Adjustment Quality Check")
        print("=" * 60)
        print("Running quality check on all 3 folders to verify adjustments...")
        print()
        
        folders_to_check = ["spx-realtime-aws", "spx-realtime-aws-clean", "spx-clean-1perDay"]
        all_results = {}
        
        for folder_name in folders_to_check:
            folder_path = Path(folder_name)
            print(f"Checking folder: {folder_name}")
            print("-" * 60)
            
            check_result = quality_check_timestamps(folder_path, silent=True)
            
            if check_result is None:
                print(f"  ✓ {folder_name}: All files are within trading hours")
                all_results[folder_name] = {
                    'files_count': 0,
                    'dates_count': 0,
                    'dates': set()
                }
            else:
                files_outside, dates_outside, hour_dist, missing_dates = check_result
                print(f"  ⚠ {folder_name}: {len(files_outside)} file(s) outside trading hours")
                print(f"     {len(dates_outside)} unique date(s) with files outside trading hours")
                all_results[folder_name] = {
                    'files_count': len(files_outside),
                    'dates_count': len(dates_outside),
                    'dates': dates_outside
                }
            print()
        
        # Summary
        print("=" * 60)
        print("Post-Adjustment Summary")
        print("=" * 60)
        total_files_outside = 0
        all_dates_outside = set()
        
        for folder_name, folder_result in all_results.items():
            total_files_outside += folder_result['files_count']
            all_dates_outside.update(folder_result['dates'])
            print(f"{folder_name}:")
            print(f"  Files outside trading hours: {folder_result['files_count']}")
            print(f"  Unique dates: {folder_result['dates_count']}")
            if folder_result['dates']:
                sorted_dates = sorted(folder_result['dates'])
                if len(sorted_dates) <= 10:
                    print(f"  Dates: {', '.join(sorted_dates)}")
                else:
                    print(f"  First 5 dates: {', '.join(sorted_dates[:5])}")
                    print(f"  Last 5 dates: {', '.join(sorted_dates[-5:])}")
                    print(f"  ... ({len(sorted_dates) - 10} more dates)")
            print()
        
        print(f"Overall Summary:")
        print(f"  Total files outside trading hours across all folders: {total_files_outside}")
        print(f"  Total unique dates with files outside trading hours: {len(all_dates_outside)}")
        if all_dates_outside:
            sorted_all_dates = sorted(all_dates_outside)
            print(f"  All dates: {', '.join(sorted_all_dates)}")
        print("=" * 60)
    
    return result


if __name__ == "__main__":
    main()

