# Extract Triangles with Risk Levels

## Overview

This script extracts triangles (buy/sell signals) from SPX chart images and determines their risk levels by comparing triangle colors to a reference colorbar. The colorbar indicates risk levels: green (low risk) at the bottom, red (high risk) at the top, with medium risk in between.

## Features

- **Triangle Detection**: Automatically detects the last/rightmost triangle in each image
- **Color Extraction**: Uses triangle mask to extract accurate colors from triangle interior (not background)
- **Risk Level Classification**: Compares triangle colors to colorbar to determine risk level (low/medium/high)
- **Price Extraction**: Extracts price values from y-axis coordinates
- **Timestamp Parsing**: Extracts timestamps from image filenames

## Requirements

All dependencies are in `requirements.txt`:
- `opencv-python` (cv2)
- `numpy`
- `PIL` (Pillow)
- `easyocr` (optional, for better OCR)
- `pytesseract` (optional, for OCR fallback)

The script also requires `extract_signals.py` to be in the same directory.

## Setup

1. Ensure you have a `colorbar.png` file on your Desktop, or specify a custom path
2. The colorbar should be vertical with:
   - Green at the bottom (low risk)
   - Red at the top (high risk)
   - Gradient in between (medium risk)

## Usage

### Basic Usage

Process images for a specific date:

```bash
python extract_triangles_with_risk.py --date 2025-02-14
```

### Command-Line Arguments

```bash
python extract_triangles_with_risk.py [OPTIONS]
```

**Options:**
- `--date DATE`: Date to process in YYYY-MM-DD format (default: 2025-02-14)
- `--folder FOLDER`: Folder containing images (default: spx-realtime-aws-clean)
- `--colorbar COLORBAR`: Path to colorbar image (default: Desktop/colorbar.png)
- `--help`: Show help message

### Examples

**1. Process default date (2025-02-14):**
```bash
python extract_triangles_with_risk.py
```

**2. Process a different date:**
```bash
python extract_triangles_with_risk.py --date 2025-02-18
```

**3. Use custom folder:**
```bash
python extract_triangles_with_risk.py --date 2025-02-19 --folder "path/to/images"
```

**4. Use custom colorbar:**
```bash
python extract_triangles_with_risk.py --date 2025-02-14 --colorbar "C:\path\to\colorbar.png"
```

**5. Combine options:**
```bash
python extract_triangles_with_risk.py --date 2025-02-20 --folder "spx-realtime-aws-clean" --colorbar "C:\Users\Vivian\Desktop\colorbar.png"
```

## Output

The script prints a formatted table to the console with the following columns:

- **Timestamp**: Date and time when the triangle appeared (from filename)
- **Price**: SPX price at the triangle location
- **Color (RGB)**: RGB color values of the triangle
- **Risk Level**: Risk classification (low/medium/high)

### Example Output

```
================================================================================
Extracted Triangles with Risk Levels
================================================================================
Timestamp            Price        Color (RGB)          Risk Level  
--------------------------------------------------------------------------------
2025-02-14 09:37:02  6116.98      (0, 128, 0)          low         
2025-02-14 09:59:00  6120.75      (66, 125, 66)        low         
2025-02-14 10:03:02  6117.86      (0, 128, 0)          low         
2025-02-14 14:29:02  6117.92      (212, 129, 0)        medium      
2025-02-14 15:07:32  6115.73      (192, 189, 0)        medium      
================================================================================

Total triangles extracted: 16
================================================================================
```

## How It Works

### 1. Image Processing
- Loads images matching the date pattern: `YYYY-MM-DD_*.png`
- Extracts y-axis price range using OCR
- Detects triangles using multiple detection strategies

### 2. Triangle Detection
- Finds all triangles in each image
- Identifies the last/rightmost triangle (newest signal)
- Uses triangle vertices to create a precise mask

### 3. Color Extraction
- Creates a triangle mask from vertices
- Samples pixels only from inside the triangle (not background)
- Filters out dark grid line pixels
- Uses median of bright pixels for robust color calculation

### 4. Risk Level Determination
- Loads colorbar image and extracts left 1/3 width
- Searches for triangle color in the colorbar
- Maps position to risk level:
  - **Upper 1/3** of colorbar (red zone) → `high` risk
  - **Middle 1/3** → `medium` risk
  - **Lower 1/3** (green zone) → `low` risk

### 5. Price Extraction
- Converts y-coordinate to price using extracted y-axis range
- Handles cases where y-axis extraction fails gracefully

## File Structure

```
extract_triangles_with_risk.py    # Main script
extract_signals.py                 # Required dependency (triangle detection)
colorbar.png                       # Reference colorbar (on Desktop by default)
spx-realtime-aws-clean/            # Image folder
  ├── 2025-02-14_09-37-02_*.png
  ├── 2025-02-14_09-59-00_*.png
  └── ...
```

## Troubleshooting

### No triangles detected
- Check that images exist for the specified date
- Verify image filenames match pattern: `YYYY-MM-DD_HH-MM-SS_*.png`
- Ensure images contain visible triangle markers
- Check that triangle area is within detection range (30-10000 pixels)

### Risk levels seem incorrect
- Verify colorbar.png exists and is accessible
- Check colorbar orientation (green at bottom, red at top)
- Ensure triangle colors are being extracted correctly (not white/background)
- Verify colorbar has the expected gradient

### Price extraction fails
- Check that y-axis labels are visible in images
- OCR may need adjustment if labels are unclear
- Script will use default grid boundaries if y-axis extraction fails

### Color extraction issues
- If triangles show white color (255, 255, 255), the triangle mask may not be working correctly
- Check that triangle detection is finding the correct shapes
- Verify triangle vertices are being calculated properly

## Technical Details

### Triangle Detection
- Uses multiple detection strategies: high saturation, bright colored, color-based, and edge-based
- Filters by area (30-10000 pixels) and aspect ratio
- Removes duplicate detections

### Color Matching
- Uses Euclidean distance in RGB space
- Searches for exact matches first (within 3 RGB units tolerance)
- Falls back to closest match if exact match not found
- Uses middle column of colorbar strip for stable matching

### Triangle Mask
- Creates mask using `cv2.fillPoly()` with triangle vertices
- Samples only pixels inside the triangle shape
- Filters out dark pixels (likely grid lines) using threshold of 80
- Uses median of bright pixels for color calculation

## Integration

This script can be integrated with other parts of the pipeline:
- Uses functions from `extract_signals.py` for triangle detection
- Can be called programmatically:
  ```python
  from extract_triangles_with_risk import extract_triangles_with_risk
  from pathlib import Path
  
  results = extract_triangles_with_risk(
      folder_path=Path("spx-realtime-aws-clean"),
      date_str="2025-02-14"
  )
  ```

## Notes

- The script processes images sequentially to track new triangles
- Timestamp from filename represents when the triangle appeared on the x-axis
- Triangle color extraction uses triangle mask to avoid background contamination
- Risk levels are determined by direct color matching to the colorbar position

