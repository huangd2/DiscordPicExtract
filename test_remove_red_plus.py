import cv2
import numpy as np
from pathlib import Path
import sys

def remove_red_plus(plot):
    """
    Remove small red '+' markers that overlap triangles
    """
    hsv = cv2.cvtColor(plot, cv2.COLOR_BGR2HSV)

    # red color mask (two HSV ranges)
    red1 = cv2.inRange(hsv, (0,120,120), (10,255,255))
    red2 = cv2.inRange(hsv, (170,120,120), (180,255,255))
    red_mask = red1 | red2

    # clean thin lines
    red_mask = cv2.morphologyEx(
        red_mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8)
    )

    contours, _ = cv2.findContours(
        red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    cleaned = plot.copy()
    red_detections = plot.copy()

    for c in contours:
        area = cv2.contourArea(c)
        if 20 < area < 120:  # "+" is small
            cv2.drawContours(cleaned, [c], -1, (255,255,255), -1)
            cv2.drawContours(red_detections, [c], -1, (0, 0, 255), 2)  # Draw in red

    return cleaned, red_mask, red_detections


def test_remove_red_plus_detailed(image_path):
    """
    Detailed test showing original, red mask, detected markers, and cleaned result
    """
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return
    
    # Crop to plot region
    plot = img[60:560, 120:900]
    
    # Apply cleaning
    plot_clean, red_mask, red_detections = remove_red_plus(plot)
    
    # Convert red_mask to 3-channel for display
    red_mask_3ch = cv2.cvtColor(red_mask, cv2.COLOR_GRAY2BGR)
    
    # Create 2x2 grid: Original | Red Mask | Detected Markers | Cleaned
    top_row = np.hstack([plot, red_mask_3ch])
    bottom_row = np.hstack([red_detections, plot_clean])
    comparison = np.vstack([top_row, bottom_row])
    
    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    h, w = plot.shape[:2]
    cv2.putText(comparison, "Original", (10, 30), font, 0.7, (0, 255, 0), 2)
    cv2.putText(comparison, "Red Mask", (w + 10, 30), font, 0.7, (0, 255, 0), 2)
    cv2.putText(comparison, "Detected Red Markers", (10, h + 30), font, 0.7, (0, 255, 0), 2)
    cv2.putText(comparison, "Cleaned", (w + 10, h + 30), font, 0.7, (0, 255, 0), 2)
    
    # Try to show the comparison (may fail if OpenCV doesn't have GUI support)
    try:
        cv2.imshow("Red Plus Removal Test", comparison)
        print("Press any key to close the window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except cv2.error as e:
        print(f"Note: Could not display window (GUI not available): {e}")
        print("Image will be saved instead.")
    
    # Save the comparison
    output_path = Path(image_path).parent / f"{Path(image_path).stem}_red_plus_test.png"
    cv2.imwrite(str(output_path), comparison)
    print(f"Saved comparison to: {output_path}")
    print(f"Open the image file to view the results.")


if __name__ == "__main__":
    # Check if image path provided as command line argument
    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
        if not image_path.exists():
            print(f"Error: Image not found: {image_path}")
        else:
            print(f"Testing with: {image_path.name}")
            test_remove_red_plus_detailed(image_path)
    else:
        # Default: Test with first image in folder
        image_dir = Path("spx-realtime-aws-clean")
        image_files = list(image_dir.glob("*.png"))
        
        if image_files:
            test_image = image_files[0]
            print(f"Testing with: {test_image.name}")
            test_remove_red_plus_detailed(test_image)
        else:
            print(f"No images found in {image_dir}")
            print("Usage: python test_remove_red_plus.py <image_path>")