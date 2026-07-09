import base64

import cv2
import httpx

OCRSPACE_URL = "https://api.ocr.space/parse/image"


def _request(b64_png, api_key, engine, timeout):
    data = {
        "apikey": api_key,
        "base64Image": "data:image/png;base64," + b64_png,
        "OCREngine": engine,
        "isOverlayRequired": "true",
        "language": "eng",
        "scale": "true",
    }
    resp = httpx.post(OCRSPACE_URL, data=data, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("IsErroredOnProcessing"):
        msg = payload.get("ErrorMessage")
        if isinstance(msg, list):
            msg = "; ".join(msg)
        raise RuntimeError(msg or "OCR.space error")
    return payload


def _grid_from(payload, step):
    """Bin each detected digit into its cell by its bounding-box centre.
    Returns (grid, found_any)."""
    grid = [[0] * 9 for _ in range(9)]
    found = False
    results = payload.get("ParsedResults") or []
    if not results:
        return grid, found
    overlay = results[0].get("TextOverlay") or {}
    for line in overlay.get("Lines", []):
        for word in line.get("Words", []):
            digits = [c for c in (word.get("WordText") or "") if c in "123456789"]
            if not digits:
                continue
            left = word.get("Left", 0)
            top = word.get("Top", 0)
            width = word.get("Width", 0)
            height = word.get("Height", 0)
            n = len(digits)
            for i, ch in enumerate(digits):
                cx = left + width * (i + 0.5) / n
                cy = top + height / 2.0
                row, col = int(cy // step), int(cx // step)
                if 0 <= row < 9 and 0 <= col < 9:
                    grid[row][col] = int(ch)
                    found = True
    return grid, found


def read_grid_ocrspace(warped, api_key, timeout=30.0):
    """Recognize digits on a de-warped Sudoku board via the OCR.space API.

    Tries engine 2 (best for handwriting) first; if it yields no positioned
    digits, retries engine 1 (which reliably returns bounding boxes). Raises on
    transport/HTTP/API errors so the caller can fall back to Tesseract.
    """
    side = warped.shape[0]
    step = side / 9.0

    ok, buf = cv2.imencode(".png", warped)
    if not ok:
        raise ValueError("Could not encode the board image.")
    b64 = base64.b64encode(buf).decode("ascii")

    grid = [[0] * 9 for _ in range(9)]
    for engine in ("2", "1"):
        payload = _request(b64, api_key, engine, timeout)
        grid, found = _grid_from(payload, step)
        if found:
            return grid
    return grid
