# YOLOv8 Vehicle and Pedestrian Detection System

A YOLOv8-based computer vision engineering project for vehicle and pedestrian detection, video tracking, lightweight traffic analytics, local visualization, API serving, and Docker-based deployment.

This repository is not only a single-image detection demo. It documents and implements an end-to-end workflow from dataset preparation and model evaluation to image/video inference, ByteTrack tracking, line/ROI analytics, Bad Case review, FastAPI serving, and deployment acceptance.

---

## 1. Project Summary

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
| Model weight policy | `local_weights/best.pt` is local-only and ignored by Git |

---

## 2. What This Project Does

The system takes images or videos as input and produces structured detection, tracking, counting, ROI, and event outputs.

```text
image / video
  -> YOLOv8 detector
  -> detection boxes
  -> ByteTrack tracking
  -> tracks.csv
  -> line counter / ROI counter / event rules
  -> CSV / JSON / JSONL outputs
  -> Streamlit / FastAPI / optional React frontend for video jobs and Bad Case review
```

Core capabilities:

- Detect six target classes: `Bus`, `Car`, `Motorcycle`, `Person`, `Truck`, and `mini-truck`.
- Run single-image, batch-image, and video inference.
- Generate detection CSV files and annotated visual outputs.
- Track video targets with ByteTrack and export `tracks.csv`.
- Count vehicle and pedestrian flow through configured crossing lines.
- Count objects inside polygon ROI regions.
- Generate lightweight rule-based events such as crowd warning, density warning, long stay, and wrong direction.
- Review detector, tracker, counter, ROI, and event Bad Cases.
- Serve image and video jobs through FastAPI.
- Run local demos through Streamlit.
- Package the runtime with Docker while keeping model weights and large datasets outside Git.

---

## 3. Development Roadmap

This project was completed in eight engineering stages. Each stage produced stable artifacts, documentation, and acceptance checks.

| Stage | Goal | Main Outputs |
| --- | --- | --- |
| 1. Project foundation | Build a safe and maintainable repo structure | `src/`, `configs/`, `tests/`, `Makefile`, `.gitignore`, `.dockerignore`, CI syntax check |
| 2. Dataset and label quality | Prepare YOLOv8 dataset configuration and validation workflow | `dataset/data.yaml`, dataset analysis, label checks, dataset documentation |
| 3. Training and evaluation | Train and compare YOLOv8 models on fixed splits | YOLOv8n / YOLOv8s / YOLOv8m reports, Precision, Recall, mAP50, mAP50-95 |
| 4. Image and video inference | Build reusable inference scripts and CSV outputs | `predict_image.py`, `predict_video.py`, `batch_predict.py`, detection CSVs |
| 5. Multi-object tracking | Convert frame-level detections into object trajectories | ByteTrack runtime, `track_video.py`, `tracks.csv`, tracked video rendering |
| 6. Video analytics | Add counting, ROI statistics, and result organization | line counter, ROI counter, `VideoAnalysisCenter`, analytics CSV/JSON outputs |
| 7. Bad Case and evaluation loop | Record errors and create lightweight GT evaluation samples | Bad Case schema/report, reviewed sample collection, GT evaluation scaffold |
| 8. Serving and deployment | Package the project for local UI, API, and Docker use | Streamlit, FastAPI, SQLite job index, artifact download endpoints, Docker smoke results |

---

## 4. System Architecture

```text
User Interface Layer
  ├── Streamlit local demo
  └── Optional React frontend for video jobs and Bad Case review

API Layer
  ├── Health / config / model-status endpoints
  ├── Image prediction endpoint
  ├── Async video job endpoints
  ├── Result query endpoints
  └── Bad Case endpoints

Service Layer
  ├── Model loading
  ├── Image inference
  ├── Video job execution
  ├── Result query
  └── Bad Case handling

Computer Vision Layer
  ├── YOLOv8 detector
  ├── ByteTrack tracker
  ├── Geometry utilities
  ├── Line counter
  ├── ROI counter
  └── Event rules

Storage / Artifact Layer
  ├── CSV / JSON / JSONL outputs
  ├── SQLite video job index
  ├── Local-only generated outputs
  └── Local-only model weights and datasets
```

