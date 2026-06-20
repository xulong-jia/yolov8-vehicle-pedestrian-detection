# SQLite Job Restart Smoke Result

## Scope

This document records the `v1.3.2-sqlite-job-restart-smoke` acceptance check for
the FastAPI video job metadata index.

The smoke used an attach-mode fake VideoAnalysisCenter run under `/tmp`:

```text
/tmp/yolov8_sqlite_restart_smoke/demo_run/video_analysis_summary.json
```

No YOLO inference, ByteTrack/DeepSORT tracking, analytics execution, rendering,
Docker build, or Docker run was executed.

## Commands

The FastAPI service was started locally:

```bash
.venv/bin/uvicorn src.api:app --host 127.0.0.1 --port 8000
```

The job was created with only `video_id`, `run_name`, and `run_dir`:

```bash
curl -X POST http://127.0.0.1:8000/api/videos/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "sqlite_restart_demo",
    "run_name": "sqlite_restart_demo_run",
    "run_dir": "/tmp/yolov8_sqlite_restart_smoke/demo_run"
  }'
```

Then the service was stopped, restarted, and the same job was queried again:

```bash
curl http://127.0.0.1:8000/api/videos/jobs/548680e9422447068ac92e1ff76ace37
```

## Result

| Field | Value |
| --- | --- |
| job_id | `548680e9422447068ac92e1ff76ace37` |
| status before restart | `attached` |
| status after restart | `attached` |
| run_dir | `/tmp/yolov8_sqlite_restart_smoke/demo_run` |
| summary_path | `/tmp/yolov8_sqlite_restart_smoke/demo_run/video_analysis_summary.json` |
| artifact_paths | `{"summary": "/tmp/yolov8_sqlite_restart_smoke/demo_run/video_analysis_summary.json"}` |

The same `job_id` remained queryable after a real FastAPI process restart. The
job metadata was restored from:

```text
local_outputs/api_video_jobs/video_jobs.sqlite3
```

The SQLite database stores metadata only. It does not store artifact file
contents, model weights, source videos, CSV contents, JSON contents, JSONL
contents, or rendered videos.

## Repository Safety

- `local_outputs/api_video_jobs/video_jobs.sqlite3` was generated locally and is
  ignored by Git.
- `/tmp/yolov8_sqlite_restart_smoke/` was not copied into the repository.
- No `.pt`, `.onnx`, source video, run output, CSV, JSON, JSONL, rendered video,
  Docker image, or Docker container output is committed.

## Remaining Docker Boundary

This smoke verifies local FastAPI process restart behavior only. Docker runtime
smoke has not yet been refreshed for the `v1.1`-`v1.4` API additions, including
async video jobs, SQLite metadata, Bad Case metadata, GT evaluation scaffold,
and artifact download endpoints.
