"""Extract buy/sell signals from SPX chart images."""
import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    # Initialize EasyOCR reader (English only for faster loading)
    try:
        EASYOCR_READER = easyocr.Reader(['en'], gpu=False)
    except:
        EASYOCR_READER = None
        EASYOCR_AVAILABLE = False
except ImportError:
    EASYOCR_AVAILABLE = False
    EASYOCR_READER = None


def parse_timestamp_from_filename(filename: str) -> Optional[datetime]:
    """Parse timestamp from filename format: YYYY-MM-DD_HH-MM-SS_originalname.ext"""
    try:
        timestamp_str = filename[:19]
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        return dt
    except (ValueError, IndexError):
        return None


def detect_triangles(image_path: Path) -> List[Dict]:
    """
    Detect triangles in the image and return their properties.
    Returns list of dicts with keys: center, orientation, color, risk_level
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        return []
    
    # Convert to RGB for processing
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]
    
    # Create a mask for the grid area (right side of image, typically 50-95% of width)
    grid_left = int(w * 0.4)
    grid_right = int(w * 0.98)
    grid_top = int(h * 0.1)
    grid_bottom = int(h * 0.9)
    
    # Extract grid region
    grid_region = img_rgb[grid_top:grid_bottom, grid_left:grid_right]
    
    if grid_region.size == 0:
        return []
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(grid_region, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(grid_region, cv2.COLOR_RGB2GRAY)
    
    triangles = []
    
    # Try multiple detection strategies
    strategies = [
        {
            'name': 'high_saturation',
            'mask': (hsv[:, :, 1] > 80) & (hsv[:, :, 2] > 80) & (hsv[:, :, 2] < 240)
        },
        {
            'name': 'bright_colored',
            'mask': (np.abs(hsv[:, :, 0].astype(int) - 90) > 20) & (hsv[:, :, 2] > 100)
        },
        {
            'name': 'color_based',
            'mask': (
                ((hsv[:, :, 0] >= 40) & (hsv[:, :, 0] <= 80)) |  # Green
                ((hsv[:, :, 0] >= 15) & (hsv[:, :, 0] < 40)) |  # Yellow
                ((hsv[:, :, 0] >= 0) & (hsv[:, :, 0] < 15)) |   # Orange/Red
                (hsv[:, :, 0] > 160)  # Red (wraps around)
            ) & (hsv[:, :, 1] > 50) & (hsv[:, :, 2] > 80)
        },
        {
            'name': 'edge_based',
            'mask': None  # Will use Canny edges
        }
    ]
    
    all_contours = []
    
    for strategy in strategies:
        if strategy['mask'] is not None:
            mask = strategy['mask'].astype(np.uint8) * 255
        else:
            edges = cv2.Canny(gray, 50, 150)
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            mask = edges
        
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        all_contours.extend(contours)
    
    # Process all found contours
    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area < 30 or area > 10000:
            continue
        
        x, y, w_cont, h_cont = cv2.boundingRect(contour)
        aspect_ratio = max(w_cont, h_cont) / max(min(w_cont, h_cont), 1)
        if aspect_ratio > 3:
            continue
        
        for epsilon_factor in [0.02, 0.03, 0.04, 0.05]:
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) == 3:
                M = cv2.moments(contour)
                if M["m00"] == 0:
                    continue
                    
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                center_x = grid_left + cx
                center_y = grid_top + cy
                
                pts = approx.reshape(3, 2)
                pts_full = pts.copy()
                pts_full[:, 0] += grid_left
                pts_full[:, 1] += grid_top
                
                y_coords = pts[:, 1]
                sorted_y = sorted(y_coords)
                y_min = sorted_y[0]
                y_max = sorted_y[2]
                y_mid = sorted_y[1]
                
                dist_to_top = abs(y_mid - y_min)
                dist_to_bottom = abs(y_mid - y_max)
                
                if dist_to_bottom < dist_to_top:
                    orientation = "buy"
                else:
                    orientation = "sell"
                
                # Calculate center y based on triangle orientation
                # For buy (upward triangle): tip is at top (y_min), center should be lower (toward base at y_max)
                # For sell (inverted triangle): tip is at bottom (y_max), center should be higher (toward base at y_min)
                if orientation == "buy":
                    # Shift center toward the base (larger y value)
                    center_y_geometric = grid_top + (y_min + 2 * y_max) / 3
                else:  # sell
                    # Shift center toward the base (smaller y value)
                    center_y_geometric = grid_top + (2 * y_min + y_max) / 3
                
                center_y = int(center_y_geometric)
                
                center_y_img = max(0, min(center_y, img_rgb.shape[0] - 1))
                center_x_img = max(0, min(center_x, img_rgb.shape[1] - 1))
                
                # Sample from a larger region to get better color representation
                sample_radius = 5
                y_start = max(0, center_y_img - sample_radius)
                y_end = min(img_rgb.shape[0], center_y_img + sample_radius + 1)
                x_start = max(0, center_x_img - sample_radius)
                x_end = min(img_rgb.shape[1], center_x_img + sample_radius + 1)
                
                color_region = img_rgb[y_start:y_end, x_start:x_end]
                
                if color_region.size > 0:
                    # Convert to grayscale to detect line pixels
                    gray_region = cv2.cvtColor(color_region, cv2.COLOR_RGB2GRAY)
                    
                    # Detect line pixels using multiple methods
                    # Method 1: Very dark pixels (likely lines)
                    dark_threshold = 80
                    dark_mask = gray_region < dark_threshold
                    
                    # Method 2: Edge detection to find line edges
                    edges = cv2.Canny(gray_region, 50, 150)
                    edge_mask = edges > 0
                    
                    # Method 3: Detect thin horizontal/vertical lines
                    # Horizontal lines
                    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
                    horizontal_lines = cv2.morphologyEx((gray_region < 100).astype(np.uint8) * 255, 
                                                       cv2.MORPH_OPEN, horizontal_kernel)
                    horizontal_mask = horizontal_lines > 0
                    
                    # Vertical lines
                    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 9))
                    vertical_lines = cv2.morphologyEx((gray_region < 100).astype(np.uint8) * 255,
                                                     cv2.MORPH_OPEN, vertical_kernel)
                    vertical_mask = vertical_lines > 0
                    
                    # Combine all line masks
                    line_mask = dark_mask | edge_mask | horizontal_mask | vertical_mask
                    
                    # Create mask for non-line pixels
                    non_line_mask = ~line_mask
                    
                    # Extract colors from non-line pixels only
                    color_region_flat = color_region.reshape(-1, 3)
                    non_line_pixels = color_region_flat[non_line_mask.reshape(-1)]
                    
                    if len(non_line_pixels) > 0:
                        # Use median instead of mean for better robustness
                        color_rgb = np.median(non_line_pixels, axis=0).astype(int)
                    else:
                        # If all pixels are lines, use mean of all pixels but exclude very dark ones
                        bright_pixels = color_region_flat[gray_region.reshape(-1) > 50]
                        if len(bright_pixels) > 0:
                            color_rgb = np.median(bright_pixels, axis=0).astype(int)
                        else:
                            color_rgb = np.mean(color_region_flat, axis=0).astype(int)
                else:
                    color_rgb = img_rgb[center_y_img, center_x_img]
                
                r, g, b = color_rgb
                
                # Risk level estimation removed
                risk_level = None
                
                triangles.append({
                    'center': (center_x, center_y),
                    'orientation': orientation,
                    'color': tuple(color_rgb),
                    'area': area,
                    'vertices': pts_full.tolist()
                })
                break
    
    # Remove duplicates
    unique_triangles = []
    for triangle in triangles:
        is_duplicate = False
        for existing in unique_triangles:
            dist = np.sqrt((triangle['center'][0] - existing['center'][0])**2 + 
                          (triangle['center'][1] - existing['center'][1])**2)
            if dist < 30:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_triangles.append(triangle)
    
    unique_triangles.sort(key=lambda t: t['center'][0], reverse=True)
    
    return unique_triangles


def extract_y_axis_range(image_path: Path) -> Optional[Tuple[float, float, int, int]]:
    """
    Extract the y-axis price range by detecting y-axis labels using OCR.
    Returns: (min_price, max_price, y_top, y_bottom) or None
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]
    
    # Y-axis is on the left side
    y_axis_left = 0
    y_axis_right = int(w * 0.35)
    y_axis_region = img_rgb[:, y_axis_left:y_axis_right]
    
    grid_top = int(h * 0.12)
    grid_bottom = int(h * 0.88)
    
    all_detected_prices = []
    
    # Try EasyOCR first
    if EASYOCR_AVAILABLE and EASYOCR_READER is not None:
        try:
            # Try different y-axis widths
            for y_axis_width in [0.25, 0.3, 0.35, 0.2]:
                y_axis_left = 0
                y_axis_right = int(w * y_axis_width)
                y_axis_region = img_rgb[:, y_axis_left:y_axis_right]
                
                grid_y_start = int(h * 0.1)
                grid_y_end = int(h * 0.9)
                y_axis_grid_region = img_rgb[grid_y_start:grid_y_end, y_axis_left:y_axis_right]
                
                regions_to_try = [
                    ("Full y-axis", y_axis_region, 0),
                    ("Grid-focused", y_axis_grid_region, grid_y_start)
                ]
                
                for region_name, region_img, y_offset in regions_to_try:
                    for scale in [2, 3]:
                        upscaled = cv2.resize(region_img, 
                                             (region_img.shape[1] * scale, region_img.shape[0] * scale), 
                                             interpolation=cv2.INTER_CUBIC)
                        
                        gray_axis = cv2.cvtColor(upscaled, cv2.COLOR_RGB2GRAY)
                        
                        preprocess_methods = [
                            ("Original", gray_axis),
                            ("CLAHE", cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(gray_axis)),
                            ("Threshold", cv2.threshold(gray_axis, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
                            ("Adaptive", cv2.adaptiveThreshold(gray_axis, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
                        ]
                        
                        for method_name, processed_img in preprocess_methods:
                            try:
                                results = EASYOCR_READER.readtext(processed_img, detail=1, paragraph=False, width_ths=0.3, height_ths=0.3)
                                
                                for (bbox, text, confidence) in results:
                                    if confidence > 0.1:
                                        price_pattern = r'\b\d{4,5}(?:\.\d{1,2})?\b'
                                        prices = re.findall(price_pattern, text)
                                        if not prices:
                                            alt_pattern = r'\d{4,}'
                                            prices = re.findall(alt_pattern, text)
                                        if not prices:
                                            any_numbers = re.findall(r'\d+', text)
                                            prices = [n for n in any_numbers if len(n) >= 4]
                                        
                                        if prices:
                                            for p in prices:
                                                try:
                                                    price_val = float(p)
                                                    if 4000 <= price_val <= 7000:
                                                        bbox_y = (bbox[0][1] + bbox[2][1]) / 2 / scale + y_offset
                                                        all_detected_prices.append((price_val, bbox_y))
                                                except:
                                                    continue
                            except Exception:
                                continue
                            
                            if len(all_detected_prices) >= 3:
                                break
                        if len(all_detected_prices) >= 3:
                            break
                    if len(all_detected_prices) >= 3:
                        break
                if len(all_detected_prices) >= 3:
                    break
        except Exception as e:
            pass
    
    # Try Tesseract as fallback
    if len(all_detected_prices) < 2 and TESSERACT_AVAILABLE:
        try:
            gray_axis = cv2.cvtColor(y_axis_region, cv2.COLOR_RGB2GRAY)
            _, thresh1 = cv2.threshold(gray_axis, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresh2 = cv2.adaptiveThreshold(gray_axis, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                           cv2.THRESH_BINARY, 11, 2)
            
            all_prices = []
            for thresh_img in [thresh1, thresh2]:
                try:
                    for psm in [6, 7, 8, 11]:
                        try:
                            text = pytesseract.image_to_string(thresh_img, config=f'--psm {psm} -c tessedit_char_whitelist=0123456789.')
                            price_pattern = r'\b\d{4,5}(?:\.\d{1,2})?\b'
                            prices = re.findall(price_pattern, text)
                            if prices:
                                all_prices.extend([float(p) for p in prices])
                        except:
                            continue
                except:
                    continue
            
            if len(all_prices) >= 2:
                unique_prices = sorted(set(all_prices))
                if len(unique_prices) >= 2:
                    min_price = min(unique_prices)
                    max_price = max(unique_prices)
                    # Estimate grid boundaries
                    y_top = grid_top
                    y_bottom = grid_bottom
                    return (min_price, max_price, y_top, y_bottom)
        except:
            pass
    
    # If we have prices with y positions, use them
    if len(all_detected_prices) >= 2:
        all_detected_prices.sort(key=lambda x: x[1])
        prices_sorted = [p[0] for p in all_detected_prices]
        y_positions = [p[1] for p in all_detected_prices]
        
        min_price = min(prices_sorted)
        max_price = max(prices_sorted)
        
        y_top = int(min(y_positions))
        y_bottom = int(max(y_positions))
        
        y_top = max(0, y_top - 20)
        y_bottom = min(h, y_bottom + 20)
        
        return (min_price, max_price, y_top, y_bottom)
    
    return None


def y_to_price(y: int, min_price: float, max_price: float, y_top: int, y_bottom: int) -> Optional[float]:
    """Convert y-coordinate to price value."""
    if y_bottom == y_top:
        return None
    
    normalized = (y - y_top) / (y_bottom - y_top)
    normalized = max(0.0, min(1.0, normalized))
    
    price = max_price - normalized * (max_price - min_price)
    
    return price


def extract_signals_sequential(folder_path: Path, date_str: str) -> List[Dict]:
    """
    Extract signals sequentially from each image for a given date.
    Returns list of signal dictionaries with prices.
    """
    pattern = f"{date_str}_*.png"
    image_files = sorted(folder_path.glob(pattern))
    
    if not image_files:
        print(f"No images found for date {date_str}")
        return []
    
    print(f"Found {len(image_files)} images for {date_str}")
    print("Processing images sequentially...\n")
    
    all_signals = []
    signal_number = 1
    previous_triangles = []
    
    for i, image_path in enumerate(image_files):
        timestamp = parse_timestamp_from_filename(image_path.name)
        if not timestamp:
            continue
        
        print(f"Processing {i+1}/{len(image_files)}: {image_path.name}")
        
        # Extract y-axis range from THIS image
        y_axis_info = extract_y_axis_range(image_path)
        
        image_min_price = None
        image_max_price = None
        image_y_top = None
        image_y_bottom = None
        
        if y_axis_info:
            image_min_price, image_max_price, image_y_top, image_y_bottom = y_axis_info
            print(f"  Y-axis range: {image_min_price:.2f} - {image_max_price:.2f}")
        else:
            img = cv2.imread(str(image_path))
            if img is not None:
                h, w = img.shape[:2]
                image_y_top = int(h * 0.15)
                image_y_bottom = int(h * 0.85)
                print(f"  Warning: Could not extract y-axis range. Using default grid boundaries.")
        
        # Detect triangles in current image
        triangles = detect_triangles(image_path)
        
        if not triangles:
            print(f"  No triangles detected")
            continue
        
        # Find the new triangle (rightmost one not in previous image)
        if i == 0:
            new_triangle = max(triangles, key=lambda t: t['center'][0])
        else:
            rightmost = max(triangles, key=lambda t: t['center'][0])
            rightmost_x = rightmost['center'][0]
            
            if previous_triangles:
                max_prev_x = max(t['center'][0] for t in previous_triangles)
                if rightmost_x > max_prev_x + 20:
                    new_triangle = rightmost
                else:
                    candidates = [t for t in triangles if t['center'][0] > max_prev_x + 10]
                    if candidates:
                        new_triangle = max(candidates, key=lambda t: t['center'][0])
                    else:
                        new_triangle = rightmost
            else:
                new_triangle = rightmost
        
        # Get y-coordinate
        center_y = new_triangle['center'][1]
        
        # Calculate price using THIS image's y-axis range
        price = None
        if image_min_price is not None and image_max_price is not None and image_y_top is not None and image_y_bottom is not None:
            price = y_to_price(center_y, image_min_price, image_max_price, image_y_top, image_y_bottom)
        
        signal = {
            'signal#': signal_number,
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'price': round(price, 2) if price is not None else None,
            'buy/sell': new_triangle['orientation'].capitalize(),
            'y_coordinate': center_y,
            'triangle': new_triangle
        }
        
        all_signals.append(signal)
        signal_number += 1
        
        previous_triangles = triangles.copy()
        
        price_str = f", price: {price:.2f}" if price is not None else ", price: N/A"
        print(f"  Signal {signal_number-1}: {signal['buy/sell']} at {signal['timestamp']}{price_str}\n")
    
    return all_signals


def process_date(folder_path: Path, date_str: str, output_dir: Optional[Path] = None) -> List[Dict]:
    """
    Process a specific date and extract all signals.
    
    Args:
        folder_path: Path to folder containing images (should be -clean folder)
        date_str: Date string in YYYY-MM-DD format
        output_dir: Optional output directory (defaults to Desktop/SPXsignal)
    
    Returns:
        List of signal dictionaries
    """
    if not folder_path.exists():
        print(f"Error: Folder {folder_path} does not exist")
        return []
    
    print("=" * 60)
    print(f"Extracting signals for date: {date_str}")
    print(f"Folder: {folder_path}")
    print("=" * 60)
    
    signals = extract_signals_sequential(folder_path, date_str)
    
    if not signals:
        print("No signals extracted.")
        return []
    
    if output_dir is None:
        desktop_path = Path.home() / "Desktop" / "SPXsignal"
    else:
        desktop_path = output_dir
    desktop_path.mkdir(parents=True, exist_ok=True)
    
    csv_path = desktop_path / f"{date_str}.csv"
    fieldnames = ['signal#', 'timestamp', 'price', 'buy/sell']
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for signal in signals:
            writer.writerow({
                'signal#': signal['signal#'],
                'timestamp': signal['timestamp'],
                'price': signal['price'] if signal['price'] is not None else '',
                'buy/sell': signal['buy/sell']
            })
    
    print(f"\nSaved CSV to: {csv_path}")
    
    print("\n" + "=" * 60)
    print("Extracted Signals Table")
    print("=" * 60)
    print(f"{'Signal#':<8} {'Timestamp':<20} {'Price':<12} {'Buy/Sell':<10}")
    print("-" * 60)
    for signal in signals:
        price_str = f"{signal['price']:.2f}" if signal['price'] is not None else "N/A"
        print(f"{signal['signal#']:<8} {signal['timestamp']:<20} {price_str:<12} {signal['buy/sell']:<10}")
    print("=" * 60)
    print(f"\nTotal signals extracted: {len(signals)}")
    
    return signals


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract buy/sell signals from SPX chart images")
    parser.add_argument(
        "--folder",
        type=str,
        default="spx-realtime-aws-clean",
        help="Folder containing images (default: spx-realtime-aws-clean)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default="2025-02-14",
        help="Date to process (YYYY-MM-DD format, default: 2025-02-14)"
    )
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder)
    date_str = args.date
    
    process_date(folder_path, date_str)


if __name__ == "__main__":
    main()
