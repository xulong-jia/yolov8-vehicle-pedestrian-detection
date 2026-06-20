# Streamlit Video Demo Page

`v0.12.0` added a read-only Streamlit page for browsing existing video analysis
artifacts. `v1.1.0` added a FastAPI Video Job Launcher to the same page. The
page is still a local demo surface: it either browses existing artifacts or
submits a job to an already running FastAPI service.

## What It Shows

The page can load local artifact paths and display:

- `video_analysis_summary.json` run metrics
- `tracks.csv` row count, unique tracks, frames with tracks, and class counts
- `count_events.csv` preview rows
- `roi_frame_counts.csv` preview rows
- `events.jsonl` preview rows
- tracked preview video path when the file already exists
- synthetic-vs-ByteTrack comparison JSON when provided

Core parsing logic lives in `src/services/video_demo_catalog.py`. Tests cover
that pure-Python catalog service with synthetic `tmp_path` artifacts and do not
depend on Streamlit. Job execution is handled by FastAPI, not directly by the
Streamlit process.

## Run Command

```bash
.venv/bin/streamlit run app/streamlit_video_demo.py
```

Then either:

- enter local artifact paths in the sidebar and click **Load artifacts**, or
- expand **Start or query FastAPI video jobs**, set the FastAPI base URL, model
  path, video path, and runtime parameters, then submit/query a job.

Example local inputs from the ByteTrack validation workflow:

```text
Video analysis run directory:
/tmp/yolov8_bytetrack_pipeline_validation/analytics/bytetrack_validation

Tracked preview video path:
/tmp/yolov8_bytetrack_pipeline_validation/bytetrack_tracked_preview_300.mp4

Tracking comparison JSON path:
/tmp/yolov8_tracking_comparison.json
```

## FastAPI Job Launcher

The launcher depends on a running FastAPI service, for example:

```bash
.venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000
```

The launcher calls:

- `POST /api/videos/analyze`
- `GET /api/videos/jobs/{job_id}`

FastAPI writes job artifacts under `local_outputs/api_video_jobs/<job_id>/`.
Those outputs are local-only and ignored by Git.

## Safety Boundary

- The artifact browser does not run YOLO, ByteTrack, analytics, or rendering.
- The job launcher does not execute video analysis inside Streamlit; it delegates
  to FastAPI.
- It does not copy `/tmp` outputs into the repository.
- Do not commit local `detections.csv`, `tracks.csv`, JSON, JSONL, MP4,
  model weights, source videos, or generated run directories.

## Current Limits

- The launcher requires FastAPI to be running separately.
- It does not validate full-length tracked video quality.
- It is not a production dashboard with authentication, monitoring, or
  multi-user job management.
- SQLite job metadata persistence is provided by FastAPI; a real FastAPI process
  restart smoke for the SQLite index remains pending.

## Recommended Next Steps

- Use this page for local demo review of ByteTrack validation artifacts.
- Use the FastAPI launcher for local controlled video analysis jobs.
- Add production dashboard behavior only after authentication, output retention,
  and monitoring policies are defined.
