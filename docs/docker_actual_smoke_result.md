# Docker Actual Smoke Result

## Summary

| Field | Value |
| --- | --- |
| Version | v0.14.5-mounted-weight-container-predict-smoke |
| Date | 2026-06-20 |
| Final status | Docker Actual Smoke Passed |
| Reason | Docker image build passed, FastAPI container smoke passed, Streamlit container smoke passed, and mounted-weight `/predict` passed with read-only `local_weights/best.pt`. |

This result records the first actual Docker build/run smoke attempt after the
`v0.14.3` preflight plan, the `v0.14.4` FastAPI dependency-fix rerun, and the
`v0.14.5` mounted-weight `/predict` smoke. Docker image layers, weights,
videos, CSV, JSON, JSONL, MP4, `runs`, `local_outputs`, and `/tmp` outputs
remain local-only artifacts.

## Docker availability

| Check | Result |
| --- | --- |
| docker path | `/usr/local/bin/docker` |
| docker version | Docker version 29.5.3, build d1c06ef |
| docker info exit code | `0` |
| Docker Desktop server architecture | `aarch64` |

## Initial attempt

Initial build command:

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

Initial result:

- image build: passed
- FastAPI container smoke: failed
- `/health`: failed, connection refused
- `/config`: failed, connection refused
- `/model-status`: failed, connection refused
- `/api/videos/analyze`: failed because FastAPI was not running
- root cause summary: `ModuleNotFoundError: No module named 'fastapi'`
- Streamlit container smoke: passed with `HTTP/1.1 200 OK`
- mounted-weight `/predict`: skipped because `local_weights/best.pt` was not
  present and FastAPI did not start

Root cause:

- `Dockerfile` installed `requirements.txt`.
- `fastapi` and `uvicorn` are declared in `requirements-api.txt`.
- Local tests could import FastAPI because the local `.venv` had API
  requirements installed.

## Dependency fix

Change:

```dockerfile
COPY requirements.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-api.txt
```

Reason:

- Keeps API runtime dependencies in `requirements-api.txt`.
- Avoids moving API-specific dependencies into the base project requirements.
- Keeps the fix limited to Docker image dependency installation.
- Does not modify `src/`, `app.py`, or business logic.

## OpenCV runtime library fix

The first mounted-weight `/predict` attempt found that `ultralytics` was
installed in the container but failed while importing OpenCV because
`libxcb.so.1` was missing. `Dockerfile` now installs the minimal native runtime
libraries needed by OpenCV in the slim Python image:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 libxcb1 \
    && rm -rf /var/lib/apt/lists/*
```

This does not change project source code, app code, or Python requirements.

## After dependency fix

Rebuild command:

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

Rebuild result:

- status: passed
- exit code: `0`
- image retained locally: `yolov8-vehicle-pedestrian:latest`
- observed image size: about `9.44GB`
- full build log stayed local under `/tmp` and was not committed

FastAPI command summary:

```bash
docker run -d --rm --name yolov8-api-smoke -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

FastAPI after-fix results:

- container running status: passed
- `/health`: passed, returned `{"status":"ok","service":"yolov8-vehicle-pedestrian-api"}`
- `/config`: passed, returned JSON with `model_path=/app/local_weights/best.pt`
- `/model-status`: passed, returned JSON with `exists=false` and `loaded=false`
- `/api/videos/analyze`: passed, returned `job_id` and `status=created`
- compute status: no YOLO inference, ByteTrack, analytics, or rendering was run

Video job skeleton response summary:

Historical note: this response reflects the `v0.14.4` Docker smoke, when the
video API was still a skeleton. Starting in `v1.1.0`, `POST
/api/videos/analyze` supports async video job execution; `v1.2.0` adds
SQLite-backed job metadata; `v1.3.0` adds Bad Case metadata and GT evaluation
scaffolds; and `v1.4.0` adds registered artifact download endpoints. Docker
smoke has not yet been rerun for the full v1.1-v1.4 API surface.

```json
{
  "status": "created",
  "video_id": "demo",
  "run_name": "docker_smoke_after_dependency_fix",
  "message": "Video execution is not implemented in this skeleton."
}
```

Streamlit rerun command summary:

```bash
docker run -d --rm --name yolov8-streamlit-smoke -p 8501:8501 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Streamlit after-fix result:

- container running status: passed
- HTTP check result: passed, `HTTP/1.1 200 OK` from `http://localhost:8501`
- container stopped after smoke check

## Mounted-weight predict smoke

Result:

- status: passed
- mounted host file: `local_weights/best.pt`
- container model path: `/app/local_weights/best.pt`
- mount mode: read-only
- sha256: `1eb1360fc3d59cc955384912389ea835e218ba62af72bcf96386e0ea6f34af47`
- test image: temporary `/tmp/yolov8_mounted_predict_smoke.jpg`, not committed
- response path: temporary `/tmp/yolov8_mounted_predict_smoke_response.json`, not committed
- response contained required fields: `image_name`, `image_size`, `model_path`,
  `num_detections`, and `detections`
- response status: JSON returned successfully
- `num_detections`: `0`, expected for the blank white 64x64 temporary smoke image
- `num_detections=0` is expected for this blank 64x64 smoke image.

Predict response summary:

```json
{
  "image_name": "yolov8_mounted_predict_smoke.jpg",
  "image_size": {"width": 64, "height": 64},
  "model_path": "/app/local_weights/best.pt",
  "num_detections": 0,
  "detections": []
}
```

Model status:

- before `/predict`: `exists=true`, `loaded=false`
- after `/predict`: `exists=true`, `loaded=true`

No temporary image or prediction response was committed.

## Cleanup

- FastAPI predict smoke container stopped.
- Streamlit container stopped.
- `docker ps --filter name=yolov8` showed no remaining running `yolov8` containers.
- Docker image retained locally for manual follow-up; cleanup is optional.
- No repository outputs were committed.

Optional manual cleanup:

```bash
docker image rm yolov8-vehicle-pedestrian:latest
```

## Asset safety

- no weights, videos, generated CSV/JSON/JSONL, MP4 previews, `runs`, or
  `local_outputs` were added to the repository.
- Weights were mounted read-only with `-v "$PWD/local_weights:/app/local_weights:ro"`.
- No weights are copied into the image by `Dockerfile`.
- No `local_outputs/` or `runs/` artifacts were committed.
- No source videos, tracked videos, CSV, JSON, JSONL, MP4, or `/tmp` outputs were committed.
- The retained local image is not a Git artifact.

## Final status

Final status: Docker Actual Smoke Passed.

The Docker image build succeeded after installing `requirements-api.txt` and
the OpenCV native runtime libraries. FastAPI `/health`, `/config`,
`/model-status`, and `/api/videos/analyze` passed inside the container.
Streamlit container smoke passed. Mounted-weight /predict passed with
`local_weights/best.pt` mounted read-only into `/app/local_weights/best.pt`.

The previous `v0.14.4` state was partial because `local_weights/best.pt` was not
yet prepared. `v0.14.5` closes that mounted-weight `/predict` acceptance item.
