---
name: vision-motion-lab-unified
description: "vision-motion-lab — OpenCV+MediaPipe playground; Sudoku OCR+solver deployed as FastAPI on EC2 with a Flutter front end, multi-provider vision-LLM OCR fallback chain"
metadata:
  node_type: memory
  type: project
---

Curated GitHub repo built 2026-07-09 from the old tinkering project `G:\PycharmProjects\pythonProject` (originals left untouched). Repo: **G:\PycharmProjects\vision-motion-lab**, pushed to **https://github.com/GuptaOum/vision-motion-lab** (public, GuptaOum). Organized OpenCV+MediaPipe scripts into `body_pose_tracking / hand_tracking / head_tracking / opencv_basics / ocr / automation / gui_experiments / misc + assets`. Code copied verbatim (user preference: no AI-added comments); only asset paths patched to resolve via `__file__`.

---

## Sudoku feature (end-to-end, the flagship piece)

Reorganized 2026-07-09 into ONE self-contained folder `sudoko_flutter_app/` containing `ocr/`, `backend/`, and the Flutter app (`lib/`). Backup zip moved OUT of the repo to `G:\PycharmProjects\pythonProject-backup-2026-07-09.zip` (never commit it).

- `sudoko_flutter_app/ocr/sudoku_ocr.py` — robust pipeline: corner-ordering, cell-border crop, blank detection, Tesseract auto-config, plus a backtracking solver + CLI.
- `sudoko_flutter_app/backend/` — FastAPI **v3 API**: `POST /read` (image→detected grid; OpenCV pre-clean via `find_grid(1000px)+CLAHE+border`, retries raw if <10 digits detected), `POST /solve` (grid→solution + conflict cells, auto-saves to history when a Bearer token is present), `POST /auth/signup|login` (HMAC-signed token, 180d), `GET /history`, `DELETE /history/{id}`. `store.py` = stdlib SQLite + pbkdf2 passwords + HMAC tokens. DB in Docker volume `sudoku-data` → `/app/data`.

### OCR reader priority chain: AWS Bedrock (primary) → Groq → OCR.space → Vision → Tesseract
All fall back automatically.

- **Bedrock** (`bedrock_ocr.py`, boto3 `converse`, region `ap-south-1`) reads the WHOLE raw photo — primary path. **Current model: `qwen.qwen3-vl-235b-a22b`** (Qwen3 VL 235B) — largest credit-covered vision model available; found to beat Gemma on real handwriting. Also tested: gemma-3-27b-it, apac.amazon.nova-pro/lite.
- **Groq** (`groq_ocr.py`, `meta-llama/llama-4-scout-17b-16e-instruct`) also reads the raw photo — **must send a browser User-Agent** (Groq is behind Cloudflare; default library UAs get error 1010).
- OCR.space/Vision/Tesseract use `find_grid(side=900)` + de-warp instead of reading the raw photo.
- All engines land ~33-37 digits correctly on a noisy test photo; the editable-grid UI step covers the rest.

### AWS Bedrock billing gotcha (important — costs real debugging time if rediscovered)
Account has AWS credits but **no card** → Anthropic/Claude models on Bedrock are a Marketplace product → gives exactly ONE free grace invoke per model, then `INVALID_PAYMENT_INSTRUMENT` (needs a card even with credits available). Tested extensively: Claude 3-haiku/3.5-sonnet/3.7-sonnet all "work" on root once then block; no IAM user can invoke Claude at all (even `AmazonBedrockFullAccess` = AccessDenied) — **Claude on this account is account-level/root-gated AND card-gated, full stop.**
- **Amazon Nova + Google Gemma are first-party/credit-covered and work reliably with no card**, on a scoped IAM user.
- To ever use Claude here: add a card to AWS (no forced deposit needed, just a card on file).
- Google GCP/Gemini direct API is blocked by an India ₹1000 minimum billing requirement — avoid that path.

### Credentials
Dedicated IAM user **`sudoku-bedrock`** (access key `AKIA3BG7JN5FTZXDNKOG`) with inline policy `bedrock-invoke` (`bedrock:InvokeModel*` + `aws-marketplace:ViewSubscriptions/Subscribe`). Keys live in a gitignored `.env` on the server (`~/sudoku-api/sudoko_flutter_app/backend/.env`): `AWS_ACCESS_KEY_ID/SECRET`, `BEDROCK_MODEL_ID`, `GROQ_API_KEY`, `OCRSPACE_API_KEY`. **Not root** — root keys were briefly used, then dropped for security in favor of the scoped IAM user above.

### Flutter app (`sudoko_flutter_app/lib/`) — v3 (3.0.0+3)
Login/signup → solver screen ("Hi, username" appbar + history/logout) → pick/capture → `/read` → **editable grid + number pad** → `/solve` (auto-saved) → render; history screen (list, tap = bottom-sheet grid view, delete, pull-refresh); 401 auto-logout; dark mode via `ThemeMode.system`. `baseUrl` baked to `http://3.109.177.77:8000`. APK published on GitHub Release v1.0.0.

**Critical release-build gotcha:** Flutter only puts the INTERNET permission in debug/profile manifests by default — a **release** APK needs `<uses-permission android:name="android.permission.INTERNET"/>` added to `AndroidManifest.xml` manually, or the release build silently has no network access ("could not reach server"). Also needs a `network_security_config.xml` cleartext-permit entry for the server IP (HTTP, not HTTPS). These `android/` edits are gitignored and lost on `flutter create .` regen — must be re-applied after any platform-folder regeneration.

## Deployment
Co-hosted on the **FaceAttendance EC2** (`i-00c50e742d73480ac`, t3.medium, ap-south-1, Elastic IP **3.109.177.77**, user `ubuntu`, key `C:\Users\hp\.ssh\face-attendance.pem` — see `E:\proj\FaceAttendance\PROJECT_MEMORY.md` for that project's own details). Container `sudoku-api` via docker compose in `~/sudoku-api/backend`, published on port **8000** (FaceAttendance itself stays on port 80). SG ingress rule added for 8000/tcp 0.0.0.0/0. `restart: unless-stopped`.

**Outstanding:** no HTTPS — fine for Android debug builds, but blocks a Play Store release which requires cleartext-disabled by default. If the EC2 instance is stopped, the Sudoku API goes down (it was previously found stopped and had to be manually started).
