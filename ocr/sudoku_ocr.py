import os
import sys
import argparse
from shutil import which

import cv2
import numpy as np
import pytesseract


def configure_tesseract():
    """Point pytesseract at a Tesseract binary: PATH first, then common install paths."""
    if which("tesseract"):
        return
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/opt/homebrew/bin/tesseract",
    ]
    for path in candidates:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return


def order_corners(pts):
    """Order four points as top-left, top-right, bottom-right, bottom-left."""
    pts = pts.reshape(4, 2).astype("float32")
    ordered = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    ordered[0] = pts[np.argmin(s)]   # top-left has the smallest x + y
    ordered[2] = pts[np.argmax(s)]   # bottom-right has the largest x + y
    ordered[1] = pts[np.argmin(d)]   # top-right has the smallest y - x
    ordered[3] = pts[np.argmax(d)]   # bottom-left has the largest y - x
    return ordered


def find_grid(image, side=450):
    """Locate the board and return a top-down, de-warped grayscale square."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No contours found - does the image contain a Sudoku grid?")

    board = None
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True):
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            board = approx
            break
    if board is None:
        raise ValueError("Could not find a four-cornered Sudoku grid.")

    src = order_corners(board)
    dst = np.array([[0, 0], [side, 0], [side, side], [0, side]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(gray, matrix, (side, side))


def extract_cell_digit(cell):
    """OCR a single cell, returning its digit or 0 when the cell is blank."""
    h, w = cell.shape
    margin = int(0.12 * h)                      # crop away the printed grid lines
    cell = cell[margin:h - margin, margin:w - margin]
    if cell.size == 0:
        return 0

    cell = cv2.adaptiveThreshold(
        cell, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    if cv2.countNonZero(cell) < 0.02 * cell.size:  # almost no ink -> empty cell
        return 0

    contours, _ = cv2.findContours(cell, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0
    x, y, cw, ch = cv2.boundingRect(max(contours, key=cv2.contourArea))
    if cw * ch < 0.02 * cell.size:                 # largest blob is just a speck
        return 0
    digit = cell[y:y + ch, x:x + cw]

    size = max(cw, ch) + 10                          # center the digit on a square
    canvas = np.zeros((size, size), dtype="uint8")
    ox, oy = (size - cw) // 2, (size - ch) // 2
    canvas[oy:oy + ch, ox:ox + cw] = digit
    canvas = cv2.bitwise_not(canvas)                 # black digit on white for Tesseract
    canvas = cv2.resize(canvas, (48, 48), interpolation=cv2.INTER_AREA)
    canvas = cv2.copyMakeBorder(canvas, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)

    text = pytesseract.image_to_string(
        canvas, config="--psm 10 --oem 3 -c tessedit_char_whitelist=123456789"
    ).strip()
    return int(text) if text.isdigit() else 0


def read_grid(warped):
    """Split the de-warped board into 81 cells and OCR each into a 9x9 list of ints."""
    side = warped.shape[0]
    step = side // 9
    grid = []
    for r in range(9):
        row = []
        for c in range(9):
            cell = warped[r * step:(r + 1) * step, c * step:(c + 1) * step]
            row.append(extract_cell_digit(cell))
        grid.append(row)
    return grid


def find_empty(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None


def is_valid(grid, num, pos):
    r, c = pos
    if any(grid[r][j] == num for j in range(9) if j != c):
        return False
    if any(grid[i][c] == num for i in range(9) if i != r):
        return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if grid[i][j] == num and (i, j) != pos:
                return False
    return True


def solve(grid):
    """Backtracking solver that fills the grid in place. Returns True if solved."""
    empty = find_empty(grid)
    if not empty:
        return True
    r, c = empty
    for num in range(1, 10):
        if is_valid(grid, num, (r, c)):
            grid[r][c] = num
            if solve(grid):
                return True
            grid[r][c] = 0
    return False


def is_consistent(grid):
    """True if the parsed puzzle has no immediate row/column/box conflicts."""
    for r in range(9):
        for c in range(9):
            n = grid[r][c]
            if n != 0 and not is_valid(grid, n, (r, c)):
                return False
    return True


def format_grid(grid):
    """Render a 9x9 grid as text with 3x3 box separators ('.' for blanks)."""
    lines = []
    for r in range(9):
        if r % 3 == 0 and r != 0:
            lines.append("------+-------+------")
        cells = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                cells.append("|")
            cells.append(str(grid[r][c]) if grid[r][c] else ".")
        lines.append(" ".join(cells))
    return "\n".join(lines)


def render_solution(warped, original, solved):
    """Draw the solved digits (only in originally-blank cells) onto the board."""
    canvas = cv2.cvtColor(warped, cv2.COLOR_GRAY2BGR)
    side = warped.shape[0]
    step = side // 9
    for r in range(9):
        for c in range(9):
            if original[r][c] == 0 and solved[r][c] != 0:
                x = c * step + step // 2 - 12
                y = r * step + step // 2 + 12
                cv2.putText(canvas, str(solved[r][c]), (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 170, 0), 2, cv2.LINE_AA)
    return canvas


def main():
    parser = argparse.ArgumentParser(
        description="Read a Sudoku puzzle from an image and solve it."
    )
    parser.add_argument("image", help="path to an image of a Sudoku puzzle")
    parser.add_argument("--side", type=int, default=450,
                        help="de-warped board size in pixels (default: 450)")
    parser.add_argument("--save", metavar="PATH",
                        help="write an image of the solved board to PATH")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        sys.exit(f"Image not found: {args.image}")

    configure_tesseract()

    image = cv2.imread(args.image)
    if image is None:
        sys.exit(f"Could not read image: {args.image}")

    warped = find_grid(image, side=args.side)
    grid = read_grid(warped)

    print("Detected puzzle:\n")
    print(format_grid(grid))
    print()

    if not is_consistent(grid):
        sys.exit("The digits read from the image break Sudoku rules - the OCR likely "
                 "misread a cell. Try a clearer, straight-on image.")

    solved = [row[:] for row in grid]
    if not solve(solved):
        sys.exit("No valid solution - the puzzle is unsolvable or a digit was misread.")

    print("Solved:\n")
    print(format_grid(solved))

    if args.save:
        cv2.imwrite(args.save, render_solution(warped, grid, solved))
        print(f"\nSaved solved board to {args.save}")


if __name__ == "__main__":
    main()