Design principles:

- YOLOv8 handles object detection only.
- Tracking converts independent frame detections into continuous object identities.
- Analytics converts trajectories into counts, ROI statistics, and rule-based events.
- Streamlit is used for local interaction and visualization.
- FastAPI exposes model and result functionality as structured JSON endpoints.
- Docker packages the environment but does not include model weights, full datasets, or generated large outputs.

---

## 5. Dataset

The dataset follows the YOLOv8 detection format.

```text
dataset/
  data.yaml
  train/images/   # local-only, ignored
  train/labels/   # local-only, ignored
  valid/images/   # local-only, ignored
  valid/labels/   # local-only, ignored
  test/images/    # local-only, ignored
  test/labels/    # local-only, ignored
```

Target classes:

| Class ID | Class Name |
| ---: | --- |
| 0 | Bus |
| 1 | Car |
| 2 | Motorcycle |
| 3 | Person |
| 4 | Truck |
| 5 | mini-truck |

Data quality work completed:

- Dataset configuration review.
- Label format validation.
- Class distribution analysis.
- Invalid polygon-like label cleanup or conversion.
- Documentation of local-only dataset split policy.

---

## 6. Model Experiments and Results

### 6.1 Main Detection Results

| Experiment | Split | Image Size | Epochs | Precision | Recall | mAP50 | mAP50-95 | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| YOLOv8n smoke test | validation | 416 | 10 | 0.786 | 0.749 | 0.797 | 0.511 | Quick Colab smoke test |
| YOLOv8n baseline | validation | 640 | 50 | 0.81981 | 0.82768 | 0.86422 | 0.59102 | Main lightweight baseline |
| YOLOv8n official test | test | 640 | 50 | 0.841 | 0.816 | 0.859 | 0.582 | Official test split evaluation |
| YOLOv8s retrain | validation | 640 | 50 | 0.83909 | 0.84059 | 0.87705 | 0.60405 | Recommended model candidate |
| YOLOv8s official test | test | 640 | 50 | 0.865 | 0.838 | 0.876 | 0.601 | Recommended final model |
| YOLOv8m training | validation | 640 | 50 | 0.837 | 0.817 | 0.870 | 0.594 | Model-scaling comparison |
| YOLOv8m official test | test | 640 | 50 | 0.852 | 0.820 | 0.872 | 0.594 | Did not outperform YOLOv8s |

### 6.2 Final Model Choice

YOLOv8s is the recommended default model because it achieved the best current accuracy/latency trade-off.

Compared with YOLOv8n on the same official test split, YOLOv8s improved:

| Metric | YOLOv8n | YOLOv8s | Delta |
| --- | ---: | ---: | ---: |
| Precision | 0.841 | 0.865 | +0.024 |
| Recall | 0.816 | 0.838 | +0.022 |
| mAP50 | 0.859 | 0.876 | +0.017 |
| mAP50-95 | 0.582 | 0.601 | +0.019 |

### 6.3 Speed Benchmarks

| Runtime | Model | Hardware | Image Size | Speed | FPS |
| --- | --- | --- | ---: | ---: | ---: |
| PyTorch | YOLOv8n | Colab Tesla T4 | 640 | 11.562 ms/image | 86.49 |
| PyTorch | YOLOv8s | Colab Tesla T4 | 640 | 15.985 ms/image | 62.56 |
| ONNX Runtime | YOLOv8n | Colab Tesla T4 | 640 | 10.994 ms/image | 90.96 |
| ONNX Runtime | YOLOv8s | Colab Tesla T4 | 640 | 13.657 ms/image | 73.22 |

No ONNX files are committed to the repository.

---

## 7. Main Features

