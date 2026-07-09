import base64
import json
import re

import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

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


def _mime(image_bytes):
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    return "image/jpeg"


def _extract_grid(content):
    """Pull a 9x9 int grid out of the model's reply, tolerant of stray text."""
    obj = None
    try:
        obj = json.loads(content)
    except Exception:
        match = re.search(r"\{.*\}", content, re.S)
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


def read_grid_groq(image_bytes, api_key, model=DEFAULT_MODEL, timeout=60.0):
    """Read a Sudoku grid from a raw photo using a Groq-hosted vision LLM.

    The model sees the whole image and returns the 9x9 grid, so no OpenCV grid
    detection is needed. Raises on transport/HTTP errors for caller fallback.
    """
    data_url = f"data:{_mime(image_bytes)};base64," + base64.b64encode(image_bytes).decode("ascii")
    body = {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    }
    resp = httpx.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            # Groq is behind Cloudflare, which 403s (error 1010) some default
            # library User-Agents; a browser-like UA avoids the block.
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SudokuBackend/1.0",
        },
        json=body,
        timeout=timeout,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return _extract_grid(content)
