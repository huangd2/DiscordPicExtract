"""Script to adjust specific timestamps: 2025-09-24 files with time >= 11:52:43, subtract 1 hour."""
import re
from pathlib import Path
from datetime import datetime, timedelta


def adjust_hour_for_specific_condition(filename: str) -> str:
    """
    Adjust hour by subtracting 1 hour if:
    - Date is 2025-09-24
    - Time is >= 11:52:43
    
    Args:
        filename: Original filename with timestamp
        
    Returns:
        New filename with adjusted hour, or original filename if condition not met
    """
    # Pattern to match: YYYY-MM-DD_HH-MM-SS_...
    pattern = r'^(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})_(.+)$'
    match = re.match(pattern, filename)
    
    if not match:
        return filename
    
    date_str = match.group(1)  # YYYY-MM-DD
    hour_str = match.group(2)  # HH
    minute_str = match.group(3)  # MM
    second_str = match.group(4)  # SS
    rest = match.group(5)  # originalname.ext
    
    # Check if date is 2025-09-24
    if date_str != "2025-09-24":
        return filename
    
    # Check if time is >= 11:52:43
    try:
        hour = int(hour_str)
        minute = int(minute_str)
        second = int(second_str)
        
        # Create time object for comparison
        file_time = datetime.strptime(f"{hour:02d}:{minute:02d}:{second:02d}", "%H:%M:%S").time()
        threshold_time = datetime.strptime("11:52:43", "%H:%M:%S").time()
        
        if file_time < threshold_time:
            return filename  # Time is before threshold, don't adjust
    except ValueError:
        return filename
    
    # Subtract 1 hour
    new_hour = hour - 1
    
    # Handle day rollover if hour becomes negative
    if new_hour < 0:
        new_hour += 24
        # Adjust the date by subtracting one day
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_obj = date_obj - timedelta(days=1)
            date_str = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return filename
    
    # Format the new hour as two digits
    new_hour_str = f"{new_hour:02d}"
    
    # Reconstruct the filename
    new_filename = f"{date_str}_{new_hour_str}-{minute_str}-{second_str}_{rest}"
    
    return new_filename


def adjust_files_in_folder(folder_path: Path) -> tuple[int, int]:
    """
    Adjust files in a folder according to the specific condition.
    
    Args:
        folder_path: Path to the folder containing files
        
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
        new_name = adjust_hour_for_specific_condition(old_name)
        
        if old_name == new_name:
            # File doesn't match condition or doesn't need adjustment
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
            print(f"  RENAMED: {old_name} -> {new_name}")
            files_renamed += 1
        except Exception as e:
            print(f"  ERROR renaming {old_name}: {e}")
            files_skipped += 1
    
    return files_renamed, files_skipped


def main():
    """Main function."""
    folders_to_adjust = ["spx-realtime-aws", "spx-realtime-aws-clean", "spx-clean-1perDay"]
    
    print("=" * 60)
    print("Adjusting Timestamps for 2025-09-24")
    print("Condition: Files with time >= 11:52:43, subtract 1 hour")
    print("=" * 60)
    
    total_renamed = 0
    total_skipped = 0
    
    for folder_name in folders_to_adjust:
        folder_path = Path(folder_name)
        print(f"\nProcessing folder: {folder_name}")
        print("-" * 60)
        
        renamed, skipped = adjust_files_in_folder(folder_path)
        total_renamed += renamed
        total_skipped += skipped
        
        print(f"Summary for {folder_name}:")
        print(f"  Renamed: {renamed}")
        print(f"  Skipped: {skipped}")
    
    print("\n" + "=" * 60)
    print("Overall Summary:")
    print(f"  Total renamed: {total_renamed}")
    print(f"  Total skipped: {total_skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()

