import json
import re

import boto3

# Gemma 3 27B and Amazon Nova are billed as normal AWS usage (covered by credits,
# no card) - unlike Anthropic/Marketplace models which require a payment instrument.
DEFAULT_MODEL = "google.gemma-3-27b-it"

PROMPT = (
    "The image contains a 9x9 Sudoku puzzle. Read the digits exactly as written, "
    "row by row, top to bottom, left to right. Return ONLY a JSON object of the "
    'form {"grid": [[...], ... 9 rows]} where each row has 9 integers and each '
    "cell is the digit 1-9, or 0 for an empty cell. No text, no markdown fences."
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
