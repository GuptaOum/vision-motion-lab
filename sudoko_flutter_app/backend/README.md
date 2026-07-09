# Sudoku Solver API

A small [FastAPI](https://fastapi.tiangolo.com/) service that wraps the computer-vision
pipeline in [`../ocr/sudoku_ocr.py`](../ocr/sudoku_ocr.py). Upload a photo of a Sudoku puzzle and
get back the detected grid and the solved grid as JSON (optionally with a rendered image).

## Setup

Requires **Python 3.9+** and the [Tesseract OCR engine](https://github.com/tesseract-ocr/tesseract)
installed on the machine (the pip package `pytesseract` only wraps it).

```bash
cd sudoko_flutter_app/backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

- Interactive docs (Swagger UI): http://localhost:8000/docs
- Health check: `GET http://localhost:8000/`

> `--host 0.0.0.0` makes it reachable from a phone/emulator on your LAN. From the Android emulator,
> reach your host machine at `http://10.0.2.2:8000`.

## Endpoint

### `POST /solve`

Multipart form upload.

| Field / param | Type | Description |
| --- | --- | --- |
| `file` (form-data) | image | Photo of a Sudoku puzzle |
| `include_image` (query) | bool | If `true`, also returns a base64 PNG of the solved board |

**Success `200`**

```json
{
  "detected": [[5,3,0, ...], ...],
  "solved":   [[5,3,4, ...], ...],
  "solved_image_png_base64": "iVBORw0K..."   // only when include_image=true
}
```

`0` in `detected` marks a blank cell. Rows are top-to-bottom, columns left-to-right.

**Errors**

| Status | When |
| --- | --- |
| `400` | Empty upload or the image could not be decoded |
| `422` | No 4-corner grid found, OCR produced rule-breaking digits, or the puzzle is unsolvable |

## Try it with curl

```bash
curl -F "file=@puzzle.jpg" "http://localhost:8000/solve"
curl -F "file=@puzzle.jpg" "http://localhost:8000/solve?include_image=true"
```

## Call it from Flutter

Using the [`http`](https://pub.dev/packages/http) package:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<List<List<int>>> solveSudoku(String imagePath) async {
  // Use 10.0.2.2 for the Android emulator, or your machine's LAN IP on a real device.
  final uri = Uri.parse('http://10.0.2.2:8000/solve');

  final request = http.MultipartRequest('POST', uri)
    ..files.add(await http.MultipartFile.fromPath('file', imagePath));

  final streamed = await request.send();
  final response = await http.Response.fromStream(streamed);

  if (response.statusCode != 200) {
    throw Exception('Solve failed (${response.statusCode}): ${response.body}');
  }

  final data = jsonDecode(response.body) as Map<String, dynamic>;
  return (data['solved'] as List)
      .map((row) => (row as List).map((n) => n as int).toList())
      .toList();
}
```

To display the rendered board, request `?include_image=true` and decode the base64 field:

```dart
import 'dart:convert';
import 'package:flutter/material.dart';

// bytes -> Image widget
final bytes = base64Decode(data['solved_image_png_base64'] as String);
final widget = Image.memory(bytes);
```

## Docker

The image bundles the Tesseract engine and uses `opencv-python-headless`, so no host setup is
needed beyond Docker. The build context is the app folder `sudoko_flutter_app/` (it pulls in both
`backend/` and `ocr/`), which the compose file already handles.

```bash
cd sudoko_flutter_app/backend
docker compose up -d --build
# API on http://localhost:8000  (override with HOST_PORT)
```

## Deploy to EC2

Same flow as the FaceAttendance stack — `git archive → scp → docker compose up -d --build` — wrapped
in [`deploy.ps1`](deploy.ps1):

```powershell
cd sudoko_flutter_app/backend
.\deploy.ps1 -Server ec2-user@<EC2_IP> -KeyPath C:\Users\hp\.ssh\<key>.pem
```

The remote host needs **Docker + the compose plugin**. Open the chosen port (default **8000**) in the
instance's **security group**, then point the Flutter app's `baseUrl` at `http://<EC2_IP>:8000`.

> **Co-hosting note.** If you deploy onto a box that already serves port 80 (e.g. the FaceAttendance
> instance), keep `HOST_PORT=8000` so the two don't collide, or run nginx in front for path-based
> routing (`/sudoku` → this container). t3.micro (1 GB) is enough to run it, but add ~1 GB swap if a
> build ever gets OOM-killed.

## Notes

- Accuracy is bounded by the OCR step — feed a clear, straight-on image for best results
  (see the caveats in the root [README](../README.md#notes-and-caveats)).
- The CORS policy is wide open for development. Restrict `allow_origins` in `app.py` before
  exposing this anywhere public.
