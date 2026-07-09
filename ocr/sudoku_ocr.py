import cv2
import numpy as np
import pytesseract

# Ensure you have Tesseract installed and configured correctly
# If necessary, specify the path to the Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    """
    Preprocesses the image for OCR.
    """
    # Load the image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(img, (5, 5), 0)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    return thresh

def extract_sudoku_grid(image):
    """
    Extracts the Sudoku grid from the image.
    """
    # Find contours
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest rectangular contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Approximate to a polygon
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)

    # Ensure it has four sides
    if len(approx) == 4:
        pts = np.array([point[0] for point in approx], dtype="float32")

        # Define the desired square size
        side_length = 450  # e.g., 450x450 pixels for a 9x9 grid
        target_pts = np.array(
            [[0, 0], [side_length, 0], [side_length, side_length], [0, side_length]],
            dtype="float32",
        )

        # Perform perspective transform
        matrix = cv2.getPerspectiveTransform(pts, target_pts)
        warped = cv2.warpPerspective(image, matrix, (side_length, side_length))
        return warped
    else:
        raise ValueError("Unable to detect a rectangular Sudoku grid.")

def extract_digits(grid_image):
    """
    Splits the grid into 81 cells and performs OCR on each cell.
    """
    side_length = grid_image.shape[0]  # Assuming square grid
    cell_size = side_length // 9
    sudoku_array = []

    for row in range(9):
        row_data = []
        for col in range(9):
            # Extract the cell
            x, y = col * cell_size, row * cell_size
            cell = grid_image[y:y+cell_size, x:x+cell_size]

            # Remove noise from the cell
            cell = cv2.bitwise_not(cell)
            cell = cv2.resize(cell, (28, 28), interpolation=cv2.INTER_AREA)

            # Perform OCR to detect the digit
            digit = pytesseract.image_to_string(
                cell, config="--psm 10 -c tessedit_char_whitelist=0123456789"
            ).strip()

            # Append the digit or empty space
            row_data.append(int(digit) if digit.isdigit() else None)
        sudoku_array.append(row_data)
    
    return sudoku_array

# Path to the Sudoku image
image_path = ""  # Replace with your image path

# Process the Sudoku image
try:
    preprocessed = preprocess_image(image_path)
    grid = extract_sudoku_grid(preprocessed)
    sudoku_array = extract_digits(grid)

    # Print the 2D Sudoku array
    for row in sudoku_array:
        print(row)
except Exception as e:
    print(f"Error: {e}")
