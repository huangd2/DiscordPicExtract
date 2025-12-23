"""
Continue fetching SPX prices for CSV files that don't have fPrice column yet.

This script processes all CSV files in the SPXsignal folder and adds SPX (SPY) prices
for timestamps that don't already have fPrice data. It skips files that already have
fPrice data populated, allowing the script to resume after interruptions.

Usage:
    python continue_fetch_spx_prices.py

The script will:
1. Find all CSV files in ~/Desktop/SPXsignal/
2. Skip files that already have fPrice column with data
3. For remaining files, fetch SPY minute data from Polygon API
4. Match timestamps to closest available price
5. Add fPrice column to CSV files
6. Preserve all existing data and columns
"""
import os
import re
import time
import json
import pandas as pd
from polygon import RESTClient
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =========================
# AGENT LOG
# =========================
LOG_PATH = r"c:\Users\Vivian\Desktop\DiscordPicExtract\.cursor\debug.log"

def debug_log(location, message, data, hypothesis_id=None):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId":"debug-session",
                "runId":"run1",
                "hypothesisId":hypothesis_id,
                "location":location,
                "message":message,
                "data":data,
                "timestamp":int(time.time()*1000)
            }) + "\n")
    except:
        pass

# =========================
# CONFIG
# =========================
API_KEY = os.getenv("POLYGON_API_KEY")
debug_log("continue_fetch_spx_prices.py", "API key check", {"has_key":bool(API_KEY),"key_length":len(API_KEY) if API_KEY else 0}, "B")

if not API_KEY:
    raise ValueError(
        "POLYGON_API_KEY not found in environment variables. "
        "Please create a .env file with POLYGON_API_KEY=your_key_here"
    )

DATA_DIR = Path.home() / "Desktop" / "SPXsignal"
SLEEP_SECONDS = 12   # rate-limit safe (5 calls/min)

client = RESTClient(API_KEY)

DATE_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.csv$")

# =========================
# FUNCTIONS
# =========================
def fetch_spx_day(trading_date):
    """Fetch 1-minute SPY bars for a single trading day (SPY tracks SPX)"""
    debug_log("continue_fetch_spx_prices.py", "fetch_spx_day entry", {"trading_date":trading_date}, "E")
    try:
        aggs = client.get_aggs(
            ticker="SPY",
            multiplier=1,
            timespan="minute",
            from_=trading_date,
            to=trading_date,
            limit=5000
        )
        debug_log("continue_fetch_spx_prices.py", "API call success", {"ticker":"SPY","trading_date":trading_date,"agg_count":len(list(aggs)) if aggs else 0}, "E")
    except Exception as e:
        debug_log("continue_fetch_spx_prices.py", "API call failed", {"ticker":"SPY","trading_date":trading_date,"error_type":type(e).__name__,"error_message":str(e)}, "E")
        raise

    df = pd.DataFrame([{
        "timestamp": pd.to_datetime(a.timestamp, unit="ms"),
        "close": a.close
    } for a in aggs])

    if df.empty:
        raise ValueError(f"No SPX data for {trading_date}")

    # Convert to US Eastern naive (remove tz)
    df["timestamp"] = df["timestamp"].dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)

    return df.set_index("timestamp").sort_index()

def price_at_timestamp(minute_df, ts):
    """Last available close price <= timestamp"""
    debug_log("continue_fetch_spx_prices.py", "price_at_timestamp called", {
        "ts": str(ts),
        "df_index_tz_aware": minute_df.index.tz is not None if len(minute_df) > 0 else False
    }, "E")
    try:
        # Get all prices up to and including this timestamp
        available = minute_df.loc[:ts]
        if len(available) == 0:
            # Timestamp is before first available data, use first available price
            return minute_df.iloc[0]["close"]
        return available.iloc[-1]["close"]
    except Exception as e:
        debug_log("continue_fetch_spx_prices.py:price_at_timestamp", "Error in price lookup", {
            "ts": str(ts),
            "error": str(e),
            "df_range": f"{minute_df.index[0]} to {minute_df.index[-1]}" if len(minute_df) > 0 else "empty"
        }, "E")
        raise

def is_already_processed(df):
    """
    Check if file already has fPrice column with data.
    
    Args:
        df: DataFrame to check
        
    Returns:
        True if fPrice column exists and contains non-empty data, False otherwise
    """
    if 'fPrice' not in df.columns:
        return False
    
    # Check if fPrice has any non-empty, non-NaN values
    # This allows the script to skip files that were already processed
    fprice_col = df['fPrice']
    has_data = fprice_col.notna().any() and (fprice_col.astype(str).str.strip() != '').any()
    return has_data

