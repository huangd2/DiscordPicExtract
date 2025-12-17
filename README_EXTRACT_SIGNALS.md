# SPX Signal Extraction

A tool for extracting buy/sell signals from SPX chart images by detecting colored triangles and extracting price information.

## Description

This script processes SPX chart images sequentially to detect buy/sell signal triangles and extract:
- Signal number
- Timestamp (from filename)
- Price (calculated from y-axis position)
- Buy/Sell type (based on triangle orientation)

## Features

- **Triangle Detection**: Detects colored triangles (buy/sell signals) using multiple detection strategies
- **Price Extraction**: Extracts price values by detecting y-axis labels using OCR (EasyOCR/Tesseract)
- **Sequential Processing**: Processes images in chronological order to track new signals
- **Line Pixel Filtering**: Filters out price line pixels for better color extraction
- **CSV Export**: Exports results to CSV format with all signal information

## Prerequisites

- Python 3.8 or higher
- OpenCV (`opencv-python`)
- NumPy
- Pillow (PIL)
- EasyOCR or Tesseract OCR (for price extraction)

### Installing OCR Dependencies

**Option 1: EasyOCR (Recommended)**
```bash
pip install easyocr
```

**Option 2: Tesseract OCR**
```bash
# Install Tesseract OCR on your system first
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

pip install pytesseract
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your images are in a folder with filenames in the format:
   ```
   YYYY-MM-DD_HH-MM-SS_originalname.png
   ```
   Example: `2025-02-14_09-37-02_images_SPX-liqtest.png`

## Usage

### Basic Usage

Process images for a specific date:
```bash
python extract_signals.py --folder spx-realtime-aws-clean --date 2025-02-14
```

### Arguments

- `--folder`: Folder containing images (default: `spx-realtime-aws-clean`)
- `--date`: Date to process in YYYY-MM-DD format (default: `2025-02-14`)

### Examples

**Example 1: Process default folder and date**
```bash
python extract_signals.py
```

**Example 2: Process specific folder and date**
```bash
python extract_signals.py --folder my-images --date 2025-02-15
```

**Example 3: Process different clean folder**
```bash
python extract_signals.py --folder spx-clean --date 2025-02-14
```

## Output

The script generates:

1. **CSV File**: `Desktop/SPXsignal/{date}.csv`
   - Columns: `signal#`, `timestamp`, `price`, `buy/sell`
   - Example:
     ```csv
     signal#,timestamp,price,buy/sell
     1,2025-02-14 09:37:02,6116.98,Buy
     2,2025-02-14 09:59:00,6120.75,Sell
     ```

2. **Console Output**: 
   - Processing progress for each image
   - Y-axis price range detection
   - Detected signals with prices
   - Summary table

## How It Works

### 1. Triangle Detection
- Uses multiple detection strategies (color-based, edge-based, saturation-based)
- Detects triangles in the right portion of the chart (grid area)
- Filters by size and aspect ratio to avoid false positives
- Determines orientation (upward = Buy, inverted = Sell)

### 2. Price Extraction
- Extracts y-axis price range using OCR (EasyOCR or Tesseract)
- Processes each image individually to get accurate price ranges
- Converts triangle y-coordinate to price value using:
  - Triangle center position (adjusted for orientation)
  - Detected min/max prices from y-axis
  - Grid boundaries

### 3. Sequential Processing
- Processes images in chronological order
- Tracks previous triangles to identify new signals
- Extracts y-axis range from each image for accurate price calculation

### 4. Color Extraction
- Samples color from triangle region
- Filters out line pixels (price lines) for better color accuracy
- Uses median color value for robustness

## Output Format

### CSV Structure
```csv
signal#,timestamp,price,buy/sell
1,2025-02-14 09:37:02,6116.98,Buy
2,2025-02-14 09:59:00,6120.75,Sell
3,2025-02-14 10:03:02,6117.86,Buy
```

### Console Output Example
```
============================================================
Extracting signals for date: 2025-02-14
Folder: spx-realtime-aws-clean
============================================================
Found 16 images for 2025-02-14
Processing images sequentially...

Processing 1/16: 2025-02-14_09-37-02_images_SPX-liqtest.png
  Y-axis range: 6116.00 - 6122.00
  Signal 1: Buy at 2025-02-14 09:37:02, price: 6116.98

...

============================================================
Extracted Signals Table
============================================================
Signal#  Timestamp            Price        Buy/Sell  
------------------------------------------------------------
1        2025-02-14 09:37:02  6116.98      Buy       
2        2025-02-14 09:59:00  6120.75      Sell      
...
============================================================

Total signals extracted: 16
```

## Troubleshooting

### No signals detected
- Check that images contain visible triangles
- Verify images are in the correct format (PNG)
- Ensure images have proper timestamps in filename

### Price extraction fails
- Install EasyOCR or Tesseract OCR
- Check that y-axis labels are visible and readable
- Try different preprocessing methods (script tries multiple automatically)

### Incorrect prices
- Y-axis range detection may need adjustment
- Check that grid boundaries are correctly identified
- Verify triangle center calculation (uses geometric center adjusted for orientation)
- **Known Issue:** Price extraction may be inaccurate during rapid price movements (fast drops or increases). The OCR-based y-axis extraction and triangle position mapping may not correctly capture prices during volatile periods. Manual verification is recommended for signals during high volatility.

## Technical Details

### Triangle Detection
- Detects triangles using contour approximation
- Filters by area (30-10000 pixels)
- Checks aspect ratio to avoid elongated shapes
- Uses multiple color detection strategies

### Price Calculation
- Extracts y-axis labels using OCR
- Maps y-coordinates to price values
- Adjusts triangle center based on orientation:
  - Buy (upward): center shifted toward base (lower than tip)
  - Sell (inverted): center shifted toward base (higher than tip)

### Color Extraction
- Samples 5-pixel radius around triangle center
- Filters line pixels using:
  - Dark pixel thresholding
  - Edge detection
  - Morphological line detection
- Uses median color for robustness

## File Structure

```
extract_signals.py          # Main script
requirements.txt            # Python dependencies
README_EXTRACT_SIGNALS.md  # This file
```

## License

See main repository license.

