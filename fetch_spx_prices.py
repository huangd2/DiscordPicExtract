import os
import re
import time
import json
import pandas as pd
from polygon import RESTClient
from datetime import datetime
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
debug_log("fetch_spx_prices.py:22", "API key check", {"has_key":bool(API_KEY),"key_length":len(API_KEY) if API_KEY else 0}, "B")

if not API_KEY:
    raise ValueError(
        "POLYGON_API_KEY not found in environment variables. "
        "Please create a .env file with POLYGON_API_KEY=your_key_here"
    )

DATA_DIR = os.path.expanduser("~/Desktop/SPXsignal")
SLEEP_SECONDS = 12   # rate-limit safe (5 calls/min)

client = RESTClient(API_KEY)

DATE_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.csv$")

# =========================
# FUNCTIONS
# =========================
def fetch_spx_day(trading_date):
    """Fetch 1-minute SPY bars for a single trading day (SPY tracks SPX)"""
    debug_log("fetch_spx_prices.py:36", "fetch_spx_day entry", {"trading_date":trading_date}, "E")
    try:
        aggs = client.get_aggs(
            ticker="SPY",
            multiplier=1,
            timespan="minute",
            from_=trading_date,
            to=trading_date,
            limit=5000
        )
        debug_log("fetch_spx_prices.py:44", "API call success", {"ticker":"SPY","trading_date":trading_date,"agg_count":len(list(aggs)) if aggs else 0}, "E")
    except Exception as e:
        debug_log("fetch_spx_prices.py:49", "API call failed", {"ticker":"SPY","trading_date":trading_date,"error_type":type(e).__name__,"error_message":str(e)}, "E")
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
    debug_log("fetch_spx_prices.py:63", "price_at_timestamp called", {
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
        debug_log("fetch_spx_prices.py:price_at_timestamp", "Error in price lookup", {
            "ts": str(ts),
            "error": str(e),
            "df_range": f"{minute_df.index[0]} to {minute_df.index[-1]}" if len(minute_df) > 0 else "empty"
        }, "E")
        raise

# =========================
# MAIN LOOP
# =========================
for fname in sorted(os.listdir(DATA_DIR)):

    if not DATE_FILE_PATTERN.match(fname):
        continue

    file_path = os.path.join(DATA_DIR, fname)
    trading_date = fname.replace(".csv", "")
    debug_log("fetch_spx_prices.py:80", "Processing file", {"filename":fname,"trading_date":trading_date}, "C")

    print(f"Processing {fname}")

    df = pd.read_csv(file_path)

    if "timestamp" not in df.columns:
        print(f"  Skipped (no timestamp column)")
        continue

    # Store original timestamp column for writing back (preserve original format)
    original_timestamp_col = df["timestamp"].copy()
    
    # Debug: Check what we're reading
    print(f"  Columns: {list(df.columns)}")
    print(f"  Timestamp column sample (first 3): {df['timestamp'].head(3).tolist()}")
    print(f"  Timestamp column empty/NaN count: {df['timestamp'].isna().sum() + (df['timestamp'].astype(str).str.strip() == '').sum()}")
    
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
    
    debug_log("fetch_spx_prices.py:92", "CSV timestamps parsed", {
        "first_ts": str(parsed_timestamps.iloc[0]) if len(parsed_timestamps) > 0 and pd.notna(parsed_timestamps.iloc[0]) else "empty",
        "tz_aware": False,
        "na_count": parsed_timestamps.isna().sum(),
        "total_count": len(parsed_timestamps)
    }, "E")
    
    print(f"  Parsed timestamps - valid: {parsed_timestamps.notna().sum()}, invalid: {parsed_timestamps.isna().sum()}")

    # Fetch SPX minute data once for the day
    minute_df = fetch_spx_day(trading_date)
    debug_log("fetch_spx_prices.py:98", "Polygon data prepared", {
        "first_ts": str(minute_df.index[0]) if len(minute_df) > 0 else "empty",
        "tz_aware": minute_df.index.tz is not None if len(minute_df) > 0 else False
    }, "E")

    # Compute prices with error handling
    prices = []
    for idx, ts in enumerate(parsed_timestamps):
        if pd.isna(ts):
            prices.append("")
            debug_log("fetch_spx_prices.py:price_loop", "Skipping NaT timestamp", {"row": idx}, "E")
        else:
            try:
                price = price_at_timestamp(minute_df, ts)
                prices.append(price)
            except Exception as e:
                # Timestamp might be before first available data, after last, or other error
                print(f"    Warning: Could not get price for row {idx+1} (timestamp: {ts}): {e}")
                debug_log("fetch_spx_prices.py:price_loop", "Price lookup failed", {
                    "row": idx,
                    "ts": str(ts),
                    "error": str(e),
                    "error_type": type(e).__name__
                }, "E")
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
    
    # Write back to same file
    df["fPrice"] = prices
    df.to_csv(file_path, index=False)
    
    print(f"  Written - timestamps: {df['timestamp'].notna().sum()} valid, fPrice: {sum(1 for p in prices if p != '')} valid")

    print(f"  Added fPrice column ({len(prices)} rows)")

    # Rate limit protection
    time.sleep(SLEEP_SECONDS)

print("DONE.")