### 7.1 Image Detection

- Upload or select an image.
- Run YOLOv8 inference.
- Display annotated detections.
- Show class, confidence, and bounding box coordinates.
- Export detection results as CSV.
- Handle missing model weights, invalid images, model loading failures, and inference errors with clear messages.

### 7.2 Video Detection and Tracking

- Read local video metadata and frames.
- Export frame-level detection results.
- Run ByteTrack through the standard `track_video.py` runtime.
- Export `tracks.csv` with `track_id`, class, confidence, bbox, center point, frame index, and timestamp.
- Render tracked preview videos from existing track files.

### 7.3 Video Analytics

- Line crossing counter for vehicle and pedestrian flow.
- Polygon ROI counter for area-level object statistics.
- Rule-based event outputs.
- `VideoAnalysisCenter` for organizing one video analysis run into stable artifacts.

Typical artifacts:

```text
metadata.json
detections.csv
tracks.csv
count_events.csv
roi_frame_counts.csv
events.jsonl
video_analysis_summary.json
```

### 7.4 Bad Case and Evaluation

- Bad Case schema for detector, tracker, counter, ROI, and event errors.
- Reviewed Bad Case sample collection.
- Lightweight GT evaluation sample pack.
- Counting, ROI, event, and tracking engineering metric scaffolds.

The reviewed GT sample reports:

| Evaluation Area | Sample Metric |
| --- | ---: |
| Counting MAE | 1.0 |
| ROI frame count MAE | 1.0 |
| Event precision | 0.5 |
| Event recall | 0.6666666666666666 |
| Tracking identity metric status | `gt_required_for_idf1=true` |

These samples are evaluation scaffolds and reviewed demonstrations, not a production-scale benchmark.

### 7.5 Serving and Deployment

FastAPI includes:

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

Engineering features:

- Lazy model loading.
- Optional API key authentication.
- Request correlation through `X-Request-ID`.
- SQLite-backed video job metadata index.
- Safe artifact download endpoints limited to registered job artifacts.
- Local CORS support for Streamlit and the optional React frontend.

---

## 8. Project Structure

```text
yolov8-vehicle-pedestrian-detection/
  app.py
  configs/
    analytics.yaml
    default.yaml
    tracking.yaml
  dataset/
    data.yaml
    train/                  # local-only, ignored
    valid/                  # local-only, ignored
    test/                   # local-only, ignored
  docs/
    api_usage.md
    bad_case_report.md
    delivery_notes.md
    docker_deployment.md
    final_acceptance_checklist.md
    final_project_report.md
    release_summary.md
    video_analytics_mvp.md
  frontend/                 # optional React frontend for video jobs and Bad Case review
  local_outputs/            # generated local outputs, ignored
  local_weights/            # local model weights, ignored
  src/
    analytics/
    core/
    services/
    tracking/
    analyze_dataset.py
    api.py
    batch_predict.py
    check_setup.py
    evaluate.py
    predict_image.py
    predict_video.py
    train.py
    track_video.py
    video_reader.py
    visualize_dataset.py
  tests/
  .dockerignore
  .gitignore
  Dockerfile
  Makefile
  README.md
  requirements.txt
  requirements-api.txt
  requirements-dev.txt
```

---

## 9. Quick Start

### 9.1 Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-api.txt
```

For tests and development tools:

```bash
pip install -r requirements-dev.txt
```

### 9.2 Prepare Model Weights

Model weights are not included in GitHub.

Place the recommended YOLOv8s weight at:

```text
local_weights/best.pt
```

Historical experiment weights may also be stored in local-only versioned folders, for example:

```text
local_weights/yolov8s_640_50epochs/best.pt
```

Do not commit model weights.

### 9.3 Run Setup Check

```bash
python3 src/check_setup.py
```

### 9.4 Run Streamlit Demo

```bash
streamlit run app.py
```

or:

```bash
make streamlit
```

### 9.5 Run Batch Image Prediction

```bash
python3 src/batch_predict.py \
  --model local_weights/best.pt \
  --source docs/error_case_gallery/images \
  --output-csv local_outputs/batch_predictions/detections.csv \
  --imgsz 640 \
  --conf 0.25 \
  --device cpu
