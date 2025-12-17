# Fetch SPX Prices from Polygon API

This script fetches SPX (S&P 500 Index) prices from Polygon.io API and adds them to your signal CSV files.

**Note:** Due to API limitations on the free tier, this script uses **SPY** (SPDR S&P 500 ETF Trust) as a proxy for SPX. SPY closely tracks the S&P 500 Index and provides accurate price data for signal analysis.

## Setup

### 1. Install Dependencies

Make sure you have the required package installed:

```bash
pip install polygon-api-client pandas
```

Or install from the project's requirements.txt (which includes polygon-api-client).

### 2. Get Your Polygon API Key

1. Sign up for a free account at [Polygon.io](https://polygon.io/)
2. Navigate to your dashboard to get your API key
3. The free tier allows **5 API calls per minute**

### 3. Configure the API Key

**The script uses environment variables for security (no API keys in code!)**

1. Create a `.env` file in the project root (if it doesn't exist)
2. Add your Polygon API key:

```
POLYGON_API_KEY=your_actual_api_key_here
```

**Important:** The `.env` file is already in `.gitignore`, so your API key will never be committed to GitHub.

If you see an error about `POLYGON_API_KEY` not found, make sure:
- The `.env` file exists in the project root directory
- The file contains `POLYGON_API_KEY=your_key_here` (no quotes around the key)
- You've installed `python-dotenv` (included in requirements.txt)

## Usage

### Directory Structure

The script expects CSV files in the following location:

```
~/Desktop/SPXsignal/
├── 2024-01-15.csv
├── 2024-01-16.csv
├── 2024-01-17.csv
└── ...
```

Each CSV file should:
- Be named in `YYYY-MM-DD.csv` format
- Contain a `timestamp` column with time values (e.g., "09:30:00", "10:15:30")

### Running the Script

```bash
python fetch_spx_prices.py
```

The script will:
1. Process each date CSV file in `~/Desktop/SPXsignal/`
2. Fetch 1-minute SPY bar data from Polygon for that trading day (SPY is used as a proxy for SPX due to API limitations)
3. Match each timestamp in your CSV to the closest available SPY price
4. Add a new `fPrice` column with the SPY close price at that timestamp
5. Save the updated CSV back to the same file

### Rate Limiting

The script includes a 12-second delay between files to respect Polygon's free tier limit of 5 calls per minute. This means:
- **Processing time**: ~12 seconds per file
- **Example**: 10 files = ~2 minutes total

## Output

Each CSV file will be updated with a new `fPrice` column containing the SPX close price at each timestamp.

### Example

**Before:**
```csv
timestamp,signal_type,value
09:30:00,BUY,100
10:15:30,SELL,150
```

**After:**
```csv
timestamp,signal_type,value,fPrice
09:30:00,BUY,100,4850.25
10:15:30,SELL,150,4855.75
```

## Troubleshooting

### "No SPX data for YYYY-MM-DD"

This means Polygon doesn't have data for that date. Possible reasons:
- Weekend or holiday (non-trading day)
- Date is too recent (data may not be available yet)
- Date is before Polygon's historical data coverage

### "Skipped (no timestamp column)"

The CSV file doesn't have a `timestamp` column. Make sure your CSV files include this column.

### API Rate Limit Errors

If you see rate limit errors:
- Increase `SLEEP_SECONDS` on line 13 (e.g., to 15 or 20 seconds)
- The free tier is 5 calls/minute, so minimum delay should be 12 seconds

## Notes

- The script uses the **last available close price** at or before each timestamp
- **SPY is used as a proxy for SPX** due to API limitations on the free tier (SPY closely tracks SPX)
- Data is fetched at 1-minute granularity
- The script processes files in alphabetical order (by date)
- Timestamps can be in full datetime format (`YYYY-MM-DD HH:MM:SS`) or time-only format (`HH:MM:SS`)