# =========================
# MAIN LOOP
# =========================
def main():
    """Process all CSV files in SPXsignal folder, skipping those with fPrice already filled."""
    if not DATA_DIR.exists():
        print(f"Error: Directory {DATA_DIR} does not exist")
        return
    
    # Get all CSV files matching date pattern
    csv_files = sorted([f for f in os.listdir(DATA_DIR) if DATE_FILE_PATTERN.match(f)])
    
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return
    
    print("=" * 80)
    print(f"Found {len(csv_files)} CSV files to process")
    print("=" * 80)
    print()
    
    successful = 0
    failed = 0
    skipped = 0
    already_processed_count = 0
    
    for i, fname in enumerate(csv_files, 1):
        print("=" * 80)
        print(f"Processing file {i}/{len(csv_files)}: {fname}")
        print("=" * 80)
        
        file_path = DATA_DIR / fname
        trading_date = fname.replace(".csv", "")
        
        try:
            df = pd.read_csv(file_path)
            
            if "timestamp" not in df.columns:
                print(f"  Skipped (no timestamp column)")
                skipped += 1
                print()
                continue
            
            # Check if already processed - allows script to resume after interruptions
            if is_already_processed(df):
                print(f"  Already processed (fPrice column exists with data), skipping...")
                already_processed_count += 1
                print()
                continue
            
            # Store original timestamp column for writing back (preserve original format)
            original_timestamp_col = df["timestamp"].copy()
            
            # Parse timestamps - handle both full datetime and time-only formats
            # First try parsing as full datetime (YYYY-MM-DD HH:MM:SS)
            parsed_timestamps = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors='coerce')
            
            # If that fails, try combining with trading_date (for time-only format like "09:37:02")
            mask_na = parsed_timestamps.isna()
            if mask_na.any():
                # Check if remaining values look like time-only (HH:MM:SS)
                time_only_str = df.loc[mask_na, "timestamp"].astype(str)
                time_only = pd.to_datetime(
                    trading_date + " " + time_only_str,
                    format="%Y-%m-%d %H:%M:%S",
                    errors='coerce'
                )
                parsed_timestamps.loc[mask_na] = time_only
            
            print(f"  Parsed timestamps - valid: {parsed_timestamps.notna().sum()}, invalid: {parsed_timestamps.isna().sum()}")
            
            # Fetch SPX minute data once for the day
            print(f"  Fetching SPX data for {trading_date}...")
            minute_df = fetch_spx_day(trading_date)
            print(f"  Fetched {len(minute_df)} minute bars")
            
            # Compute prices with error handling
            print(f"  Computing prices for {len(parsed_timestamps)} timestamps...")
            prices = []
            for idx, ts in enumerate(parsed_timestamps):
                if pd.isna(ts):
                    prices.append("")
                else:
                    try:
                        price = price_at_timestamp(minute_df, ts)
                        prices.append(price)
                    except Exception as e:
                        # Timestamp might be before first available data, after last, or other error
                        print(f"    Warning: Could not get price for row {idx+1} (timestamp: {ts}): {e}")
                        prices.append("")
            
            # Restore timestamp column: use original if it had values, otherwise use formatted parsed timestamps
            # Convert original to string, handling NaN/empty values
            timestamp_to_write = original_timestamp_col.astype(str)
            timestamp_to_write = timestamp_to_write.replace('nan', '').replace('NaT', '').replace('None', '')
            
            # Where original was empty/NaN but we have valid parsed timestamps, use the formatted parsed version
            mask_empty_original = (timestamp_to_write.str.strip() == '') | original_timestamp_col.isna()
            mask_valid_parsed = parsed_timestamps.notna()
            mask_fill = mask_empty_original & mask_valid_parsed
            
            timestamp_to_write.loc[mask_fill] = parsed_timestamps.loc[mask_fill].apply(
                lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            df["timestamp"] = timestamp_to_write
            
            # Add or update fPrice column
            df["fPrice"] = prices
            df.to_csv(file_path, index=False)
            
            valid_prices = sum(1 for p in prices if p != '')
            print(f"  Successfully added fPrice column - {valid_prices}/{len(prices)} valid prices")
            successful += 1
            
            # Rate limit protection - Polygon free tier allows 5 calls/minute
            # 12 second delay ensures we stay within limits
            if i < len(csv_files):  # Don't sleep after last file
                print(f"  Waiting {SLEEP_SECONDS} seconds before next file...")
                time.sleep(SLEEP_SECONDS)
            
        except Exception as e:
            print(f"  ERROR processing {fname}: {e}")
            debug_log("continue_fetch_spx_prices.py:main", "File processing failed", {
                "filename": fname,
                "error": str(e),
                "error_type": type(e).__name__
            }, "E")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total files found: {len(csv_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped (no timestamp column): {skipped}")
    print(f"Already processed (fPrice exists): {already_processed_count}")
    print("=" * 80)
    print("DONE.")

if __name__ == "__main__":
    main()

