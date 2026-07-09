import json
import re

import boto3

# Qwen3 VL 235B: large vision model, credit-covered (no card), usable by the
# scoped IAM user. Amazon Nova / Gemma are lighter credit-covered fallbacks.
# Anthropic/Claude here needs a card, so it is not used.
DEFAULT_MODEL = "qwen.qwen3-vl-235b-a22b"

PROMPT = (
    "The image contains a 9x9 Sudoku puzzle. It may be PRINTED or HAND-DRAWN on "
    "paper (possibly lined/ruled paper, photographed at an angle, with uneven "
    "hand-drawn grid lines and handwritten digits).\n"
    "\n"
    "How to read it:\n"
    "- First locate the Sudoku grid and its 9x9 cell structure, ignoring notebook "
    "ruling lines, paper edges, shadows, and background. Hand-drawn cells vary in "
    "size - judge each digit's row/column by its position relative to the grid's "
    "own lines, not by absolute spacing.\n"
    "- Transcribe each cell exactly as written. Do NOT solve the puzzle and do NOT "
    "fill in any cell the writer left empty - empty cells are 0.\n"
    "- Handwriting cautions: 1 vs 7 (a 7 usually has a horizontal top bar), 4 vs 9, "
    "5 vs 6, 6 vs 0, 2 vs Z-like strokes, 8 vs 3. Stray dots, ink smudges, or "
    "crossed-out marks are NOT digits.\n"
    "- If a cell is truly unreadable, use 0 rather than guessing.\n"
    "\n"
    "Read row by row, top to bottom, left to right. Before answering, verify you "
    "have exactly 9 rows of exactly 9 integers.\n"
    'Return ONLY a JSON object of the form {"grid": [[...], ... 9 rows]} where '
    "each cell is the digit 1-9, or 0 for an empty cell. No text, no markdown fences."
)

_client = None


def _get_client(region):
    global _client
    if _client is None:
        _client = boto3.client("bedrock-runtime", region_name=region)
    return _client


def _image_format(image_bytes):
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    return "jpeg"


def _extract_grid(text):
    obj = None
    try:
        obj = json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                obj = json.loads(match.group(0))
            except Exception:
                obj = None
    grid = obj.get("grid") if isinstance(obj, dict) else obj

    out = [[0] * 9 for _ in range(9)]
    if isinstance(grid, list):
        for r in range(min(9, len(grid))):
            row = grid[r]
            if isinstance(row, list):
                for c in range(min(9, len(row))):
                    try:
                        v = int(row[c])
                    except (ValueError, TypeError):
                        v = 0
                    out[r][c] = v if 0 <= v <= 9 else 0
    return out


def read_grid_bedrock(image_bytes, model, region="ap-south-1"):
    """Read a Sudoku grid from a raw photo using a Bedrock vision model (Converse API).

    The model sees the whole image and returns the 9x9 grid, so no OpenCV grid
    detection is needed. Raises on client errors for caller fallback.
    """
    client = _get_client(region)
    resp = client.converse(
        modelId=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": PROMPT},
                    {"image": {"format": _image_format(image_bytes),
                               "source": {"bytes": image_bytes}}},
                ],
            }
        ],
        inferenceConfig={"temperature": 0, "maxTokens": 800},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    return _extract_grid(text)
