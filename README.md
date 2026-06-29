<div align="center">

# 🚗 YOLOv8 Vehicle and Pedestrian Detection System

### Vehicle and pedestrian detection, tracking, lightweight video analytics, local demo, API serving, and Docker delivery.

This is not only a single-image detection demo. It is an end-to-end computer
vision engineering project from dataset validation and model evaluation to
image/video inference, ByteTrack tracking, analytics, Bad Case review, FastAPI
serving, Streamlit demo, and Docker acceptance.

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-Demo-FF4B4B)
![Docker](https://img.shields.io/badge/Docker-Smoke%20Passed-2496ED)
![Status](https://img.shields.io/badge/Status-Final%20Delivery-success)

</div>

## ✨ Highlights

| Area | What This Project Provides |
| --- | --- |
| 🧾 Dataset quality | YOLO-format dataset config review, label validation, class distribution checks, and local-only split policy |
| 🎯 Detection training/evaluation | YOLOv8n, YOLOv8s, and YOLOv8m comparisons with Precision, Recall, mAP50, and mAP50-95 |
| 🖼️ Image/video inference | Single-image, batch-image, and video inference with annotated outputs and CSV contracts |
| 🧭 ByteTrack tracking | Frame detections converted into track identities and `tracks.csv` artifacts |
| 📊 Video analytics | Line counting, ROI counting, rule-based events, and `VideoAnalysisCenter` run organization |
| 🧪 Bad Case and GT evaluation | Metadata-only Bad Case review plus small reviewed GT evaluation scaffolds |
| 🔌 FastAPI and Docker delivery | Local API serving, SQLite video job index, artifact downloads, and Docker smoke acceptance |

## Project Snapshot

| Item | Status |
| --- | --- |
| Project type | Detection model engineering system |
| Main task | Vehicle and pedestrian detection + lightweight video analysis |
| Recommended model | YOLOv8s |
| Current final state | `v1.8.5-final-freeze-identity-cleanup` |
| Baseline release tag | `v1.0.0-final-release-summary` |
| Final delivery status | Ready for final freeze / delivery |
| Docker build/run smoke | Passed |
| Mounted-weight Docker `/predict` smoke | Passed |
| Streamlit container smoke | Passed |
| FastAPI container smoke | Passed |
| Boundary | Local/demo engineering project, not production traffic enforcement |

## 🧠 What Problem It Solves

Object detection answers what is in the frame. This project adds tracking and
lightweight analytics to answer how objects move, whether they cross a line,
whether they enter an ROI, and whether rule-based events are triggered.

The engineering chain is:

```text
detection -> tracking -> analytics -> review -> local/API/Docker delivery
```

## 🔁 Core Pipeline

```text
image / video
  -> YOLOv8 detector
  -> detection boxes
  -> ByteTrack tracking
  -> tracks.csv
  -> line counter / ROI counter / event rules
  -> VideoAnalysisCenter
  -> CSV / JSON / JSONL artifacts
  -> Streamlit / FastAPI / Docker local delivery
```

## ⚙️ Key Features

### 🧾 Dataset and Label Quality

- YOLOv8 dataset configuration through `dataset/data.yaml`.
- Target classes: `Bus`, `Car`, `Motorcycle`, `Person`, `Truck`, and
  `mini-truck`.
- Label format validation, class distribution analysis, and cleanup notes for
  invalid polygon-like labels.
- Dataset split folders are local-only and ignored by Git.

### 🎯 Detection Experiments

- YOLOv8n smoke, baseline, and official test evaluation.
- YOLOv8s retrain and official test evaluation.
- YOLOv8m scaling comparison.
- Accuracy and speed summaries retained as lightweight documentation artifacts.

### 🖼️ Image and Video Inference

- Single-image prediction through `src/predict_image.py`.
- Batch-image prediction through `src/batch_predict.py`.
- Video detection CSV generation through `src/predict_video.py`.
- Annotated outputs and generated result files stay in ignored local folders.

### 🧭 ByteTrack Tracking

- `src/track_video.py` converts frame-level detections into object tracks.
- `tracks.csv` stores `track_id`, class, confidence, bbox, center point, frame
  index, and timestamp.
- Tracked preview rendering is supported from existing track files.

### 📊 Video Analytics

- Line crossing counter for vehicle and pedestrian flow.
- Polygon ROI counter for area-level object statistics.
- Lightweight rule-based events such as crowd warning, density warning, long
  stay, and wrong direction.
- `VideoAnalysisCenter` organizes one video analysis run into stable artifacts:

```text
metadata.json
detections.csv
tracks.csv
count_events.csv
roi_frame_counts.csv
events.jsonl
video_analysis_summary.json
```

### 🧪 Bad Case and Evaluation

- Bad Case schema for detector, tracker, counter, ROI, and event errors.
- Small reviewed Bad Case sample collection.
- Small reviewed GT evaluation sample pack.
- Counting, ROI, event, and tracking engineering metric scaffolds.

Reviewed GT sample metrics:

| Evaluation Area | Sample Metric |
| --- | ---: |
| Counting MAE | 1.0 |
| ROI frame count MAE | 1.0 |
| Event precision | 0.5 |
| Event recall | 0.6666666666666666 |
| Tracking identity metric status | `gt_required_for_idf1=true` |

These samples are evaluation scaffolds and reviewed demonstrations, not a
production-scale benchmark.

### 🔌 FastAPI Serving

- Lazy model loading for `/predict`.
- Public health, config, and model-status endpoints.
- Optional API key authentication for protected endpoints.
- Request correlation through `X-Request-ID`.
- SQLite-backed video job metadata index.
- Registered artifact download endpoints limited to job artifacts.

### 🖥️ Streamlit and Non-Technical Launchers

- `app.py` provides the local Streamlit demo surface.
- Users with prepared `.venv` and `local_weights/best.pt` can start the app
  through `scripts/start_app_macos.command` or `scripts/start_app_windows.bat`.
- The optional React frontend is minimal and scoped to video jobs and Bad Case
  review.

### 🐳 Docker Delivery

- Docker image build and run smoke passed.
- FastAPI and Streamlit container smoke passed.
- Mounted-weight `/predict` smoke passed with `local_weights/best.pt` mounted
  read-only.
- Docker delivery keeps model weights, videos, datasets, SQLite files, and
  generated outputs outside Git.

## 🏗️ System Architecture

```text
UI Layer
  Streamlit local demo
  Optional React frontend for video jobs and Bad Case review
  Non-technical macOS / Windows launchers

API Layer
  FastAPI health, config, model-status, prediction, video job, and artifact APIs
  Optional API key auth
  X-Request-ID middleware

Service Layer
  Model loading
  Image inference
  Video job execution
  Result query
  Bad Case metadata handling

CV & Analytics Layer
  YOLOv8 detector
  ByteTrack tracker
  Geometry utilities
  Line counter
  ROI counter
  Event rules
  VideoAnalysisCenter

Storage / Artifact Layer
  CSV / JSON / JSONL outputs
  SQLite video job index
  Local-only generated outputs
  Local-only model weights and datasets
```

## 📈 Model Results

### Main Detection Results

| Experiment | Split | Image Size | Epochs | Precision | Recall | mAP50 | mAP50-95 | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| YOLOv8n smoke test | validation | 416 | 10 | 0.786 | 0.749 | 0.797 | 0.511 | Quick Colab smoke test |
| YOLOv8n baseline | validation | 640 | 50 | 0.81981 | 0.82768 | 0.86422 | 0.59102 | Main lightweight baseline |
| YOLOv8n official test | test | 640 | 50 | 0.841 | 0.816 | 0.859 | 0.582 | Official test split evaluation |
| YOLOv8s retrain | validation | 640 | 50 | 0.83909 | 0.84059 | 0.87705 | 0.60405 | Recommended model candidate |
| YOLOv8s official test | test | 640 | 50 | 0.865 | 0.838 | 0.876 | 0.601 | Recommended final model |
| YOLOv8m training | validation | 640 | 50 | 0.837 | 0.817 | 0.870 | 0.594 | Model-scaling comparison |
| YOLOv8m official test | test | 640 | 50 | 0.852 | 0.820 | 0.872 | 0.594 | Did not outperform YOLOv8s |

### YOLOv8s vs YOLOv8n Delta

YOLOv8s is the recommended final model because it achieved the best current
accuracy/latency trade-off.

| Metric | YOLOv8n | YOLOv8s | Delta |
| --- | ---: | ---: | ---: |
| Precision | 0.841 | 0.865 | +0.024 |
| Recall | 0.816 | 0.838 | +0.022 |
| mAP50 | 0.859 | 0.876 | +0.017 |
| mAP50-95 | 0.582 | 0.601 | +0.019 |

### Speed Benchmarks

| Runtime | Model | Hardware | Image Size | Speed | FPS |
| --- | --- | --- | ---: | ---: | ---: |
| PyTorch | YOLOv8n | Colab Tesla T4 | 640 | 11.562 ms/image | 86.49 |
| PyTorch | YOLOv8s | Colab Tesla T4 | 640 | 15.985 ms/image | 62.56 |
| ONNX Runtime | YOLOv8n | Colab Tesla T4 | 640 | 10.994 ms/image | 90.96 |
| ONNX Runtime | YOLOv8s | Colab Tesla T4 | 640 | 13.657 ms/image | 73.22 |

ONNX files are not committed to the repository.

## 🔌 API Overview

Full endpoint details are documented in [`docs/api_usage.md`](docs/api_usage.md).

- `GET /health`
- `GET /config`
- `GET /model-status`
- `POST /predict`
- `POST /api/videos/analyze`
- `GET /api/videos/jobs/{job_id}`
- `GET /api/videos/jobs/{job_id}/detections`
- `GET /api/videos/jobs/{job_id}/tracks`
- `GET /api/videos/jobs/{job_id}/analytics`
- `GET /api/videos/jobs/{job_id}/events`
- `GET /api/videos/jobs/{job_id}/artifacts/{artifact_name}/download`

## 🚀 Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-api.txt
```

Optional test/development tools:

```bash
pip install -r requirements-dev.txt
```

### Prepare Local Weights

Model weights are not included in GitHub. Place the recommended YOLOv8s weight
at:

```text
local_weights/best.pt
```

### Run Setup Check

```bash
python3 src/check_setup.py
```

### Run Streamlit Demo

```bash
streamlit run app.py
```

or:

```bash
make streamlit
```

### Run Batch Image Prediction

```bash
python3 src/batch_predict.py \
  --model local_weights/best.pt \
  --source docs/error_case_gallery/images \
  --output-csv local_outputs/batch_predictions/detections.csv \
  --imgsz 640 \
  --conf 0.25 \
  --device cpu
```

### Run FastAPI Locally

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Run with optional API key authentication:

```bash
API_KEY_AUTH_ENABLED=true API_KEY=your-secret \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Run Docker With Mounted Weights

Build image:

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

Run FastAPI with read-only mounted weights:

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Run Streamlit with read-only mounted weights:

```bash
docker run --rm -p 8501:8501 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Mounted `/predict` example:

```bash
curl -X POST "http://localhost:8000/predict?conf=0.25&imgsz=640&device=cpu" \
  -F "file=@sample.jpg"
```

## ✅ Validation Status

| Check | Status | Evidence |
| --- | --- | --- |
| Docker build/run smoke | Passed | `docs/docker_actual_smoke_result.md` |
| FastAPI container smoke | Passed | `docs/docker_actual_smoke_result.md` |
| Streamlit container smoke | Passed | `docs/docker_actual_smoke_result.md` |
| Mounted-weight `/predict` smoke | Passed | `docs/docker_actual_smoke_result.md` |
| Docker v1 API smoke refresh | Passed | `docs/docker_v1_api_smoke_result.md` |
| SQLite job restart smoke | Passed | `docs/sqlite_job_restart_smoke_result.md` |
| Bad Case sample collection | Completed | `docs/bad_case_report.md` |
| Reviewed GT sample pack | Completed | `docs/evaluation/reviewed_gt_eval_result.md` |

## 🏁 Milestones

| Version | Scope |
| --- | --- |
| `v0.13.0-fastapi-basic-service-acceptance` | FastAPI basic service endpoints accepted |
| `v0.14.5-mounted-weight-container-predict-smoke` | Mounted-weight container `/predict` smoke passed |
| `v1.0.0-final-release-summary` | Final release summary and delivery notes prepared |
| `v1.4.1-docker-v1-api-smoke-refresh` | Docker runtime smoke refreshed for v1.1-v1.4 API surface |
| `v1.8.0-react-video-job-frontend` | Minimal optional React frontend accepted |
| `v1.8.5-final-freeze-identity-cleanup` | Final identity docs, ignore policy, and delivery cleanup accepted |

## 🔒 Safety and Data Policy

Do not commit:

- `local_weights/`
- `*.pt`
- `*.pth`
- `*.onnx`
- `*.sqlite3`
- videos such as `*.mp4`, `*.avi`, `*.mov`, and `*.mkv`
- `dataset/train/`
- `dataset/valid/`
- `dataset/test/`
- `runs/`
- `local_outputs/`
- `local_videos/source/`
- `.venv/`
- new large videos or generated outputs

GitHub only stores code, configs, docs, tests, summaries, and selected
lightweight demo assets. Model weights, full datasets, SQLite databases, Docker
images, and generated outputs are local-only.

## ⚠️ Known Boundaries

- Not a production traffic enforcement system.
- Not an autonomous driving decision system.
- Not a formal COCO, MOT, or TrackEval benchmark.
- Reviewed GT samples are small demonstration/evaluation scaffolds, not a
  production-scale benchmark.
- React frontend is optional and minimal.
- Model weights and full datasets are local-only.
- Docker smoke results are local acceptance evidence, not environment-agnostic
  production certification.

## 🧾 Final Status

The project has completed the full engineering path from dataset validation and
YOLOv8 model evaluation to image/video inference, ByteTrack tracking, video
analytics, Bad Case review, FastAPI serving, Streamlit demo, Docker smoke
testing, and final delivery documentation.

Final status: **ready for final freeze and delivery**, subject to normal
environment-specific deployment checks.
