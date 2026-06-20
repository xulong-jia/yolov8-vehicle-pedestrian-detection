# Docker Actual Smoke Result

## Summary

| Field | Value |
| --- | --- |
| Version | v0.14.4-docker-actual-build-smoke |
| Date | 2026-06-20 |
| Final status | Partial Docker Actual Smoke Passed — mounted-weight predict pending |
| Reason | Docker image build passed, FastAPI container smoke passed after installing API requirements in the image, and Streamlit container smoke passed. Mounted-weight `/predict` remains skipped because `local_weights/best.pt` is not present. |

This result records the first actual Docker build/run smoke attempt after the
`v0.14.3` preflight plan, plus the dependency-fix rerun for the FastAPI
container. Docker image layers, weights, videos, CSV, JSON, JSONL, MP4,
`runs`, `local_outputs`, and `/tmp` outputs remain local-only artifacts.

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

- status: skipped
- reason: `local_weights/best.pt` was not present
- classification: `skipped_missing_local_weight`

No sample image or prediction response was created or committed. A future
mounted-weight `/predict` smoke requires a local, untracked `best.pt` mounted
read-only into the container.

## Cleanup

- FastAPI container stopped.
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

Final status: Partial Docker Actual Smoke Passed — mounted-weight predict pending.

The Docker image build succeeded after installing `requirements-api.txt`.
FastAPI `/health`, `/config`, `/model-status`, and `/api/videos/analyze`
passed inside the container. Streamlit container smoke also passed. Full Docker
deployment acceptance remains incomplete only for mounted-weight `/predict`,
which is pending until an untracked local `local_weights/best.pt` is available.
