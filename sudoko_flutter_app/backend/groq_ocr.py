import base64
import json
import re

import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

PROMPT = (
    "The image contains a 9x9 Sudoku puzzle. Read the digits exactly as written, "
    "row by row, top to bottom, left to right. Return ONLY a JSON object of the "
    'form {"grid": [[...],[...], ... 9 rows]} where each row has 9 integers and '
    "each cell is the digit 1-9, or 0 for an empty cell. Do not add any text, "
    "explanation, or markdown fences."
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
