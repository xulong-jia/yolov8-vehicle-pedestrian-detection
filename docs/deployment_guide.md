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

This page is read-only. It browses existing local Video Analysis Center and
tracked-video artifacts. It does not run YOLO, ByteTrack, analytics, or
rendering.

### Run FastAPI

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

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

The video job API is a safe result-query skeleton. real async video execution remains future work.

### Run Batch Prediction CLI

```bash
python3 src/batch_predict.py --model local_weights/yolov8s_640_50epochs/best.pt --source docs/error_case_gallery/images --output-csv local_outputs/batch_predictions/detections.csv
```

Generated outputs should go under `local_outputs/`, which is ignored by Git.

## Docker Path

`v0.14.1` adds Docker deployment static acceptance. The following commands are
documented and statically checked. Actual Docker build/run smoke later passed
locally in `v0.14.4`, and mounted-weight container `/predict` passed in
`v0.14.5`.

### Build

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

### Run FastAPI with Mounted Weights

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
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

The video job result API can attach to existing artifacts only if those
artifacts are mounted into the container:

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  -v "$PWD/local_outputs:/app/local_outputs:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Then create a skeleton job:

```bash
curl -X POST http://localhost:8000/api/videos/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_id":"demo","run_name":"demo_run","run_dir":"/app/local_outputs/run1"}'
```

## Bad Case Documentation

The project has a Bad Case schema and report foundation:

- `docs/bad_cases_schema.md`
- `docs/bad_case_report.md`
- `docs/error_taxonomy.md`
- `docs/hard_examples.md`
- `docs/error_case_gallery/README.md`

The current Bad Case gallery CSV is a tiny hand-written documentation sample,
not a full real bad case dataset.

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