```

### 9.6 Run FastAPI Locally

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Run with optional API key authentication:

```bash
API_KEY_AUTH_ENABLED=true API_KEY=your-secret \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### 9.7 Run Docker

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

---

## 10. Non-Technical User Launchers

If `.venv` and `local_weights/best.pt` have already been prepared by the maintainer, ordinary users can start the local application without typing Python, Uvicorn, Streamlit, React, or Docker commands.

- macOS: double-click `scripts/start_app_macos.command`
- Windows: double-click `scripts/start_app_windows.bat`
- Guide: `docs/non_technical_user_guide.md`

On macOS, if the script is not executable, run:

```bash
chmod +x scripts/start_app_macos.command
```

The launcher starts:

- FastAPI: `http://localhost:8000`
- Streamlit: `http://localhost:8501`
- Optional React frontend for video jobs and Bad Case review: `http://localhost:5173` when frontend dependencies already exist

---

## 11. Makefile Commands

| Command | Purpose |
| --- | --- |
| `make check` | Run Python syntax checks for the main app and scripts |
| `make test` | Run pytest tests under `tests/` |
| `make api-check` | Run syntax check for `src/api.py` |
| `make streamlit` | Start the local Streamlit demo |
| `make status` | Show short Git status |
| `make danger-check` | Check staged files for risky paths |
| `make list-large-docs` | List large files under `docs/` |

---

## 12. Final Review Entry Points

For final review, read these documents in order:

1. `docs/release_summary.md`
2. `docs/delivery_notes.md`
3. `docs/final_acceptance_checklist.md`
4. `docs/final_project_report.md`
5. `docs/docker_actual_smoke_result.md`
6. `docs/api_usage.md`
7. `docs/bad_case_report.md`
8. `docs/video_analytics_mvp.md`

---

## 13. Known Limitations and Future Work

Non-blocking future work:

- Expand the reviewed Bad Case dataset.
- Expand the reviewed GT evaluation dataset.
- Add optional DeepSORT production runtime.
- Harden ByteTrack for production-scale full-length validation.
- Add OAuth/JWT, multi-user authorization, API key rotation, and external monitoring.
- Add Prometheus/Grafana or other production observability.
- Harden the optional React frontend into a production dashboard and video player.
- Run larger GT-based tracking, counting, ROI, and event quantitative evaluations.
- Add optional full YOLOv8m PyTorch and ONNX Runtime speed benchmarks.
- Add ONNX Runtime mAP/NMS evaluation if a separate protocol is defined.

---

## 14. Safety and Git Policy

Do not commit:

- `local_weights/`
- `*.pt`
- `*.pth`
- `*.onnx`
- `*.sqlite3`
- `*.zip`
- `*.mp4`
- `*.avi`
- `*.mov`
- `*.mkv`
- `dataset/train/`
- `dataset/valid/`
- `dataset/test/`
- `runs/`
- `local_outputs/`
- `local_videos/source/`
- `.venv/`
- new large videos or generated outputs

Repository policy:

- GitHub stores code, configs, tests, documentation, summaries, and selected lightweight demo assets.
- Model weights are local-only.
- Full dataset splits are local-only.
- Generated outputs are local-only.
- Docker images and layers are local-only.
- Large videos and bulk inference outputs should be managed through local paths, external storage, or deployment volumes.

---

## 15. Final Status

The project has completed the full engineering path from dataset validation and YOLOv8 model evaluation to image/video inference, ByteTrack tracking, video analytics, Bad Case review, FastAPI serving, Streamlit demo, Docker smoke testing, and final delivery documentation.

Final status: **ready for final freeze and delivery**, subject to normal environment-specific deployment checks.
