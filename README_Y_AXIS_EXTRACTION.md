# Y-Axis Price Extraction

To extract accurate prices from the SPX chart images, you need to provide the y-axis price range for each image.

## Option 1: Install Tesseract OCR (Recommended)

1. Download Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install it and add it to your PATH
3. The script will automatically extract y-axis ranges from images

## Option 2: Manual Range Specification

Create a dictionary mapping image filenames to (min_price, max_price) tuples:

```python
from pathlib import Path
from extract_signals import process_date

manual_ranges = {
    "2025-02-14_09-37-02_images_SPX-liqtest.png": (6116.0, 6122.0),
    "2025-02-14_09-59-00_images_SPX-liqtest.png": (6116.0, 6122.5),
    # Add more images as needed
}

signals = process_date(
    Path("spx-realtime-aws-clean"), 
    "2025-02-14",
    manual_ranges=manual_ranges
)
```

## How to Find Y-Axis Range

Look at the left side of each image where the price labels are displayed. Find the minimum and maximum price values shown on the y-axis.

For example:
- Image 1 shows prices from 6116 to 6122
- Image 2 shows prices from 6116 to above 6122 (use 6122.5 or higher)


