# Docker v1 API Smoke Result

## Scope

This document records the `v1.4.1-docker-v1-api-smoke-refresh` runtime smoke.
It refreshes Docker acceptance after the post-final API additions:

- `v1.1.0` async video jobs
- `v1.2.0` SQLite-backed job metadata
- `v1.3.0` Bad Case metadata and GT evaluation scaffold
- `v1.4.0` registered artifact download endpoints

The smoke validates existing Docker/FastAPI behavior only. It does not add new
features, run full video YOLO/ByteTrack, run DeepSORT, run React, or add API
key/auth/logging.

## Commands

Build:

```bash
docker build -t yolov8-vehicle-pedestrian:v1-api-smoke .
```

Run FastAPI:

```bash
docker run --rm --name yolov8-v1-api-smoke \
  -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v /Users/jiaxulong/Documents/yolov8-vehicle-pedestrian-detection/local_weights:/app/local_weights:ro \
  -v /tmp/yolov8_docker_v1_api_smoke/fake_run:/tmp/yolov8_docker_v1_api_smoke/fake_run:ro \
  -v /tmp/yolov8_docker_v1_api_smoke/local_outputs:/app/local_outputs \
  yolov8-vehicle-pedestrian:v1-api-smoke \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

The first run attempt used the host-only `.venv/bin/uvicorn` path and failed
before the app started. The successful command above uses container-installed
`uvicorn`.

## Result Summary

| Check | Result |
| --- | --- |
| Docker build | Passed |
| Docker run FastAPI | Passed |
| `/health` | `{"status":"ok","service":"yolov8-vehicle-pedestrian-api"}` |
| `/model-status` before predict | `exists=true`, `loaded=false`, `model_path=/app/local_weights/best.pt` |
| `/predict` mounted-weight smoke | Passed with a temporary blank `/tmp` image; `num_detections=0` |
| `/model-status` after predict | `exists=true`, `loaded=true` |
| `/api/videos/analyze` attach-mode | Passed with `status=attached` |
| `/api/videos/jobs/{job_id}` | Passed |
| SQLite-backed job metadata | Wrote `/app/local_outputs/api_video_jobs/video_jobs.sqlite3` on the mounted `/tmp` output volume |
| Artifact download | `GET /api/videos/jobs/{job_id}/artifacts/summary/download` returned `200` |
| `/api/bad-cases` POST | Passed |
| `/api/bad-cases` GET | Passed, returned 1 smoke metadata record |

Video job summary:

| Field | Value |
| --- | --- |
| job_id | `4a65422e836e4f65888c0ede98e1bc23` |
| status | `attached` |
| run_dir | `/tmp/yolov8_docker_v1_api_smoke/fake_run` |
| summary_path | `/tmp/yolov8_docker_v1_api_smoke/fake_run/video_analysis_summary.json` |
| downloaded artifact | `summary` |
| download status | `200` |
| downloaded video_id | `docker_v1_api_demo` |

Bad Case metadata summary:

| Field | Value |
| --- | --- |
| POST case_id | `BC-3245a7e7` |
| module | `docker_smoke` |
| case_type | `metadata_only` |
| GET count | `1` |

## Runtime Outputs

Runtime outputs were written only under `/tmp/yolov8_docker_v1_api_smoke`:

```text
/tmp/yolov8_docker_v1_api_smoke/local_outputs/api_video_jobs/video_jobs.sqlite3
/tmp/yolov8_docker_v1_api_smoke/local_outputs/bad_cases/bad_cases.csv
/tmp/yolov8_docker_v1_api_smoke/local_outputs/bad_cases/bad_cases.jsonl
```

These files are local smoke artifacts and are not committed.

## Safety Notes

- No full real video YOLO inference was run.
- No ByteTrack/DeepSORT tracking was run.
- No React, API key/auth, structured logging, or monitoring feature was added.
- `local_weights/best.pt` was mounted read-only and not committed.
- The temporary `/tmp` image, API response summaries, SQLite DB, Bad Case CSV,
  Bad Case JSONL, and Docker image layers are not committed.
