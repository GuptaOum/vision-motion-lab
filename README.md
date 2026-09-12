# Sudoku Vision & Solver Platform

An end-to-end full-stack application that uses advanced Computer Vision and LLM-powered Optical Character Recognition (OCR) to read, digitize, and solve Sudoku puzzles directly from your phone's camera.

## Architecture

This project is built around a robust, multi-layered architecture:

1.  **Flutter Mobile App (Frontend)**
    *   Cross-platform mobile application for capturing photos of unsolved Sudoku grids.
    *   Features a fully editable interactive grid to correct any OCR mistakes before solving.
    *   Includes user authentication (Login/Signup) with JWT-based session management.
    *   Maintains a cloud-synced history of all solved puzzles.

2.  **FastAPI Backend**
    *   High-performance Python backend serving the OCR pipeline and solving logic.
    *   Secure SQLite storage with PBKDF2 password hashing and HMAC signed tokens.
    *   Dockerized for easy deployment (currently hosted on an AWS EC2 instance).

3.  **Multi-Provider Vision/OCR Pipeline**
    *   The core engine uses a resilient, fallback-based OCR pipeline to extract digits from noisy photos:
        *   **Primary:** AWS Bedrock using large Vision-Language Models (e.g., Qwen3 VL 235B) reading the raw photo directly.
        *   **Secondary:** Groq (Llama 4 Vision) as a high-speed fallback.
        *   **Tertiary:** Traditional OCR (OCR.space, Google Vision, Tesseract) combined with custom OpenCV pre-processing (contour detection, grid de-warping, CLAHE contrast enhancement).
    *   *If the AI models struggle to read the raw image, the system falls back to the deterministic OpenCV grid-extraction pipeline before trying again.*

4.  **Algorithmic Solver**
    *   A lightning-fast backtracking algorithm that processes the digitized 9x9 grid, returns the complete solution, and flags any conflicting cells inputted by the user.

## Repository Structure

```text
sudoko_flutter_app/
â”œâ”€â”€ backend/          # FastAPI server, database logic, Docker configuration
â”œâ”€â”€ lib/              # Flutter UI, state management, API integration
â””â”€â”€ ocr/              # OpenCV pre-processing and standalone OCR scripts
```

## Quick Start (Backend)

The backend requires several API keys to power the fallback OCR chain.

```bash
cd sudoko_flutter_app/backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
BEDROCK_MODEL_ID=your_model_id
GROQ_API_KEY=your_key
OCRSPACE_API_KEY=your_key
```

Run the server:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Quick Start (Flutter App)

```bash
cd sudoko_flutter_app
flutter pub get
flutter run
```
*Note: For release builds on Android, ensure cleartext traffic is permitted in your network security config if you are communicating with an HTTP (non-HTTPS) backend.*
