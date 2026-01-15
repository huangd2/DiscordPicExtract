"""
Combine daily CSV files from Desktop/SPXsignal-test into a single combined_data.csv,
excluding the last (most recent) file.
"""
from pathlib import Path
import re
import pandas as pd


DATA_DIR = Path.home() / "Desktop" / "SPXsignal-test"
OUTPUT_DIR = Path(__file__).resolve().parent / "test-result"
OUTPUT_FILE = OUTPUT_DIR / "combined_data.csv"

DATE_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.csv$")


def get_csv_files() -> list[Path]:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    csv_files = sorted([f for f in DATA_DIR.iterdir() if DATE_FILE_PATTERN.match(f.name)])
    if not csv_files:
        raise FileNotFoundError(f"No date-named CSV files found in {DATA_DIR}")

    if len(csv_files) == 1:
        raise ValueError("Only one CSV file found; nothing to combine after excluding last file.")

    excluded = csv_files.pop()  # Exclude the last (most recent) file
    print(f"Excluding last file: {excluded.name}")
    print(f"Combining {len(csv_files)} files from {DATA_DIR}")
    return csv_files


def main() -> None:
    csv_files = get_csv_files()

    dataframes = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        dataframes.append(df)
        print(f"  Loaded {csv_file.name}: {len(df)} rows")

    combined_df = pd.concat(dataframes, ignore_index=True)

    # Sort by timestamp if present
    if "timestamp" in combined_df.columns:
        combined_df["timestamp"] = pd.to_datetime(combined_df["timestamp"], errors="coerce")
        combined_df = combined_df.sort_values("timestamp").reset_index(drop=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved combined data to: {OUTPUT_FILE}")
    print(f"Total rows: {len(combined_df)}")


if __name__ == "__main__":
    main()

