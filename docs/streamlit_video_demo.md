# Streamlit Video Demo Page

`v0.12.0` adds a read-only Streamlit page for browsing existing video analysis
artifacts. The page is a presentation layer only: it does not run YOLO, does
not run ByteTrack, does not run analytics, and does not render new videos.

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
depend on Streamlit.

## Run Command

```bash
.venv/bin/streamlit run app/streamlit_video_demo.py
```

Then enter local artifact paths in the sidebar and click **Load artifacts**.

Example local inputs from the ByteTrack validation workflow:

```text
Video analysis run directory:
/tmp/yolov8_bytetrack_pipeline_validation/analytics/bytetrack_validation

Tracked preview video path:
/tmp/yolov8_bytetrack_pipeline_validation/bytetrack_tracked_preview_300.mp4

Tracking comparison JSON path:
/tmp/yolov8_tracking_comparison.json
```

## Safety Boundary

- The page is read-only.
- It does not run YOLO.
- It does not run ByteTrack.
- It does not run analytics.
- It does not generate videos.
- It does not copy `/tmp` outputs into the repository.
- Do not commit local `detections.csv`, `tracks.csv`, JSON, JSONL, MP4,
  model weights, source videos, or generated run directories.

## Current Limits

- This is not a job launcher.
- It does not validate full-length tracked video quality.
- It does not provide FastAPI endpoints.
- It does not provide database persistence.
- It expects artifact files to already exist locally.

## Recommended Next Steps

- Use this page for local demo review of ByteTrack validation artifacts.
- Add a FastAPI video job endpoint later if productized serving is required.
- Add Streamlit job-launch controls only after the safe local runtime and output
  policy are finalized.
