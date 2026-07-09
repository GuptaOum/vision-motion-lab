import os
import sys
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# Reuse the Sudoku pipeline from ../ocr/sudoku_ocr.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ocr"))
import sudoku_ocr as sk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vision_ocr
import ocrspace_ocr
import groq_ocr
import bedrock_ocr

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "").strip()
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.environ.get("GROQ_MODEL", "").strip() or groq_ocr.DEFAULT_MODEL
VISION_API_KEY = os.environ.get("GOOGLE_VISION_API_KEY", "").strip()
OCRSPACE_API_KEY = os.environ.get("OCRSPACE_API_KEY", "").strip()


class GridIn(BaseModel):
    grid: list[list[int]]

    @field_validator("grid")
    @classmethod
    def _validate(cls, v):
        if len(v) != 9 or any(len(row) != 9 for row in v):
            raise ValueError("grid must be 9x9")
        if any(not (0 <= n <= 9) for row in v for n in row):
            raise ValueError("each cell must be 0-9 (0 = blank)")
        return v


def find_conflicts(grid):
    """Return [row, col] pairs whose value duplicates another in its row/column/box."""
    bad = []
    for r in range(9):
        for c in range(9):
            n = grid[r][c]
            if n == 0:
                continue
            grid[r][c] = 0
            if not sk.is_valid(grid, n, (r, c)):
                bad.append([r, c])
            grid[r][c] = n
    return bad


@asynccontextmanager
async def lifespan(app: FastAPI):
    sk.configure_tesseract()
    yield


app = FastAPI(
    title="Sudoku Solver API",
    version="2.0.0",
    description="Read a Sudoku puzzle from a photo (/read), let the user correct it, then solve (/solve).",
    lifespan=lifespan,
)

# Permissive CORS for development. Tighten allow_origins before exposing publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok", "service": "sudoku-solver"}


@app.post("/read")
async def read(file: UploadFile = File(..., description="image of a Sudoku puzzle")):
    """OCR only: return the detected 9x9 grid (0 = blank) for the user to review/correct."""
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    # LLM path: hand the whole photo to a vision model, which finds the grid
    # itself (no OpenCV detection needed - best for messy/handwritten grids).
    if BEDROCK_MODEL_ID:
        try:
            detected = bedrock_ocr.read_grid_bedrock(data, BEDROCK_MODEL_ID, AWS_REGION)
            return {"detected": detected, "engine": "bedrock"}
        except Exception:
            pass
    if GROQ_API_KEY:
        try:
            detected = groq_ocr.read_grid_groq(data, GROQ_API_KEY, GROQ_MODEL)
            return {"detected": detected, "engine": "groq"}
        except Exception:
            pass  # fall through to the OpenCV + OCR pipeline

    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    try:
        # larger board = more pixels per digit, which helps the OCR engines
        warped = sk.find_grid(image, side=900)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    engine = "tesseract"
    detected = None
    if OCRSPACE_API_KEY:
        try:
            detected = ocrspace_ocr.read_grid_ocrspace(warped, OCRSPACE_API_KEY)
            engine = "ocrspace"
        except Exception:
            detected = None
    if detected is None and VISION_API_KEY:
        try:
            detected = vision_ocr.read_grid_vision(warped, VISION_API_KEY)
            engine = "vision"
        except Exception:
            detected = None
    if detected is None:
        detected = sk.read_grid(warped)
        engine = "tesseract"

    return {"detected": detected, "engine": engine}


@app.post("/solve")
async def solve(payload: GridIn):
    """Solve a (user-confirmed) 9x9 grid. Reports conflicting cells instead of guessing."""
    grid = payload.grid

    conflicts = find_conflicts(grid)
    if conflicts:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "This grid breaks Sudoku rules - a number is duplicated in a row, "
                           "column, or box. Fix the highlighted cells.",
                "conflicts": conflicts,
            },
        )

    solved = [row[:] for row in grid]
    if not sk.solve(solved):
        raise HTTPException(status_code=422, detail={"message": "No solution exists for this grid."})

    return {"solved": solved}
