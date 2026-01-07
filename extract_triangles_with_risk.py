"""Extract triangles with risk levels by comparing colors to a reference colorbar."""
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import cv2
from extract_signals import (
    detect_triangles,
    parse_timestamp_from_filename,
    extract_y_axis_range,
    y_to_price
)


def load_colorbar(colorbar_path: Optional[Path] = None) -> Optional[np.ndarray]:
    """
    Load colorbar image and extract left 1/3 width for color matching.
    
    Args:
        colorbar_path: Path to colorbar image. If None, uses Desktop/colorbar.png
    
    Returns:
        numpy array of shape (height, width//3, 3) in RGB format, or None if not found
        The colorbar is vertical: green at bottom (row index height-1), red at top (row index 0)
        In image arrays, row 0 is at the top, so top rows = red = high risk, bottom rows = green = low risk
    """
    if colorbar_path is None:
        colorbar_path = Path.home() / "Desktop" / "colorbar.png"
    
    if not colorbar_path.exists():
        print(f"Warning: Colorbar not found at {colorbar_path}")
        return None
    
    # Load image using OpenCV (BGR format)
    img = cv2.imread(str(colorbar_path))
    if img is None:
        print(f"Warning: Could not load colorbar from {colorbar_path}")
        return None
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Extract left 1/3 width
    height, width = img_rgb.shape[:2]
    left_third_width = width // 3
    colorbar_strip = img_rgb[:, :left_third_width]
    
    return colorbar_strip


def get_risk_level(triangle_color: Tuple[int, int, int], colorbar: np.ndarray) -> str:
    """
    Locate triangle color directly on colorbar and determine risk level based on position.
    
    The colorbar is vertical: green at bottom (lower 1/3), red at top (upper 1/3).
    We search for where the triangle color appears in the colorbar and use that position.
    
    Args:
        triangle_color: RGB tuple (R, G, B) of the triangle color
        colorbar: numpy array of shape (height, width, 3) in RGB format
    
    Returns:
        Risk level as string: "low", "medium", or "high"
        - Lower 1/3 of colorbar height = green zone = "low"
        - Upper 1/3 of colorbar height = red zone = "high"
        - Middle 1/3 = "medium"
    """
    if colorbar is None or colorbar.size == 0:
        return "unknown"
    
    r_tri, g_tri, b_tri = triangle_color
    height, width = colorbar.shape[:2]
    
    # Search for the triangle color directly in the colorbar
    # First try exact matches (within 3 RGB units for each channel)
    exact_tolerance = 3
    matching_rows = []
    
    # Check all pixels in the colorbar strip
    for row in range(height):
        for col in range(width):
            r_cb, g_cb, b_cb = colorbar[row, col]
            # Check if colors match within tolerance
            if (abs(int(r_tri) - int(r_cb)) <= exact_tolerance and 
                abs(int(g_tri) - int(g_cb)) <= exact_tolerance and 
                abs(int(b_tri) - int(b_cb)) <= exact_tolerance):
                matching_rows.append(row)
                break  # Found a match in this row, move to next row
    
    # If we found exact matches, use their positions
    if matching_rows:
        # Use the average row position of all matches
        avg_row = int(np.mean(matching_rows))
    else:
        # If no exact match, find the closest color match and use its position
        # This handles cases where the triangle color doesn't exist in colorbar
        min_distance = float('inf')
        best_row = height // 2  # Default to middle if no good match
        
        # Search through the colorbar to find closest match
        # Use middle column for more stable matching
        mid_col = width // 2
        for row in range(height):
            r_cb, g_cb, b_cb = colorbar[row, mid_col]
            # Calculate Euclidean distance in RGB space
            distance = np.sqrt((r_tri - r_cb)**2 + (g_tri - g_cb)**2 + (b_tri - b_cb)**2)
            
            if distance < min_distance:
                min_distance = distance
                best_row = row
        
        avg_row = best_row
    
    # Map row position to risk level based on thirds
    # In image arrays, row 0 is at the top (red/high), row height-1 is at bottom (green/low)
    third_height = height // 3
    
    if avg_row < third_height:
        return "high"  # Upper 1/3 = red zone = high risk
    elif avg_row < 2 * third_height:
        return "medium"  # Middle 1/3 = medium risk
    else:
        return "low"  # Lower 1/3 = green zone = low risk


