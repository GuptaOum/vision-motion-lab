import os
import sys
import base64
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Reuse the Sudoku pipeline from ../ocr/sudoku_ocr.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ocr"))
import sudoku_ocr as sk


@asynccontextmanager
async def lifespan(app: FastAPI):
    sk.configure_tesseract()
    yield


app = FastAPI(
    title="Sudoku Solver API",
    version="1.0.0",
    description="Upload a photo of a Sudoku puzzle; get back the detected and solved grids.",
    lifespan=lifespan,
)

# Permissive CORS for local development (a Flutter web client or emulator can call it).
# Tighten allow_origins to your app's domain before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok", "service": "sudoku-solver"}


@app.post("/solve")
async def solve(
    file: UploadFile = File(..., description="image of a Sudoku puzzle"),
    include_image: bool = Query(False, description="also return a base64 PNG of the solved board"),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    try:
        warped = sk.find_grid(image)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    detected = sk.read_grid(warped)
    if not sk.is_consistent(detected):
        raise HTTPException(
            status_code=422,
            detail="The digits read from the image break Sudoku rules - the OCR likely "
                   "misread a cell. Try a clearer, straight-on image.",
        )

    solved = [row[:] for row in detected]
    if not sk.solve(solved):
        raise HTTPException(
            status_code=422,
            detail="No valid solution - the puzzle is unsolvable or a digit was misread.",
        )

    response = {"detected": detected, "solved": solved}

    if include_image:
        ok, buf = cv2.imencode(".png", sk.render_solution(warped, detected, solved))
        if ok:
            response["solved_image_png_base64"] = base64.b64encode(buf).decode("ascii")

    return JSONResponse(response)
