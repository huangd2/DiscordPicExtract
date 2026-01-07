# Extract Risk Values from Images

## Overview

This script extracts risk values from the right-most triangle marker in each chart image and merges them into the corresponding daily CSV signal files. The risk value is determined by matching the triangle's fill color to the vertical risk colorbar in the same image.

## How It Works

### 1. Image Processing
- **Input**: Images from `spx-realtime-aws-clean` folder
- **Filename Pattern**: `YYYY-MM-DD_HH-MM-SS_images_SPX-liqtest.png` (or `.jpg`, `.jpeg`, `.webp`)
- **Process**:
  - Parses timestamp from filename
  - Crops the main plot area and the vertical risk colorbar
  - Detects triangle markers (BUY/SELL signals)
  - Identifies the right-most triangle (latest signal)
  - Extracts the triangle's fill color
  - Matches the color to the colorbar to determine risk value (0.0 to 0.4)

### 2. Risk Extraction
- The script builds a color lookup table (LUT) from each image's own colorbar
- Uses LAB color space for accurate color matching
- Risk range: 0.0 (bottom of colorbar) to 0.4 (top of colorbar)
- Removes red '+' markers that might overlap with triangles

### 3. CSV Merging
- **Input**: Daily CSV files in `SPXsignal` folder (format: `YYYY-MM-DD.csv`)
- **Merge Strategy**:
  - **Primary**: Exact merge on timestamp column (if available)
    - Looks for columns named: `timestamp`, `time`, or `datetime`
    - Parses timestamps and matches them with image timestamps
  - **Fallback**: Chronological row order (if no timestamp column exists)
    - Assumes CSV rows are already in chronological order
    - Assigns risks sequentially to rows

### 4. Output
- Creates new CSV files with suffix `_with_risk.csv` alongside originals
- Also creates a master file: `image_extracted_risks.csv` with all extracted data
- Preserves all original columns and adds the `risk` column

## Configuration

Edit these constants at the top of `extract_risk_from_images.py` if needed:

```python
IMAGES_DIR = Path(r"C:\Users\Vivian\Desktop\DiscordPicExtract\spx-realtime-aws-clean")
SIGNALS_DIR = Path(r"C:\Users\Vivian\Desktop\SPXsignal")

# Crop regions (relative coordinates 0.0-1.0)
PLOT_CROP = dict(y0=0.08, y1=0.92, x0=0.07, x1=0.90)      # main plot area
COLORBAR_CROP = dict(y0=0.12, y1=0.90, x0=0.92, x1=0.965)  # colorbar region

# Risk range
RISK_MIN = 0.0
RISK_MAX = 0.4

# Triangle detection constraints (pixels)
TRI_AREA_MIN = 120
TRI_AREA_MAX = 2500
```

## Usage

```bash
python extract_risk_from_images.py
```

## Requirements

All dependencies are already in `requirements.txt`:
- `opencv-python` (cv2)
- `numpy`
- `pandas`

## Output Files

1. **`image_extracted_risks.csv`**: Master file containing all extracted risk values with:
   - `timestamp`: Full datetime from image filename
   - `date`: Date string (YYYY-MM-DD)
   - `type`: Triangle type (BUY or SELL)
   - `risk`: Extracted risk value (0.0 to 0.4)
   - `image`: Source image filename

2. **`YYYY-MM-DD_with_risk.csv`**: For each daily CSV file, a new file with the `risk` column added

## Notes

- The script processes all images in the `-clean` folder and matches them to CSV files by date
- If an image has no detectable triangles, it's skipped
- If a CSV file has no matching images for that date, it's skipped
- The script handles missing timestamps gracefully
- Triangle detection uses contour analysis and area constraints to filter false positives

## Troubleshooting

### No signals extracted
- Check that images are in the correct folder
- Verify image filenames match the expected pattern: `YYYY-MM-DD_HH-MM-SS_...`
- Ensure images contain visible triangle markers

### Risk values seem incorrect
- Adjust `PLOT_CROP` and `COLORBAR_CROP` if the chart layout differs
- Check that `RISK_MIN` and `RISK_MAX` match your colorbar range
- Verify triangle detection with `TRI_AREA_MIN` and `TRI_AREA_MAX`

### Merge issues
- Ensure CSV files have date-based filenames (`YYYY-MM-DD.csv`)
- Check that timestamp columns are parseable by pandas
- Verify that image timestamps match CSV timestamps for the same date