def extract_triangles_with_risk(folder_path: Path, date_str: str, colorbar_path: Optional[Path] = None) -> List[Dict]:
    """
    Extract triangles with risk levels by comparing colors to a reference colorbar.
    
    Args:
        folder_path: Path to folder containing images (should be -clean folder)
        date_str: Date string in YYYY-MM-DD format
        colorbar_path: Optional path to colorbar image (defaults to Desktop/colorbar.png)
    
    Returns:
        List of dictionaries with keys: timestamp, price, color, risk_level
    """
    # Load colorbar
    colorbar = load_colorbar(colorbar_path)
    if colorbar is None:
        print("Error: Could not load colorbar. Risk levels will not be determined.")
        return []
    
    # Find images for the specified date
    pattern = f"{date_str}_*.png"
    image_files = sorted(folder_path.glob(pattern))
    
    if not image_files:
        print(f"No images found for date {date_str}")
        return []
    
    print(f"Found {len(image_files)} images for {date_str}")
    print("Processing images to extract triangles with risk levels...\n")
    
    results = []
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
        
        # Find the last/rightmost triangle (same logic as extract_signals_sequential)
        if i == 0:
            last_triangle = max(triangles, key=lambda t: t['center'][0])
        else:
            rightmost = max(triangles, key=lambda t: t['center'][0])
            rightmost_x = rightmost['center'][0]
            
            if previous_triangles:
                max_prev_x = max(t['center'][0] for t in previous_triangles)
                if rightmost_x > max_prev_x + 20:
                    last_triangle = rightmost
                else:
                    candidates = [t for t in triangles if t['center'][0] > max_prev_x + 10]
                    if candidates:
                        last_triangle = max(candidates, key=lambda t: t['center'][0])
                    else:
                        last_triangle = rightmost
            else:
                last_triangle = rightmost
        
        # Get y-coordinate
        center_y = last_triangle['center'][1]
        
        # Calculate price using THIS image's y-axis range
        price = None
        if image_min_price is not None and image_max_price is not None and image_y_top is not None and image_y_bottom is not None:
            price = y_to_price(center_y, image_min_price, image_max_price, image_y_top, image_y_bottom)
        
        # Get triangle color
        triangle_color = last_triangle['color']
        
        # Determine risk level by comparing to colorbar
        risk_level = get_risk_level(triangle_color, colorbar)
        
        result = {
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'price': round(price, 2) if price is not None else None,
            'color': triangle_color,
            'risk_level': risk_level
        }
        
        results.append(result)
        previous_triangles = triangles.copy()
        
        price_str = f", price: {price:.2f}" if price is not None else ", price: N/A"
        print(f"  Triangle: timestamp={result['timestamp']}{price_str}, color=RGB{triangle_color}, risk={risk_level}\n")
    
    return results


def main():
    """
    Main function for extracting triangles with risk levels.
    Accepts date as command-line argument or uses default.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract triangles with risk levels from SPX chart images")
    parser.add_argument(
        "--date",
        type=str,
        default="2025-02-14",
        help="Date to process (YYYY-MM-DD format, default: 2025-02-14)"
    )
    parser.add_argument(
        "--folder",
        type=str,
        default="spx-realtime-aws-clean",
        help="Folder containing images (default: spx-realtime-aws-clean)"
    )
    parser.add_argument(
        "--colorbar",
        type=str,
        default=None,
        help="Path to colorbar image (default: Desktop/colorbar.png)"
    )
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder)
    date_str = args.date
    colorbar_path = Path(args.colorbar) if args.colorbar else None
    
    if not folder_path.exists():
        print(f"Error: Folder {folder_path} does not exist")
        return
    
    print("=" * 80)
    print("Extracting Triangles with Risk Levels")
    print("=" * 80)
    print(f"Date: {date_str}")
    print(f"Folder: {folder_path}")
    if colorbar_path:
        print(f"Colorbar: {colorbar_path}")
    print("=" * 80)
    print()
    
    # Extract triangles with risk levels
    results = extract_triangles_with_risk(folder_path, date_str, colorbar_path)
    
    if not results:
        print("No triangles extracted.")
        return
    
    # Print formatted results table
    print("\n" + "=" * 80)
    print("Extracted Triangles with Risk Levels")
    print("=" * 80)
    print(f"{'Timestamp':<20} {'Price':<12} {'Color (RGB)':<20} {'Risk Level':<12}")
    print("-" * 80)
    
    for result in results:
        timestamp = result['timestamp']
        price_str = f"{result['price']:.2f}" if result['price'] is not None else "N/A"
        color_str = f"({result['color'][0]}, {result['color'][1]}, {result['color'][2]})"
        risk_level = result['risk_level']
        
        print(f"{timestamp:<20} {price_str:<12} {color_str:<20} {risk_level:<12}")
    
    print("=" * 80)
    print(f"\nTotal triangles extracted: {len(results)}")
    print("=" * 80)


if __name__ == "__main__":
    main()

