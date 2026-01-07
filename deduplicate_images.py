"""Script to detect and remove duplicate images based on content."""
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import imagehash
from PIL import Image
import statistics


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


def calculate_image_hash(image_path: Path) -> Optional[imagehash.ImageHash]:
    """Calculate perceptual hash of an image."""
    try:
        with Image.open(image_path) as img:
            # Use perceptual hash (pHash) which is good for detecting similar/duplicate images
            return imagehash.phash(img)
    except Exception as e:
        print(f"Error calculating hash for {image_path.name}: {e}")
        return None


def find_duplicates(source_dir: Path) -> Dict[str, List[Path]]:
    """
    Find duplicate images by comparing their perceptual hashes.
    Only compares images from the same date.
    
    Returns:
        Dictionary mapping hash values to lists of file paths with that hash
    """
    print(f"Scanning images in: {source_dir.absolute()}")
    
    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    image_files = [
        f for f in source_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    print(f"Found {len(image_files)} image files")
    
    # Group files by date first
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
    
    # Find duplicates within each date group
    all_duplicates: Dict[str, List[Path]] = {}
    
    print("Calculating image hashes and finding duplicates (within same date only)...")
    
    for date_str, date_files in files_by_date.items():
        if len(date_files) < 2:
            continue  # Skip dates with only one image
        
        # Calculate hashes for images on this date
        # Use hash + file_size as the key to avoid false positives
        hash_size_to_files: Dict[str, List[Path]] = {}
        
        for image_file in date_files:
            img_hash = calculate_image_hash(image_file)
            if img_hash is not None:
                # Get file size to create a more unique identifier
                file_size = image_file.stat().st_size
                # Combine hash and file size to identify true duplicates
                hash_size_key = f"{str(img_hash)}_{file_size}"
                if hash_size_key not in hash_size_to_files:
                    hash_size_to_files[hash_size_key] = []
                hash_size_to_files[hash_size_key].append(image_file)
        
        # Find duplicates within this date (groups with more than one file)
        # Only files with both same hash AND same size are considered duplicates
        date_duplicates = {
            hash_size_key: files
            for hash_size_key, files in hash_size_to_files.items()
            if len(files) > 1
        }
        
        # Add to all_duplicates with date prefix to avoid collisions
        for hash_size_key, files in date_duplicates.items():
            # Use date + hash_size_key as key to ensure uniqueness across dates
            unique_key = f"{date_str}_{hash_size_key}"
            all_duplicates[unique_key] = files
    
    total_duplicate_groups = len(all_duplicates)
    total_duplicate_files = sum(len(files) - 1 for files in all_duplicates.values())
    print(f"Found {total_duplicate_groups} duplicate groups within same dates")
    print(f"Total duplicate files: {total_duplicate_files}")
    
    return all_duplicates


def keep_earliest_timestamp(files: List[Path]) -> Tuple[Path, List[Path], Dict[Path, Path]]:
    """
    From a list of duplicate files, keep the one with the earliest timestamp.
    
    Returns:
        Tuple of (file_to_keep, files_to_remove, mapping_of_removed_to_kept)
    """
    # Parse timestamps and sort
    files_with_timestamps = []
    for file in files:
        timestamp = parse_timestamp_from_filename(file.name)
        if timestamp:
            files_with_timestamps.append((timestamp, file))
        else:
            # If we can't parse timestamp, use file modification time as fallback
            files_with_timestamps.append((datetime.fromtimestamp(file.stat().st_mtime), file))
    
    # Sort by timestamp (earliest first)
    files_with_timestamps.sort(key=lambda x: x[0])
    
    # The first one is the earliest
    file_to_keep = files_with_timestamps[0][1]
    files_to_remove = [f[1] for f in files_with_timestamps[1:]]
    
    # Create mapping: removed_file -> kept_file
    removed_to_kept = {removed: file_to_keep for removed in files_to_remove}
    
    return file_to_keep, files_to_remove, removed_to_kept


def calculate_timestamp_differences(removed_to_kept: Dict[Path, Path]) -> Tuple[List[float], Dict[str, float]]:
    """
    Calculate timestamp differences in seconds between removed files and their kept duplicates.
    
    Args:
        removed_to_kept: Dictionary mapping removed file paths to their kept file paths
    
    Returns:
        Tuple of (list of timestamp differences in seconds, mapping of removed file name to difference)
    """
    differences = []
    file_to_diff: Dict[str, float] = {}
    
    for removed_file, kept_file in removed_to_kept.items():
        removed_timestamp = parse_timestamp_from_filename(removed_file.name)
        kept_timestamp = parse_timestamp_from_filename(kept_file.name)
        
        if removed_timestamp and kept_timestamp:
            # Calculate difference in seconds
            diff_seconds = (removed_timestamp - kept_timestamp).total_seconds()
            differences.append(diff_seconds)
            
            # Track which file has this difference
            file_to_diff[removed_file.name] = diff_seconds
        else:
            # If we can't parse timestamps, skip this pair
            continue
    
    return differences, file_to_diff


def print_timestamp_statistics(differences: List[float], file_to_diff: Dict[str, float]) -> None:
    """
    Print statistics about timestamp differences.
    
    Args:
        differences: List of timestamp differences in seconds
        file_to_diff: Mapping of removed file name to difference value
    """
    if not differences:
        print("\nNo timestamp differences to calculate.")
        return
    
    # Calculate statistics
    total = len(differences)
    mean = statistics.mean(differences)
    median = statistics.median(differences)
    min_diff = min(differences)
    max_diff = max(differences)
    
    # Calculate percentiles
    sorted_diffs = sorted(differences)
    p25 = sorted_diffs[int(len(sorted_diffs) * 0.25)] if len(sorted_diffs) > 0 else 0
    p75 = sorted_diffs[int(len(sorted_diffs) * 0.75)] if len(sorted_diffs) > 0 else 0
    p90 = sorted_diffs[int(len(sorted_diffs) * 0.90)] if len(sorted_diffs) > 0 else 0
    p95 = sorted_diffs[int(len(sorted_diffs) * 0.95)] if len(sorted_diffs) > 0 else 0
    
    # Calculate standard deviation if we have enough data
    stdev = statistics.stdev(differences) if len(differences) > 1 else 0
    
    # Format time differences for display
    def format_seconds(secs: float) -> str:
        if secs < 60:
            return f"{secs:.1f}s"
        elif secs < 3600:
            return f"{secs/60:.1f}m ({secs:.1f}s)"
        elif secs < 86400:
            return f"{secs/3600:.1f}h ({secs:.1f}s)"
        else:
            return f"{secs/86400:.1f}d ({secs:.1f}s)"
    
    print(f"\n{'='*70}")
    print("Timestamp Difference Statistics (Removed vs Kept Duplicates)")
    print(f"{'='*70}")
    print(f"Total pairs calculated:     {total:,}")
    print(f"Mean difference:            {format_seconds(mean)}")
    print(f"Median difference:          {format_seconds(median)}")
    print(f"Standard deviation:         {format_seconds(stdev)}")
    print(f"Minimum difference:         {format_seconds(min_diff)}")
    print(f"Maximum difference:         {format_seconds(max_diff)}")
    print(f"25th percentile:           {format_seconds(p25)}")
    print(f"75th percentile:           {format_seconds(p75)}")
    print(f"90th percentile:           {format_seconds(p90)}")
    print(f"95th percentile:           {format_seconds(p95)}")
    print(f"{'='*70}")
    
    # Find files with differences above 95th percentile
    files_above_p95 = []
    for filename, diff_seconds in file_to_diff.items():
        if diff_seconds > p95:
            files_above_p95.append((filename, diff_seconds))
    
    # Sort by difference (largest first)
    files_above_p95.sort(key=lambda x: x[1], reverse=True)
    
    if files_above_p95:
        print(f"\nFiles with timestamp difference above 95th percentile ({format_seconds(p95)}):")
        print(f"Total: {len(files_above_p95)} files")
        print(f"\nFile names (sorted by difference, largest first):")
        for filename, file_diff in files_above_p95:
            print(f"  {filename} (difference: {format_seconds(file_diff)})")
        print(f"{'='*70}")
    else:
        print(f"\nNo files found with timestamp difference above 95th percentile ({format_seconds(p95)}).")
        print(f"{'='*70}")


def deduplicate_images(source_dir: Path, output_dir: Path) -> None:
    """
    Find duplicate images and copy unique ones to output directory.
    
    Args:
        source_dir: Directory containing images to check
        output_dir: Directory to save unique images
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
    
    # Find duplicates
    duplicates = find_duplicates(source_dir)
    
    if not duplicates:
        print("\nNo duplicates found. All images are unique.")
    else:
        print(f"\nFound {len(duplicates)} groups of duplicate images")
        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        print(f"Total duplicate files to remove: {total_duplicates}")
    
    # Track which files to keep and which are duplicates
    files_to_keep = set()
    duplicate_files = set()
    # Track mapping of removed files to their kept duplicates for statistics
    removed_to_kept_mapping: Dict[Path, Path] = {}
    
    # Process each duplicate group
    for hash_key, files in duplicates.items():
        file_to_keep, files_to_remove, removed_to_kept = keep_earliest_timestamp(files)
        files_to_keep.add(file_to_keep)
        duplicate_files.update(files_to_remove)
        # Add to the global mapping
        removed_to_kept_mapping.update(removed_to_kept)
        
        # Extract date and hash from key (format: "YYYY-MM-DD_hash_size")
        if '_' in hash_key:
            parts = hash_key.split('_', 2)
            date_part = parts[0] if len(parts) > 0 else "unknown"
            # hash_part is now "hash_size", extract just the hash part
            hash_part = parts[1] if len(parts) > 1 else hash_key
            hash_display = hash_part[:16] if len(hash_part) > 16 else hash_part
        else:
            date_part = "unknown"
            hash_display = hash_key[:16]
        
        if len(files) <= 10:  # Only print details for small groups to reduce output
            print(f"\nDuplicate group (date: {date_part}, hash: {hash_display}...):")
            print(f"  Keeping (earliest): {file_to_keep.name}")
            for dup_file in files_to_remove:
                print(f"  Removing (duplicate): {dup_file.name}")
        else:
            print(f"\nDuplicate group (date: {date_part}, hash: {hash_display}...) - {len(files)} files:")
            print(f"  Keeping (earliest): {file_to_keep.name}")
            print(f"  Removing {len(files_to_remove)} duplicates")
    
    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    all_image_files = [
        f for f in source_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    # Copy unique images to output directory
    # Files to copy: all files that are NOT in duplicate_files
    # (This includes files_to_keep and files that are not in any duplicate group)
    print(f"\nCopying unique images to {output_dir.name}...")
    copied_count = 0
    skipped_count = 0
    
    for image_file in all_image_files:
        if image_file in duplicate_files:
            # Skip duplicate files (but keep the earliest ones which are not in duplicate_files)
            skipped_count += 1
            continue
        
        # Copy to output directory
        dest_file = output_dir / image_file.name
        try:
            shutil.copy2(image_file, dest_file)
            copied_count += 1
            if copied_count % 100 == 0:
                print(f"  Copied {copied_count} files...")
        except Exception as e:
            print(f"  Error copying {image_file.name}: {e}")
    
    # Calculate and print timestamp difference statistics
    if removed_to_kept_mapping:
        differences, file_to_diff = calculate_timestamp_differences(removed_to_kept_mapping)
        print_timestamp_statistics(differences, file_to_diff)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Deduplication Summary:")
    print(f"  Total images scanned: {len(all_image_files)}")
    print(f"  Unique images copied: {copied_count}")
    print(f"  Duplicates skipped: {skipped_count}")
    print(f"  Duplicate groups found: {len(duplicates)}")
    print(f"{'='*60}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Detect and remove duplicate images based on content"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="spx-realtime-aws",
        help="Source directory containing images (default: spx-realtime-aws)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="spx-realtime-aws-clean",
        help="Output directory for unique images (default: spx-realtime-aws-clean)"
    )
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    output_dir = Path(args.output)
    
    deduplicate_images(source_dir, output_dir)


if __name__ == "__main__":
    main()

