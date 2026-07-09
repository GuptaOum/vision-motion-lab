import base64

import cv2
import httpx

VISION_URL = "https://vision.googleapis.com/v1/images:annotate"


def _centroid(vertices):
    xs = [v.get("x", 0) for v in vertices]
    ys = [v.get("y", 0) for v in vertices]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def read_grid_vision(warped, api_key, timeout=30.0):
    """Recognize digits on a de-warped Sudoku board with Google Cloud Vision.

    `warped` is the grayscale square board image from sudoku_ocr.find_grid.
    Returns a 9x9 list of ints (0 = blank). Each detected digit is placed in the
    cell its bounding-box centre falls into, so this handles handwriting well.
    Raises on transport/HTTP errors so the caller can fall back to Tesseract.
    """
    side = warped.shape[0]
    step = side / 9.0

    ok, buf = cv2.imencode(".png", warped)
    if not ok:
        raise ValueError("Could not encode the board image.")
    content = base64.b64encode(buf).decode("ascii")

    body = {
        "requests": [
            {
                "image": {"content": content},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                "imageContext": {"languageHints": ["en"]},
            }
        ]
    }

    resp = httpx.post(VISION_URL, params={"key": api_key}, json=body, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()

    responses = payload.get("responses", [{}])
    if responses and "error" in responses[0]:
        raise RuntimeError(responses[0]["error"].get("message", "Vision API error"))

    annotation = responses[0].get("fullTextAnnotation")
    grid = [[0] * 9 for _ in range(9)]
    if not annotation:
        return grid

    for page in annotation.get("pages", []):
        for block in page.get("blocks", []):
            for para in block.get("paragraphs", []):
                for word in para.get("words", []):
                    for sym in word.get("symbols", []):
                        text = sym.get("text", "")
                        if len(text) != 1 or text not in "123456789":
                            continue
                        verts = sym.get("boundingBox", {}).get("vertices", [])
                        if not verts:
                            continue
                        cx, cy = _centroid(verts)
                        row, col = int(cy // step), int(cx // step)
                        if 0 <= row < 9 and 0 <= col < 9:
                            grid[row][col] = int(text)
    return grid
