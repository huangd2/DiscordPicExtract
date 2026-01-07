"""
Reorder columns in all CSV files to a standard order.

This script standardizes the column order across all CSV files in the SPXsignal folder
to ensure consistency. The target order is:
1. signal#
2. timestamp
3. price
4. buy/sell
5. fPrice
6. risk

Any additional columns will be preserved at the end. Missing columns will be created
as empty columns to maintain consistency.

Usage:
    python reorder_columns.py
"""
import os
import re
import pandas as pd
from pathlib import Path

# =========================
# CONFIG
# =========================
DATA_DIR = Path.home() / "Desktop" / "SPXsignal"
DATE_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.csv$")

# Desired column order - standardizes all CSV files to this structure
DESIRED_COLUMNS = ['signal#', 'timestamp', 'price', 'buy/sell', 'fPrice', 'risk']


def reorder_csv_columns(file_path: Path) -> bool:
    """
    Reorder columns in a CSV file to match the desired order.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Get current columns
        current_columns = list(df.columns)
        
        # Check if reordering is needed
        if current_columns == DESIRED_COLUMNS:
            return True  # Already in correct order
        
        # Create ordered columns list
        ordered_columns = []
        other_columns = []
        
        # Add desired columns in order (if they exist)
        # If a column doesn't exist, create it as empty to maintain consistency
        for col in DESIRED_COLUMNS:
            if col in df.columns:
                ordered_columns.append(col)
            else:
                # Column doesn't exist, create empty column to maintain structure
                df[col] = ''
                ordered_columns.append(col)
        
        # Add any other columns that aren't in the desired list (preserve them at the end)
        # This ensures we don't lose any data from unexpected columns
        for col in current_columns:
            if col not in DESIRED_COLUMNS:
                other_columns.append(col)
        
        # Combine: desired columns first, then any other columns
        final_columns = ordered_columns + other_columns
        
        # Reorder dataframe
        df = df[final_columns]
        
        # Save back to file
        df.to_csv(file_path, index=False)
        
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    """Process all CSV files in SPXsignal folder to reorder columns."""
    if not DATA_DIR.exists():
        print(f"Error: Directory {DATA_DIR} does not exist")
        return
    
    # Get all CSV files matching date pattern
    csv_files = sorted([f for f in os.listdir(DATA_DIR) if DATE_FILE_PATTERN.match(f)])
    
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return
    
    print("=" * 80)
    print(f"Reordering columns in {len(csv_files)} CSV files")
    print(f"Target order: {', '.join(DESIRED_COLUMNS)}")
    print("=" * 80)
    print()
    
    successful = 0
    failed = 0
    already_ordered = 0
    
    for i, fname in enumerate(csv_files, 1):
        print(f"Processing file {i}/{len(csv_files)}: {fname}")
        
        file_path = DATA_DIR / fname
        
        try:
            # Check current order
            df_check = pd.read_csv(file_path)
            current_cols = list(df_check.columns)
            
            # Check if already in correct order
            if current_cols == DESIRED_COLUMNS:
                print(f"  Already in correct order, skipping...")
                already_ordered += 1
                print()
                continue
            
            # Reorder columns
            if reorder_csv_columns(file_path):
                print(f"  Successfully reordered columns")
                successful += 1
            else:
                print(f"  Failed to reorder columns")
                failed += 1
                
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total files found: {len(csv_files)}")
    print(f"Successfully reordered: {successful}")
    print(f"Already in correct order: {already_ordered}")
    print(f"Failed: {failed}")
    print("=" * 80)
    print("DONE.")


if __name__ == "__main__":
    main()

