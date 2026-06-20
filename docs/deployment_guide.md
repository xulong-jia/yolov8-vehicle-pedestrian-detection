# Local Deployment Guide

## Purpose

This guide explains how to run the project locally through Python and how to
prepare Docker-based local deployment. It is a local deployment guide, not a
cloud production deployment guide.

The project keeps model weights, full datasets, generated outputs, source
videos, and large tracked previews outside Git.

## Prerequisites

- Python 3.11 recommended.
- `pip`.
- Local model weight file.
- Optional virtual environment.
- Docker installed only if using the Docker path.

## Install Dependencies

Runtime dependencies:

```bash
pip install -r requirements.txt
```

Development and tests:

```bash
pip install -r requirements-dev.txt
```

FastAPI:

```bash
pip install -r requirements-api.txt
```

Dependency files are split by purpose:

- `requirements.txt`: main demo and runtime dependencies.
- `requirements-dev.txt`: development and test dependencies.
- `requirements-api.txt`: FastAPI dependencies.

## Model Weights

Model weights are not included in GitHub.

Recommended local path:

```text
local_weights/yolov8s_640_50epochs/best.pt
```

The older YOLOv8n path may also exist for historical demos:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

Do not commit model weights.

## Local Python Path

### Run Setup Check

```bash
python3 src/check_setup.py
```

This checks core paths, sample images, and tracked risk files without training
or inference.

### Run Streamlit Image Demo

```bash
streamlit run app.py
```

or:

```bash
make streamlit
```

The Streamlit image demo supports uploaded images, sample images, confidence
threshold adjustment, a detection table, and CSV download. It does not save
prediction outputs by default.

### Run Streamlit Video Demo Page

```bash
.venv/bin/streamlit run app/streamlit_video_demo.py
```

This page browses existing local Video Analysis Center and tracked-video
artifacts. It also includes a FastAPI Video Job Launcher that can submit/query
jobs when the FastAPI service is running separately.

### Run FastAPI

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Optional API key authentication can be enabled for local or containerized
deployments:

```bash
API_KEY_AUTH_ENABLED=true API_KEY=your-secret \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

When enabled, protected endpoints require `X-API-Key: your-secret`; `/health`,
`/config`, `/model-status`, `/docs`, and `/openapi.json` remain public. Each
response includes `X-Request-ID`, either echoing the incoming header or a
generated UUID. Structured logs include request id, method, path, status code,
duration, and video job/artifact/bad-case identifiers where relevant.

### Run Minimal React Frontend

The optional React frontend is under `frontend/` and depends on FastAPI running
separately.

```bash
cd frontend
npm install
npm run dev
```

Default API base URL:

```text
http://localhost:8000
```

Override with:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

If FastAPI API key auth is enabled, enter the key in the frontend so requests
send `X-API-Key`. The frontend also sends and displays `X-Request-ID`.

This React frontend is minimal and optional. It does not include a video
player, multi-user permissions, production auth, DeepSORT, or a production
dashboard. Streamlit remains available as the local demo path.

Useful smoke commands:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/config
curl http://localhost:8000/model-status
curl -X POST "http://localhost:8000/predict?conf=0.25&imgsz=640&device=cpu" \
  -F "file=@sample.jpg"
```

Current FastAPI endpoints:

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

The video job API can create async video analysis jobs, persist job metadata in
SQLite, and query existing result artifacts. The SQLite index is stored at:

```text
local_outputs/api_video_jobs/video_jobs.sqlite3
```

The SQLite index stores metadata only. It does not store CSV, JSON, JSONL,
images, videos, or model weights. A real local FastAPI process restart smoke
for the SQLite index passed in `v1.3.2`.

### Run Batch Prediction CLI

```bash
python3 src/batch_predict.py --model local_weights/yolov8s_640_50epochs/best.pt --source docs/error_case_gallery/images --output-csv local_outputs/batch_predictions/detections.csv
```

Generated outputs should go under `local_outputs/`, which is ignored by Git.

## Docker Path

`v0.14.1` adds Docker deployment static acceptance. The following commands are
documented and statically checked. Actual Docker build/run smoke later passed
locally in `v0.14.4`, and mounted-weight container `/predict` passed in
`v0.14.5`. Docker runtime smoke for the v1.1-v1.4 API surface passed in
`v1.4.1`; see [Docker v1 API Smoke Result](docker_v1_api_smoke_result.md).

### Build

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

### Run FastAPI with Mounted Weights

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -e API_KEY_AUTH_ENABLED=false \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Run Streamlit with Mounted Weights

```bash
docker run --rm -p 8501:8501 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### Attach Existing Video Artifacts

The video job result API can attach to existing artifacts if those artifacts are
mounted into the container. Full async video execution also needs mounted model
weights, mounted source videos, and writable local outputs:

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  -v "$PWD/local_outputs:/app/local_outputs:rw" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Then create an attach-mode job:

```bash
curl -X POST http://localhost:8000/api/videos/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_id":"demo","run_name":"demo_run","run_dir":"/app/local_outputs/run1"}'
```

## Bad Case Documentation

The project has a Bad Case schema/report foundation and a metadata-only Bad
Case collection API:

- `docs/bad_cases_schema.md`
- `docs/bad_case_report.md`
- `docs/error_taxonomy.md`
- `docs/hard_examples.md`
- `docs/error_case_gallery/README.md`
- `POST /api/bad-cases`
- `GET /api/bad-cases`

The current Bad Case gallery CSV is a tiny hand-written documentation sample,
not a full real bad case dataset. Local collection records are written under
`local_outputs/bad_cases/` and remain ignored by Git.

## GT Evaluation Scaffold

Ground Truth templates for tracking, counting, ROI, and event evaluation are
documented in `docs/evaluation/gt_templates.md`. The scaffold CLI is:

```bash
python -m src.evaluation.video_eval_scaffold --help
```

`v1.7.0` adds a small reviewed GT sample evaluation under
`docs/evaluation/reviewed_gt_samples/` and
`docs/evaluation/reviewed_gt_eval_result/`. Large-scale/full benchmark
evaluation and complete MOT IDF1/MOTA remain future work.

## Run Checks

```bash
make check
make api-check
make danger-check
make list-large-docs
```

For Docker documentation changes:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache .venv/bin/python -m pytest tests/test_docker_deployment_docs.py -q
```

## What Not to Commit

Do not commit:

- weights
- full dataset splits
- `runs/`
- `local_outputs/`
- source videos
- tracked preview videos
- generated CSV, JSON, JSONL, or MP4 outputs
- ONNX exports
- Docker build cache

## Troubleshooting

### Model Not Found

Place the model under `local_weights/` and pass the path through `MODEL_PATH`,
the Streamlit model path field, or the relevant CLI `--model` argument.

### Streamlit Not Installed

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

### FastAPI Dependencies Missing

Install API dependencies:

```bash
pip install -r requirements-api.txt
```

### Pytest Missing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Docker Cannot See Weights

Check that the host directory is mounted read-only and that `MODEL_PATH` points
to the container-visible path, for example:

```text
MODEL_PATH=/app/local_weights/best.pt
```

### No Detections Found

Try lowering the confidence threshold, checking image quality, or testing
another image. A single no-detection result should not be interpreted as an
official model metric.

## Related Files

- `README.md`
- `Dockerfile`
- `.dockerignore`
- `docs/docker_deployment.md`
- `docs/api_usage.md`
- `docs/model_loading_strategy.md`
- `docs/model_weight_policy.md`
- `docs/streamlit_demo.md`
- `docs/streamlit_video_demo.md`
- `src/check_setup.py`
- `src/batch_predict.py`
- `Makefile`
