# Docker Deployment

## Current Status

`v0.14.1 static acceptance` adds Docker deployment static acceptance for the final execution
manual's Stage 8 requirements. This means the Dockerfile, `.dockerignore`, and
deployment documentation are checked for the expected build/run commands, weight
mount policy, and large-asset exclusions.

`v0.14.1` was static acceptance only. `v0.14.4` later executed actual Docker
build/run smoke locally and records the result in
`docs/docker_actual_smoke_result.md`.

For the consolidated final acceptance status, see
`docs/final_acceptance_checklist.md`. The checklist preserves actual
Docker build/run and mounted-weight container prediction as manual follow-up
acceptance items that were later closed by `v0.14.4` and `v0.14.5`.

`v0.14.3` adds `docs/docker_actual_smoke_plan.md`, which records the initial
Docker availability blocker and the exact future actual smoke commands. That
preflight found Docker CLI/daemon unavailable (`docker_info_exit=127`), so no
actual build/run was executed in that step.

`v0.14.4` adds `docs/docker_actual_smoke_result.md`, recording the first actual
Docker build/run smoke. The initial FastAPI container run failed because
`fastapi` was missing inside the built image. The Dockerfile now installs
`requirements-api.txt`; after rebuilding, FastAPI `/health`, `/config`,
`/model-status`, and `/api/videos/analyze` passed. Streamlit container smoke
also passed. Mounted-weight `/predict` was still open at that point because
`local_weights/best.pt` was not present; `v0.14.5` closed it.

`v0.14.5` completes the mounted-weight container `/predict` smoke. A local
ignored `local_weights/best.pt` was mounted read-only at
`/app/local_weights/best.pt`, `/predict` returned JSON with the required fields,
and the final Docker actual smoke status is `Docker Actual Smoke Passed`.

Post-final note: `v1.1.0` adds async FastAPI video jobs, `v1.2.0` adds the
SQLite-backed job metadata index at
`local_outputs/api_video_jobs/video_jobs.sqlite3`, and `v1.3.0` adds Bad Case
metadata plus GT evaluation scaffolds. The Docker smoke recorded here has not
yet been rerun for the complete v1.1-v1.3 API surface.

## Prerequisites

- Docker installed on the host machine.
- Local model weights available on the host and mounted at runtime.
- Model weights are never committed and are never baked into the image.
- Optional local videos, Video Analysis Center runs, and tracked-preview
  artifacts should be mounted only when needed for local review.

## Build Command

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

The image should include code, configs, and lightweight documentation assets
only. It should not include `local_weights/`, dataset split folders, generated
outputs, or large videos.

The Docker image installs the base runtime from `requirements.txt` and API
runtime dependencies from `requirements-api.txt`.

## Run FastAPI Container

Use Docker command override to start the FastAPI service:

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

The `local_weights` volume mount is read-only. Replace the mounted directory or
`MODEL_PATH` value if your local weight file uses a different path.

## FastAPI Smoke Commands

Health:

```bash
curl http://localhost:8000/health
```

Config and model status:

```bash
curl http://localhost:8000/config
curl http://localhost:8000/model-status
```

Image predict smoke:

```bash
curl -X POST "http://localhost:8000/predict?conf=0.25&imgsz=640&device=cpu" \
  -F "file=@sample.jpg"
```

Video job smoke:

```bash
curl -X POST http://localhost:8000/api/videos/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "video_id":"demo",
    "run_name":"demo_run",
    "model_path":"/app/local_weights/best.pt",
    "source":"/app/local_videos/source/demo.mp4",
    "conf":0.25,
    "imgsz":640,
    "device":"cpu"
  }'
```

The video job endpoint creates an async job, records metadata in SQLite, and
delegates execution to the existing four-step local flow. For Docker use, mount
source videos and `local_outputs` explicitly if you intend to run this workflow.
The SQLite file and generated artifacts remain local-only under
`local_outputs/api_video_jobs/`.

## Artifact Attach Smoke

To attach an existing run directory, mount it into the container and pass the
container-visible path:

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  -v "$PWD/local_outputs:/app/local_outputs:rw" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Then:

```bash
curl -X POST http://localhost:8000/api/videos/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_id":"demo","run_name":"demo_run","run_dir":"/app/local_outputs/run1"}'
```

Only attach directories that already contain existing Video Analysis Center
artifacts when using `run_dir` attach mode. Full async execution requires local
model/video paths visible inside the container and a writable `local_outputs`
mount for job artifacts and `video_jobs.sqlite3`.

## Run Streamlit Container

Use Docker command override to start the Streamlit image demo:

```bash
docker run --rm -p 8501:8501 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

The default Dockerfile command also starts Streamlit on port `8501`.

## Asset Policy

- Never bake weights into the Docker image.
- Mount `local_weights` read-only at runtime.
- Do not commit generated outputs.
- Keep `local_outputs/`, `runs/`, source videos, and full datasets outside Git.
- Do not commit CSV, JSON, JSONL, MP4, model weights, ONNX files, or Docker
  build artifacts generated by local smoke runs.

## Dockerfile Static Acceptance Checklist

- `Dockerfile` exists.
- `MODEL_PATH` is defined as an environment variable.
- Application code and configs are copied into `/app`.
- The default command can start Streamlit.
- FastAPI can be started with Docker command override using
  `uvicorn src.api:app --host 0.0.0.0 --port 8000`.

## .dockerignore Static Acceptance Checklist

`.dockerignore` must exclude:

- `.venv`
- `__pycache__`
- `runs`
- `local_outputs`
- `local_weights`
- `local_videos/source`
- `dataset/train`
- `dataset/valid`
- `dataset/test`
- `*.pt`
- `*.pth`
- `*.onnx`
- `*.mp4`
- `*.avi`
- `*.mov`
- `*.mkv`
- `*.zip`

## Validation Commands

Before committing Docker-related changes, run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache .venv/bin/python -m pytest tests/test_docker_deployment_docs.py -q
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache make check
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache make api-check
make danger-check
make list-large-docs
```

`make list-large-docs` may report the known retained demo video under
`docs/video_demos/`.

## Actual Build Status

Actual Docker build/run smoke has been run locally for `v0.14.4`:

- `docker build -t yolov8-vehicle-pedestrian:latest .` passed.
- FastAPI container smoke with `/health`, `/config`, `/model-status`, and
  `/api/videos/analyze` passed after installing `requirements-api.txt`.
- Streamlit container smoke on port `8501` passed.
- Mounted-weight `/predict` smoke passed in `v0.14.5` with
  `local_weights/best.pt` mounted read-only.
- Docker smoke has not yet been refreshed for the v1.1-v1.3 async video job,
  SQLite metadata, Bad Case metadata, and GT evaluation scaffold additions.

See `docs/docker_actual_smoke_plan.md` for the current preflight result,
manual prerequisites, success criteria, and failure handling.
See `docs/docker_actual_smoke_result.md` for the first actual smoke result and
the mounted-weight `/predict` rerun.

## Related Files

- `Dockerfile`
- `.dockerignore`
- `docs/deployment_guide.md`
- `docs/api_usage.md`
- `docs/docker_actual_smoke_plan.md`
- `docs/docker_actual_smoke_result.md`
- `docs/final_acceptance_checklist.md`
- `docs/model_loading_strategy.md`
- `docs/model_weight_policy.md`
