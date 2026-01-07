"""Merge risk levels from triangle extraction into existing CSV signal files."""
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from extract_triangles_with_risk import extract_triangles_with_risk


def find_all_dates(folder_path: Path) -> List[str]:
    """
    Find all unique dates from image filenames in the folder.
    
    Args:
        folder_path: Path to folder containing images
    
    Returns:
        List of date strings in YYYY-MM-DD format
    """
    dates = set()
    pattern = "*.png"
    
    for image_file in folder_path.glob(pattern):
        # Extract date from filename: YYYY-MM-DD_HH-MM-SS_*.png
        try:
            date_str = image_file.name[:10]  # First 10 characters = YYYY-MM-DD
            datetime.strptime(date_str, "%Y-%m-%d")  # Validate format
            dates.add(date_str)
        except (ValueError, IndexError):
            continue
    
    return sorted(list(dates))


def parse_timestamp_for_merge(timestamp_str: str, date_str: Optional[str] = None) -> Optional[datetime]:
    """
    Parse timestamp string for merging.
    Handles both full datetime and time-only formats.
    
    Args:
        timestamp_str: Timestamp string (full datetime or time-only)
        date_str: Optional date string for time-only format
    
    Returns:
        datetime object or None if parsing fails
    """
    ts_clean = timestamp_str.strip()
    
    # Try full datetime format first: YYYY-MM-DD HH:MM:SS
    try:
        return datetime.strptime(ts_clean, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    
    # Try time-only format: HH:MM:SS (combine with date_str if provided)
    if date_str:
        try:
            return datetime.strptime(f"{date_str} {ts_clean}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    
    return None


def merge_risk_levels(
    csv_path: Path,
    risk_results: List[Dict],
    date_str: str
) -> bool:
    """
    Merge risk levels into existing CSV file.
    
    Args:
        csv_path: Path to CSV file
        risk_results: List of risk extraction results with timestamp and risk_level
        date_str: Date string for handling time-only timestamps
    
    Returns:
        True if merge was successful, False otherwise
    """
    if not csv_path.exists():
        print(f"  Warning: CSV file not found: {csv_path}")
        return False
    
    # Read existing CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"  Error reading CSV: {e}")
        return False
    
    # Check if timestamp column exists
    if 'timestamp' not in df.columns:
        print(f"  Warning: No 'timestamp' column in CSV")
        return False
    
    # Create risk lookup dictionary from risk_results
    risk_lookup = {}
    for result in risk_results:
        ts_str = result['timestamp']
        risk_level = result['risk_level']
        
        # Parse timestamp (risk_results always have full datetime format)
        ts_parsed = parse_timestamp_for_merge(ts_str, date_str)
        if ts_parsed:
            risk_lookup[ts_parsed] = risk_level
    
    # Parse timestamps in CSV
    df['timestamp_parsed'] = pd.to_datetime(
        df['timestamp'],
        format="%Y-%m-%d %H:%M:%S",
        errors='coerce'
    )
    
    # Handle time-only format if parsing failed
    mask_na = df['timestamp_parsed'].isna()
    if mask_na.any():
        time_only = pd.to_datetime(
            date_str + " " + df.loc[mask_na, 'timestamp'].astype(str),
            format="%Y-%m-%d %H:%M:%S",
            errors='coerce'
        )
        df.loc[mask_na, 'timestamp_parsed'] = time_only
    
    # Match and add risk levels
    risk_values = []
    for ts_parsed in df['timestamp_parsed']:
        if pd.isna(ts_parsed):
            risk_values.append('')
            continue
        
        # Find closest match (within 1 second tolerance)
        matched_risk = None
        min_diff = float('inf')
        
        for risk_ts, risk_level in risk_lookup.items():
            diff = abs((ts_parsed - risk_ts).total_seconds())
            if diff < min_diff and diff <= 1.0:  # Within 1 second
                min_diff = diff
                matched_risk = risk_level
        
        risk_values.append(matched_risk if matched_risk else '')
    
    # Add risk column (remove if it already exists)
    if 'risk' in df.columns:
        df = df.drop(columns=['risk'])
    
    df['risk'] = risk_values
    
    # Remove temporary timestamp_parsed column
    df = df.drop(columns=['timestamp_parsed'])
    
    # Save back to CSV
    try:
        df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        print(f"  Error saving CSV: {e}")
        return False


def process_all_dates_with_risk(
    folder_path: Path,
    output_dir: Optional[Path] = None,
    colorbar_path: Optional[Path] = None
) -> None:
    """
    Process all dates in folder and merge risk levels into CSV files.
    
    Args:
        folder_path: Path to folder containing images (should be -clean folder)
        output_dir: Path to SPXsignal folder (defaults to Desktop/SPXsignal)
        colorbar_path: Optional path to colorbar image
    """
    if not folder_path.exists():
        print(f"Error: Folder {folder_path} does not exist")
        return
    
    if output_dir is None:
        output_dir = Path.home() / "Desktop" / "SPXsignal"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all dates
    print("Finding all dates in folder...")
    dates = find_all_dates(folder_path)
    
    if not dates:
        print("No dates found in folder")
        return
    
    print(f"Found {len(dates)} unique dates: {', '.join(dates[:5])}{'...' if len(dates) > 5 else ''}")
    print()
    
    # Process each date
    successful = 0
    failed = 0
    skipped = 0
    already_processed = 0
    
    for i, date_str in enumerate(dates, 1):
        print("=" * 80)
        print(f"Processing date {i}/{len(dates)}: {date_str}")
        print("=" * 80)
        
        # Check if already processed - skip files that already have risk data
        # This allows the script to resume after interruptions without reprocessing
        csv_path = output_dir / f"{date_str}.csv"
        if csv_path.exists():
            try:
                df_check = pd.read_csv(csv_path)
                # Check if risk column exists and has non-empty data
                if 'risk' in df_check.columns and df_check['risk'].notna().any() and (df_check['risk'] != '').any():
                    print(f"  Already processed (risk column exists with data), skipping...")
                    already_processed += 1
                    print()
                    continue
            except Exception:
                pass  # If we can't read it, continue processing
        
        # Extract risk levels
        risk_results = extract_triangles_with_risk(folder_path, date_str, colorbar_path)
        
        if not risk_results:
            print(f"  No risk results extracted for {date_str}")
            skipped += 1
            continue
        
        print(f"  Extracted {len(risk_results)} risk levels")
        
        # Merge into CSV
        if merge_risk_levels(csv_path, risk_results, date_str):
            print(f"  Successfully merged risk levels into {csv_path.name}")
            successful += 1
        else:
            print(f"  Failed to merge risk levels for {date_str}")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total dates found: {len(dates)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped (no risk results): {skipped}")
    print(f"Already processed: {already_processed}")
    print("=" * 80)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Merge risk levels from triangle extraction into CSV signal files"
    )
    parser.add_argument(
        "--folder",
        type=str,
        default="spx-realtime-aws-clean",
        help="Folder containing images (default: spx-realtime-aws-clean)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for CSV files (default: Desktop/SPXsignal)"
    )
    parser.add_argument(
        "--colorbar",
        type=str,
        default=None,
        help="Path to colorbar image (default: Desktop/colorbar.png)"
    )
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder)
    output_dir = Path(args.output) if args.output else None
    colorbar_path = Path(args.colorbar) if args.colorbar else None
    
    process_all_dates_with_risk(folder_path, output_dir, colorbar_path)


if __name__ == "__main__":
    main()

