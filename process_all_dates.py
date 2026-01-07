"""Process all remaining dates in the clean folder."""
from pathlib import Path
import re
from extract_signals import process_date

def main():
    # Find all dates in the clean folder
    folder = Path("spx-realtime-aws-clean")
    csv_dir = Path.home() / "Desktop" / "SPXsignal"
    
    pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})_')
    dates = set()
    for f in folder.glob("*.png"):
        m = pattern.match(f.name)
        if m:
            dates.add(m.group(1))
    
    # Find which dates already have CSVs
    existing = {f.stem for f in csv_dir.glob("*.csv")}
    
    # Get remaining dates
    remaining = sorted(dates - existing)
    
    print("=" * 60)
    print("BATCH PROCESSING: Extract Signals for All Remaining Dates")
    print("=" * 60)
    print(f"Total dates found: {len(dates)}")
    print(f"Already processed: {len(existing)}")
    print(f"Remaining to process: {len(remaining)}")
    print("=" * 60)
    print()
    
    # Track results
    results = []
    successful = []
    failed = []
    
    # Process each remaining date
    for i, date_str in enumerate(remaining, 1):
        print("\n" + "=" * 60)
        print(f"[{i}/{len(remaining)}] Starting processing for {date_str}")
        print("=" * 60)
        try:
            signals = process_date(folder, date_str)
            signal_count = len(signals) if signals else 0
            results.append((date_str, signal_count, "SUCCESS"))
            successful.append((date_str, signal_count))
            print(f"\n[OK] Completed {date_str} - {signal_count} signals extracted")
        except Exception as e:
            results.append((date_str, 0, f"ERROR: {str(e)}"))
            failed.append((date_str, str(e)))
            print(f"\n[ERROR] Failed to process {date_str}: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total dates processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print()
    
    if successful:
        total_signals = sum(count for _, count in successful)
        print(f"Total signals extracted: {total_signals}")
        print(f"Average signals per date: {total_signals / len(successful):.1f}")
        print()
        print("Successfully processed dates:")
        for date_str, count in successful:
            print(f"  {date_str}: {count} signals")
    
    if failed:
        print()
        print("Failed dates:")
        for date_str, error in failed:
            print(f"  {date_str}: {error}")
    
    print("=" * 60)
    print("All dates processed!")

if __name__ == "__main__":
    main()

