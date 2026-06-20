# Docker Actual Smoke Plan

## Purpose

This document is the preflight plan for actual Docker build/run smoke testing.
It prepares the final execution manual's deployment acceptance work without
running Docker in `v0.14.3`.

`v0.14.3` does not execute `docker build` or `docker run`. Its purpose is to
record the current blocker, confirm static Dockerfile and `.dockerignore`
safety, and define the exact manual smoke checklist for a later actual Docker
build/run tag.

## Current preflight result

| Check | Result |
| --- | --- |
| docker CLI availability | no |
| `docker --version` result summary | command not found |
| `docker info` exit code | `docker_info_exit=127` |
| Current blocker | Docker CLI/daemon unavailable |
| Go/no-go | No-Go for actual build/run until Docker CLI and daemon are available. |

## Manual prerequisite checklist

- Docker installed.
- Docker daemon running.
- Repository clean.
- Enough disk space for image build and temporary layers.
- Local weights exist under `local_weights/`.
- `MODEL_PATH` points to the mounted weight path inside the container.
- Sample image for predict smoke is local-only and not committed.
- No generated outputs staged.

## Dockerfile static review

| Item | Current observation | Acceptance | Note |
| --- | --- | --- | --- |
| Base image | `python:3.11-slim` | Accept | Reasonable small Python base for this project. |
| Workdir | `/app` | Accept | Matches documented container paths. |
| Requirements install | `pip install --no-cache-dir -r requirements.txt` | Accept | `requirements.txt` contains Streamlit, FastAPI, Uvicorn, Ultralytics, and OpenCV. |
| Copied files | `app.py`, `src`, `configs`, selected docs | Accept | Keeps image focused on code/config/docs needed by local demos. |
| Default CMD | Streamlit `app.py` on port `8501` | Accept | Matches Streamlit demo default. |
| FastAPI command override | `uvicorn src.api:app --host 0.0.0.0 --port 8000` | Accept | Documented `docker run` command overrides default CMD. |
| EXPOSE note | `8501` default, `8000` via `docker run -p 8000:8000` | Accept | FastAPI port mapping is explicit in run command. |
| Weights copied | no weights copied | Accept | Weights must be mounted read-only. |
| Local video/output copied | no local video/output copied | Accept | `local_videos`, `local_outputs`, and large videos are excluded. |

## .dockerignore asset safety review

| Item | Covered | Note |
| --- | --- | --- |
| `.venv` | yes | Local virtual environment excluded. |
| `__pycache__` | yes | Python cache excluded. |
| `runs` | yes | Generated run outputs excluded. |
| `local_outputs` | yes | Generated local outputs excluded. |
| `local_weights` | yes | Model weights excluded. |
| `local_videos/source` | yes | Source videos excluded. |
| `dataset/train` | yes | Full train split excluded. |
| `dataset/valid` | yes | Full validation split excluded. |
| `dataset/test` | yes | Full test split excluded. |
| `*.pt` | yes | PyTorch weights excluded. |
| `*.pth` | yes | PyTorch checkpoints excluded. |
| `*.onnx` | yes | ONNX exports excluded. |
| `*.mp4` | yes | Generated/source MP4 files excluded. |
| `*.avi` | yes | Generated/source AVI files excluded. |
| `*.mov` | yes | Generated/source MOV files excluded. |
| `*.mkv` | yes | Generated/source MKV files excluded. |
| `*.zip` | yes | Archives excluded. |

## Exact build command

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

## FastAPI container smoke command

```bash
docker run --rm --name yolov8-api-smoke -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Health checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/config
curl http://localhost:8000/model-status
```

## Streamlit container smoke command

```bash
docker run --rm --name yolov8-streamlit-smoke -p 8501:8501 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Mounted-weight /predict smoke command

```bash
curl -X POST "http://localhost:8000/predict?conf=0.25&imgsz=640&device=cpu" \
  -F "file=@sample.jpg"
```

`sample.jpg` is local-only and must not be committed. Success means a JSON
response with `num_detections` and `detections` fields, even when detections
are empty.

## Video job skeleton smoke command

```bash
curl -X POST http://localhost:8000/api/videos/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_id":"demo","run_name":"docker_smoke"}'
```

This endpoint creates a skeleton job and must not run YOLO, ByteTrack,
analytics, or rendering during the smoke check.

## Stop/cleanup instructions

If running detached, stop containers manually:

```bash
docker stop yolov8-api-smoke
docker stop yolov8-streamlit-smoke
```

Do not commit image layers, generated artifacts, weights, videos, CSV, JSON,
JSONL, or MP4 outputs. Optional image cleanup is manual:

```bash
docker image rm yolov8-vehicle-pedestrian:latest
```

## Expected success criteria

- Image builds successfully.
- FastAPI `/health` returns `ok`.
- `/config` returns JSON.
- `/model-status` returns `loaded=false` or another valid status JSON.
- `/predict` returns JSON when mounted weight exists.
- Streamlit starts and binds to port `8501`.
- Video job skeleton creates a job without running compute.
- No repository files are created or modified.

## Failure handling

- Docker missing: install Docker and rerun preflight.
- Daemon not running: start Docker Desktop or the Docker daemon.
- Model weight missing: place the weight under `local_weights/` and update
  `MODEL_PATH`.
- Port already in use: stop the conflicting service or choose another host
  port.
- Dependency import failure: inspect image build logs and dependency files.
- OpenCV/system package issue: capture the import error and decide whether a
  Dockerfile system package change is required.
- Command timeout: stop containers, capture logs, and rerun with a smaller
  manual smoke scope.

## Go/no-go for actual build

Current status: No-Go if Docker CLI unavailable.

Go when Docker CLI and daemon are available and the local weight path is
confirmed. Actual build/run result must be recorded in a later tag if
performed.
