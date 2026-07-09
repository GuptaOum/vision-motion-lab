# Vision Motion Lab

A personal playground of **computer-vision experiments** built with
[OpenCV](https://opencv.org/) and [MediaPipe](https://developers.google.com/mediapipe).
It started as a fitness-tracking side project — counting arm curls and leg squats from a
webcam — and grew into a collection of hand-gesture, head-tracking, OCR, and desktop-automation
tinkering scripts.

Everything here is exploratory: many of the pose scripts are iterations of the same idea, from a
bare-bones headless counter up to a threaded Tkinter GUI that logs your reps to Excel.

## Highlights

- **Rep counting from pose** — real-time bicep-curl and squat counters using MediaPipe Pose
  joint angles, with on-screen progress bars, stage detection (`up`/`down`) and FPS overlay.
- **Tkinter workout app** — pick an exercise, count reps live, reset counters, and (in the full
  version) persist history to a spreadsheet.
- **Hand finger counter** — counts raised fingers per hand with left/right hand labelling.
- **Head-turn counter** — counts left/right head turns using MediaPipe Holistic.
- **Sudoku solver** — reads a puzzle from a photo (perspective-corrected grid + digit OCR) and
  solves it with backtracking, optionally rendering the answer back onto the board.
- **Odds and ends** — Canny edge detection, a Piano Tiles auto-clicker,
  turtle/Tkinter GUI experiments, and small learning snippets.

## Repository structure

```
vision-motion-lab/
├── body_pose_tracking/     MediaPipe Pose — exercise rep counters (headless → GUI)
│   ├── exercise_tracker_full.py     Flagship Tkinter app: reps + Excel history (pandas)
│   ├── exercise_tracker.py          Tkinter app with in-window video (PIL)
│   ├── exercise_tracker_threaded.py Threaded Tkinter app, arm + leg modes
│   ├── exercise_selector_oop.py     Class-based (ExerciseApp) Tkinter selector
│   ├── exercise_selector.py         Function-based Tkinter selector
│   ├── pose_tracker_gui.py          Minimal arm/leg tracker GUI
│   ├── arm_curl_counter.py          Headless dual-arm curl counter + progress bars
│   ├── leg_squat_counter.py         Headless dual-leg squat counter + progress bars
│   ├── bicep_curl_cli.py            CLI menu: left / right / both-arm curls
│   ├── pose_smoothing_demo.py       Landmark smoothing (exponential moving average)
│   ├── gpu_pose_tracker.py          Pose tracker with a CUDA/Torch availability check
│   ├── pose_counter.py              Reusable PoseCounter class
│   ├── main.py                      Entry point that drives PoseCounter
│   └── basics/                      Minimal MediaPipe Pose starters + angle-math demo
├── hand_tracking/          MediaPipe Hands
│   ├── hand_tracking.py             Draw hand landmarks + FPS
│   ├── finger_counter.py            Count raised fingers
│   └── finger_counter_labeled.py    Count fingers with left/right hand labels + bounding box
├── head_tracking/
│   └── head_turn_counter.py         Count left/right head turns (MediaPipe Holistic)
├── opencv_basics/          Plain OpenCV webcam experiments
│   ├── webcam_view.py               Basic capture loop
│   ├── webcam_zoom.py               Upscaled webcam feed
│   ├── webcam_resize.py             Resize demo
│   ├── webcam_snapshot.py           Grab a single frame to disk
│   └── edge_detection.py            Live Canny edge detection
├── automation/             Desktop automation bots
│   ├── piano_tiles_bot.py           Pixel-watching auto-clicker for Piano Tiles
│   ├── spiral_drawing.py            Draw a spiral by moving the mouse
│   ├── whatsapp_sender.py           Send a WhatsApp message (pywhatkit)
│   └── youtube_search.py            Play / search YouTube (pywhatkit)
├── gui_experiments/        Tkinter / turtle UI scratch work
│   ├── camera_tkinter.py            Webcam inside a Tkinter window
│   ├── image_viewer.py              Show / rotate an image (uses assets/goku.png)
│   ├── image_grid_viewer.py         Responsive image grid layout
│   ├── turtle_keyboard_draw.py      Keyboard-controlled turtle drawing
│   └── ttk_template.py              ttkbootstrap / customtkinter starter
├── misc/                   Small standalone learning snippets
├── sudoko_flutter_app/     Self-contained full-stack Sudoku solver
│   ├── ocr/sudoku_ocr.py           CV pipeline + backtracking solver (CLI)
│   ├── backend/                    FastAPI POST /solve service (Dockerized)
│   └── lib/                        Flutter app: pick photo -> solve -> render
└── assets/                 Sample media (Bicep Curl.mp4, goku.png)
```

### Sudoku solver, end to end

Everything for the Sudoku feature lives together in [`sudoko_flutter_app/`](sudoko_flutter_app):

- [`ocr/sudoku_ocr.py`](sudoko_flutter_app/ocr/sudoku_ocr.py) — the CV pipeline + backtracking solver (CLI).
- [`backend/`](sudoko_flutter_app/backend) — a FastAPI service wrapping it in a `POST /solve` endpoint that
  takes a puzzle photo and returns the detected and solved grids as JSON.
  See [backend/README.md](sudoko_flutter_app/backend/README.md).
- Flutter app (`lib/`) — a minimal screen: pick/capture a photo, call `/solve`, and render the
  solved board. See [sudoko_flutter_app/README.md](sudoko_flutter_app/README.md).

## Setup

Requires **Python 3.9+**. MediaPipe pins specific OpenCV/NumPy versions, so a virtual
environment is recommended.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Some scripts need extra, platform-specific tools (see [Notes](#notes-and-caveats)):

- `sudoko_flutter_app/ocr/sudoku_ocr.py` needs the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) engine installed on your system.
- `automation/piano_tiles_bot.py` uses `pywin32` and is **Windows-only**.
- `body_pose_tracking/gpu_pose_tracker.py` will use CUDA if a compatible PyTorch + GPU is available, otherwise it falls back to CPU.

## Running

Each script is self-contained. From the repo root, for example:

```bash
python body_pose_tracking/arm_curl_counter.py
python hand_tracking/finger_counter_labeled.py
python opencv_basics/edge_detection.py

# Sudoku: read a puzzle photo, solve it, and save the filled board
python sudoko_flutter_app/ocr/sudoku_ocr.py path/to/puzzle.jpg --save solved.png
```

Most webcam windows share these keyboard controls:

| Key | Action |
| --- | --- |
| `q` or `x` | Quit the window |
| `r` | Reset the rep counter |
| `z` | Exit (some hand/pose scripts) |

## Notes and caveats

- **Bundled assets resolve automatically.** `exercise_tracker.py` (`Bicep Curl.mp4`) and
  `image_viewer.py` (`goku.png`) locate their media in [`assets/`](assets) relative to the script,
  so they run from any working directory. A couple of throwaway scripts still reference files that
  were never part of this project (`image_grid_viewer.py` → a personal photo, `play_sound.py` → a
  sample WAV); drop your own file in and adjust the name to use them.
- **Tinkering, not production.** These are learning iterations — expect duplicated logic across the
  `body_pose_tracking` scripts, broad `try/except` blocks, and hard-coded screen coordinates in the
  automation bots (`piano_tiles_bot.py` was tuned to one specific screen).
- A webcam is required for all the OpenCV/MediaPipe scripts.

## License

Released under the [MIT License](LICENSE).
