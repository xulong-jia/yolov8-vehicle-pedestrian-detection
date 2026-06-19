# track_video.py CLI Usage

`src/track_video.py` is currently a skeleton CLI for validating video analytics contracts.

Current boundaries:

- does not run YOLO
- does not read frames for detection inference
- does not integrate ByteTrack/DeepSORT
- does not generate tracked video

Current safe modes:

1. synthetic `detections.csv` to `tracks.csv` through the tracker adapter factory
2. video metadata-only mode

## Synthetic detections-to-tracks mode

Use this mode to validate field conversion from `detections.csv` to `tracks.csv`.
Internally, `track_video.py` now obtains the tracker with `create_tracker_adapter(tracker_name)`.
The default tracker is `synthetic`.

Input:

- existing or synthetic `detections.csv`

Output:

- `tracks.csv`

This mode does not read real video.
It does not run YOLO and does not generate tracked video.

Smoke command:

```bash
cat > /tmp/synthetic_detections.csv <<'CSV'
video_id,frame_index,timestamp_sec,detection_id,class_id,class_name,confidence,xmin,ymin,xmax,ymax
demo,0,0.0,1,1,Car,0.91,0,0,10,20
demo,1,0.2,1,1,Car,0.89,1,0,11,20
CSV

python3 src/track_video.py \
  --detections-csv /tmp/synthetic_detections.csv \
  --output-dir /tmp/yolov8_track_video_skeleton \
  --tracker synthetic

ls -lh /tmp/yolov8_track_video_skeleton/tracks.csv
cat /tmp/yolov8_track_video_skeleton/tracks.csv
```

Expected output:

- `tracks.csv` exists
- `track_id` is stable from `detection_id`
- `center_x`, `center_y`, `box_width`, `box_height`, and `box_area` are populated
- `state` is `confirmed`
- `tracker_name` is `synthetic`

`--tracker bytetrack` and `--tracker deepsort` are recognized only as placeholder adapter names at this stage. They currently fail with `NotImplementedError` because the real ByteTrack/DeepSORT dependencies have not been integrated. Do not use them as successful smoke commands yet.

## Two-command smoke flow

Use this flow to connect the current CSV-first detector output to the safe synthetic tracker path. Keep generated files under `/tmp` and do not commit them.

Step 1: generate `detections.csv` with `predict_video.py`.

```bash
python3 src/predict_video.py \
  --model /absolute/path/to/best.pt \
  --source /absolute/path/to/video.mp4 \
  --output-csv /tmp/yolov8_video_smoke/detections.csv \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu \
  --video-id demo
```

Step 2: convert `detections.csv` to `tracks.csv` with the synthetic tracker.

```bash
python3 src/track_video.py \
  --detections-csv /tmp/yolov8_video_smoke/detections.csv \
  --output-dir /tmp/yolov8_video_smoke/tracking \
  --tracker synthetic
```

Expected files:

- `/tmp/yolov8_video_smoke/detections.csv`
- `/tmp/yolov8_video_smoke/tracking/tracks.csv`

Step 1 runs YOLO if you provide a real model and real video. The automated test for this flow uses fake YOLO and `tmp_path` instead. Step 2 still uses the synthetic tracker and is not real ByteTrack/DeepSORT tracking. Keep model weights and videos local, write smoke outputs to `/tmp`, and do not commit `/tmp` outputs, generated `detections.csv`, generated `tracks.csv`, real videos, or model weights.

## Organizing outputs with Video Analysis Center

After `detections.csv` and `tracks.csv` already exist, `src/services/video_analysis_job.py` can organize them into a `VideoAnalysisCenter` run directory. This is currently a service function used from Python and tests, not a CLI command.

The job skeleton copies existing CSV artifacts and writes:

- `metadata.json`
- `detections.csv`
- `tracks.csv`
- `video_analysis_summary.json`

It does not run YOLO, does not run a tracker, and does not render tracked video. Use it only with already generated CSV files and keep generated run outputs outside Git-tracked directories unless they are deliberate tiny documentation examples.

## Three-step Video Analysis Center smoke flow

Use this flow to produce `detections.csv`, convert it to synthetic `tracks.csv`, and organize both files into a `VideoAnalysisCenter` run directory.

Step 1: generate `detections.csv`.

```bash
python3 src/predict_video.py \
  --model /absolute/path/to/best.pt \
  --source /absolute/path/to/video.mp4 \
  --output-csv /tmp/yolov8_video_job/detections.csv \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu \
  --video-id demo
```

Step 2: generate synthetic `tracks.csv`.

```bash
python3 src/track_video.py \
  --detections-csv /tmp/yolov8_video_job/detections.csv \
  --output-dir /tmp/yolov8_video_job/tracking \
  --tracker synthetic
```

Step 3: organize outputs with `video_analysis_job`.

There is no CLI for this step yet; use the Python service function.

```bash
python3 - <<'PY'
from src.services.video_analysis_job import create_video_analysis_job_run

summary = create_video_analysis_job_run(
    run_name="demo_run",
    base_dir="/tmp/yolov8_video_job/video_analysis",
    detections_csv="/tmp/yolov8_video_job/detections.csv",
    tracks_csv="/tmp/yolov8_video_job/tracking/tracks.csv",
    metadata={
        "video_id": "demo",
        "input_video": "/absolute/path/to/video.mp4",
        "mode": "three_step_smoke",
    },
)
print(summary)
PY
```

Expected files:

- `/tmp/yolov8_video_job/detections.csv`
- `/tmp/yolov8_video_job/tracking/tracks.csv`
- `/tmp/yolov8_video_job/video_analysis/demo_run/metadata.json`
- `/tmp/yolov8_video_job/video_analysis/demo_run/video_analysis_summary.json`

Step 1 runs YOLO if you provide a real model and real video. Step 2 still uses the synthetic tracker and is not real ByteTrack/DeepSORT tracking. Step 3 does not run YOLO or a tracker; it only organizes existing CSV files. Keep all smoke-flow outputs under `/tmp`. Do not commit `/tmp` outputs, model weights, real videos, `runs/`, or zip archives.

## Analytics on existing tracks

After `detections.csv` and `tracks.csv` already exist, the service function `create_video_analysis_job_run(..., run_analytics=True, analytics_config=...)` can run line counting, ROI counting, and event rules on the existing track rows. There is no CLI command for this step yet.

Example service-function call:

```bash
python3 - <<'PY'
from src.services.video_analysis_job import create_video_analysis_job_run

analytics_config = {
    "line": {
        "id": "line_main",
        "name": "Main Line",
        "points": [[0, 0], [10, 0]],
        "directions": {"positive": "in", "negative": "out"},
        "target_classes": ["Car", "Person"],
        "enabled": True,
    },
    "roi": {
        "id": "roi_main",
        "name": "Main ROI",
        "polygon": [[0, 0], [10, 0], [10, 10], [0, 10]],
        "target_classes": ["Car", "Person"],
        "enabled": True,
    },
    "event_rules": {
        "long_stay": {
            "event_type": "long_stay",
            "enabled": True,
            "roi_id": "roi_main",
            "target_classes": ["Car", "Person"],
            "parameters": {"min_duration_sec": 2.0},
        }
    },
}

summary = create_video_analysis_job_run(
    run_name="demo_run_with_analytics",
    base_dir="/tmp/yolov8_video_job/video_analysis",
    detections_csv="/tmp/yolov8_video_job/detections.csv",
    tracks_csv="/tmp/yolov8_video_job/tracking/tracks.csv",
    metadata={"video_id": "demo", "mode": "analytics_on_tracks"},
    analytics_config=analytics_config,
    run_analytics=True,
)
print(summary)
PY
```

This service function does not run YOLO, does not run a tracker, and only reads existing `detections.csv` and `tracks.csv`. It writes `count_events.csv`, `roi_frame_counts.csv`, `events.jsonl`, and an updated `video_analysis_summary.json` under the run directory. Keep these outputs under `/tmp` for smoke usage and do not commit generated `/tmp` outputs.

## Four-step local video analysis flow

This is the current safe local chain from video detection export to synthetic tracking to Video Analysis Center analytics.

Step 1: export detections.

```bash
python3 src/predict_video.py \
  --model /absolute/path/to/best.pt \
  --source /absolute/path/to/video.mp4 \
  --output-csv /tmp/yolov8_four_step/detections.csv \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu \
  --video-id demo
```

Step 2: convert detections to synthetic tracks.

```bash
python3 src/track_video.py \
  --detections-csv /tmp/yolov8_four_step/detections.csv \
  --output-dir /tmp/yolov8_four_step/tracking \
  --tracker synthetic
```

Step 3/4: organize the CSV artifacts and run analytics.

The analytics job is currently a Python service function, not a CLI command.

```bash
python3 - <<'PY'
from src.services.video_analysis_job import create_video_analysis_job_run

analytics_config = {
    "line": {
        "id": "line_main",
        "name": "Main Line",
        "points": [[0, 0], [10, 0]],
        "directions": {"positive": "in", "negative": "out"},
        "target_classes": ["Car", "Person"],
        "enabled": True,
    },
    "roi": {
        "id": "roi_main",
        "name": "Main ROI",
        "polygon": [[0, 0], [20, 0], [20, 30], [0, 30]],
        "target_classes": ["Car", "Person"],
        "enabled": True,
    },
    "event_rules": {
        "long_stay": {
            "id": "long_stay_main",
            "event_type": "long_stay",
            "enabled": True,
            "roi_id": "roi_main",
            "target_classes": ["Car", "Person"],
            "parameters": {"min_duration_sec": 2.0, "cooldown_sec": 10.0},
        }
    },
}

summary = create_video_analysis_job_run(
    run_name="demo_run",
    base_dir="/tmp/yolov8_four_step/video_analysis",
    detections_csv="/tmp/yolov8_four_step/detections.csv",
    tracks_csv="/tmp/yolov8_four_step/tracking/tracks.csv",
    metadata={
        "video_id": "demo",
        "input_video": "/absolute/path/to/video.mp4",
        "mode": "four_step_smoke",
    },
    analytics_config=analytics_config,
    run_analytics=True,
)
print(summary)
PY
```

Expected files:

- `/tmp/yolov8_four_step/detections.csv`
- `/tmp/yolov8_four_step/tracking/tracks.csv`
- `/tmp/yolov8_four_step/video_analysis/demo_run/metadata.json`
- `/tmp/yolov8_four_step/video_analysis/demo_run/count_events.csv`
- `/tmp/yolov8_four_step/video_analysis/demo_run/roi_frame_counts.csv`
- `/tmp/yolov8_four_step/video_analysis/demo_run/events.jsonl`
- `/tmp/yolov8_four_step/video_analysis/demo_run/video_analysis_summary.json`

Step 1 runs YOLO if you provide a real model and real video. Step 2 still uses the synthetic tracker and is not real ByteTrack/DeepSORT tracking. Step 3/4 does not run YOLO or a tracker; it only organizes existing CSV files and executes analytics. Do not commit `/tmp` outputs, model weights, or real videos.

## Unified four-step smoke runner

`src/run_video_analysis_smoke.py` wraps the current four-step local flow in one command.

```bash
.venv/bin/python -m src.run_video_analysis_smoke \
  --model /absolute/path/to/best.pt \
  --source /absolute/path/to/video.mp4 \
  --output-dir /tmp/yolov8_four_step_runner \
  --video-id demo \
  --run-name demo_run \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu
```

Expected outputs:

- `/tmp/yolov8_four_step_runner/detections.csv`
- `/tmp/yolov8_four_step_runner/tracking/tracks.csv`
- `/tmp/yolov8_four_step_runner/video_analysis/demo_run/metadata.json`
- `/tmp/yolov8_four_step_runner/video_analysis/demo_run/count_events.csv`
- `/tmp/yolov8_four_step_runner/video_analysis/demo_run/roi_frame_counts.csv`
- `/tmp/yolov8_four_step_runner/video_analysis/demo_run/events.jsonl`
- `/tmp/yolov8_four_step_runner/video_analysis/demo_run/video_analysis_summary.json`

The runner uses `predict_video.py`, so it runs YOLO when you provide a real model and video source. The tracker is still the synthetic tracker, not real ByteTrack/DeepSORT. The runner does not render tracked video. Use `/tmp` or another gitignored output directory, and do not commit generated outputs, model weights, or real videos.

For local execution, prefer module-style invocation: `.venv/bin/python -m src.run_video_analysis_smoke ...`. If direct script execution reports `ModuleNotFoundError: No module named 'src'`, use the module entrypoint first. The fallback is `PYTHONPATH=. .venv/bin/python src/run_video_analysis_smoke.py ...`.

The first real local smoke run is documented in [Real Local Smoke Run Result](real_local_smoke_run_result.md). It produced `21988` detections and `34` synthetic tracks using local-only inputs and `/tmp` outputs.

## Real local smoke preflight

Before running a real local smoke command, run the preflight checker. It does not run YOLO, does not create the output directory, does not write `detections.csv`, `tracks.csv`, or summaries, and does not run tracking. It only checks paths, optional module availability, and prints command previews.

```bash
.venv/bin/python -m src.smoke_preflight \
  --model /absolute/path/to/best.pt \
  --video /absolute/path/to/video.mp4 \
  --output-dir /tmp/yolov8_real_smoke \
  --video-id demo \
  --run-name demo_run \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu
```

Expected output:

- `ok`: `true` or `false`
- checks for `model_path`, `video_path`, `output_dir`, `ultralytics`, and `cv2`
- command previews for `predict_video.py`, `track_video.py --tracker synthetic`, and `run_video_analysis_smoke.py`

## Analytics config suggestion from tracks.csv

After a smoke run has produced `tracks.csv`, use the analytics config suggester to inspect coordinate distributions and generate a starting-point config suggestion.

```bash
.venv/bin/python -m src.analytics_config_suggester \
  --tracks-csv /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --video-id demo \
  --output-json /tmp/yolov8_real_smoke/suggested_analytics_config.json
```

This command does not rerun YOLO, does not run a tracker, and only reads the existing `tracks.csv`. Keep the suggested JSON under `/tmp` or another ignored local path. Do not commit generated `tracks.csv`, suggested config JSON, real videos, model weights, or smoke outputs.

Details: [Analytics Config Tuning](analytics_config_tuning.md)

## Analytics-only rerun

After generating a suggested analytics config, rerun only the analytics layer against existing CSV artifacts:

```bash
.venv/bin/python -m src.analytics_only_rerun \
  --detections-csv /tmp/yolov8_real_smoke/detections.csv \
  --tracks-csv /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --config-json /tmp/yolov8_real_smoke/suggested_analytics_config.json \
  --output-dir /tmp/yolov8_real_smoke_analytics_rerun \
  --video-id demo \
  --run-name suggested_config_rerun \
  --source-run-dir /tmp/yolov8_real_smoke
```

This command does not run YOLO, does not run a tracker, and does not generate tracked video. Inputs are existing `detections.csv`, `tracks.csv`, and config JSON. Write outputs to `/tmp` or another ignored path, and do not commit generated CSV, JSON, JSONL, videos, or weights.

## Analytics overlay plan

Before rendering overlays, generate a JSON plan that validates the suggested line and ROI against `tracks.csv` coordinate distributions:

```bash
.venv/bin/python -m src.analytics_overlay_plan \
  --tracks-csv /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --config-json /tmp/yolov8_real_smoke/suggested_analytics_config.json \
  --video-id demo \
  --output-json /tmp/yolov8_real_smoke/analytics_overlay_plan.json
```

This command does not run YOLO, does not run a tracker, does not read or render video frames, and does not generate tracked video. Keep the JSON output under `/tmp` or another ignored path, and do not commit generated overlay plans.

## Tracked video rendering

After a source video and `tracks.csv` already exist, render a local tracked preview:

```bash
.venv/bin/python -m src.render_tracked_video \
  --video /absolute/path/to/video.mp4 \
  --tracks-csv /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --output-video /tmp/yolov8_real_smoke/tracked_preview_300.mp4 \
  --config-json /tmp/yolov8_real_smoke/suggested_analytics_config.json \
  --overlay-plan-json /tmp/yolov8_real_smoke/analytics_overlay_plan.json \
  --max-frames 300
```

This does not rerun YOLO and does not run a tracker. It uses existing tracks to draw bbox, track labels, line overlays, and ROI overlays. Write output videos to `/tmp` or another ignored path, and do not commit generated preview videos.

## ByteTrack discovery

`v0.11.0` adds a discovery helper for planning real ByteTrack integration:

```bash
.venv/bin/python -m src.tracking.bytetrack_discovery --pretty
```

This command does not run YOLO, does not run ByteTrack, does not run DeepSORT, and does not create output files. It checks optional module availability with `importlib.util.find_spec`, summarizes candidate integration paths, and documents the `tracks.csv` contract that future ByteTrack exports must satisfy.

The recommended next implementation path is a short, explicitly approved Ultralytics `model.track(..., tracker="bytetrack.yaml")` spike that writes real ByteTrack-like `tracks.csv` output under `/tmp`. Keep the synthetic tracker fallback until real ByteTrack quality is reviewed.

## Ultralytics ByteTrack short video spike

`v0.11.1` adds a short-video spike tool:

```bash
.venv/bin/python -m src.track_video_bytetrack_spike \
  --model /absolute/path/to/best.pt \
  --video /absolute/path/to/video.mp4 \
  --output-dir /tmp/yolov8_bytetrack_spike \
  --video-id demo \
  --tracker bytetrack.yaml \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu \
  --max-frames 300 \
  --render-preview \
  --config-json /tmp/yolov8_real_smoke/suggested_analytics_config.json \
  --overlay-plan-json /tmp/yolov8_real_smoke/analytics_overlay_plan.json
```

Expected outputs, when the local ByteTrack runtime dependencies are available:

- `/tmp/yolov8_bytetrack_spike/bytetrack_tracks.csv`
- `/tmp/yolov8_bytetrack_spike/bytetrack_tracked_preview_300.mp4` when `--render-preview` is used

Do not commit these outputs. This spike uses Ultralytics ByteTrack-style tracking and is different from the existing synthetic tracker, but it is still not full production integration. The first local attempt was blocked by missing `lap`; no tracks CSV or preview video was produced.

## Successful ByteTrack short-video spike after lap install

`v0.11.2` verifies the local Ultralytics ByteTrack runtime dependency path. Install and verify `lap` in the local `.venv` before rerunning the short spike:

```bash
python -m pip install lap
```

The local verification used `lap==0.5.13`, `ultralytics==8.4.64`, and `cv2==4.13.0`. This dependency is not yet pinned in requirements; the decision to add `lap` to project requirements is still pending.

Successful local command:

```bash
.venv/bin/python -m src.track_video_bytetrack_spike \
  --model local_weights/yolov8s_640_50epochs/best.pt \
  --video local_videos/source/pexels_crosswalk_traffic_demo.mp4 \
  --output-dir /tmp/yolov8_bytetrack_spike \
  --video-id demo \
  --tracker bytetrack.yaml \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu \
  --max-frames 300 \
  --render-preview \
  --config-json /tmp/yolov8_real_smoke/suggested_analytics_config.json \
  --overlay-plan-json /tmp/yolov8_real_smoke/analytics_overlay_plan.json
```

Local output summary:

- `frames_seen=300`
- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- `bytetrack_tracks.csv`: `/tmp/yolov8_bytetrack_spike/bytetrack_tracks.csv`
- tracked preview: `/tmp/yolov8_bytetrack_spike/bytetrack_tracked_preview_300.mp4`

Do not commit `/tmp` outputs, generated CSV files, generated MP4 files, local model weights, or local source videos.

## Standard track_video ByteTrack runtime

`v0.11.4` supports the standard `track_video.py --tracker bytetrack` runtime. This path uses Ultralytics `model.track(..., tracker="bytetrack.yaml")` directly from a video source and writes real ByteTrack `tracks.csv` rows to the user-provided output directory.

Command:

```bash
.venv/bin/python -m src.track_video \
  --video-source local_videos/source/pexels_crosswalk_traffic_demo.mp4 \
  --model local_weights/yolov8s_640_50epochs/best.pt \
  --output-dir /tmp/yolov8_track_video_bytetrack \
  --tracker bytetrack \
  --max-frames 300 \
  --video-id demo \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu
```

Output:

- `/tmp/yolov8_track_video_bytetrack/tracks.csv`

This runtime does not use `detections.csv` as input. It calls Ultralytics `model.track` and normalizes `boxes.id` into the existing `tracks.csv` contract. It requires Ultralytics and `lap`; `lap==0.5.13` has been verified locally, but the requirements pin decision is still pending.

The default is a short `max_frames=300` run to avoid accidental full-length processing. Keep outputs under `/tmp` or another ignored local directory and do not commit generated CSV, MP4, model weights, or source videos.

Local v0.11.4 standard CLI validation:

- `tracks.csv` lines: `747` including header
- `track_rows=746`
- `unique_tracks=25`
- `frames_with_rows=261`
- `class_counts`: `Person=720`, `Bus=26`

The legacy spike command remains available for focused experiments:

```bash
.venv/bin/python -m src.track_video_bytetrack_spike ...
```

The synthetic tracker path remains available and unchanged for contract tests and fallback usage.

## Video metadata-only mode

Use this mode to validate video path reading, metadata extraction, and `frame_index.csv` creation.

This mode does not run detection, does not run tracking, and does not save frame images.

Smoke command:

```bash
VIDEO_PATH="/absolute/path/to/demo.mp4"

python3 src/track_video.py \
  --video-source "$VIDEO_PATH" \
  --output-dir /tmp/yolov8_video_metadata_only \
  --metadata-only \
  --sample-every-n 5 \
  --max-frames 20

ls -lh /tmp/yolov8_video_metadata_only/video_metadata.json
ls -lh /tmp/yolov8_video_metadata_only/frame_index.csv
cat /tmp/yolov8_video_metadata_only/video_metadata.json
head /tmp/yolov8_video_metadata_only/frame_index.csv
```

Expected output:

- `video_metadata.json` contains `fps`, `width`, `height`, `frame_count`, and `duration_sec`
- `frame_index.csv` contains sampled `frame_index` and `timestamp_sec`
- no frames, images, or videos are saved

## Recommended output policy

- For smoke commands, use `/tmp` or another external temp directory.
- Do not write generated outputs into Git-tracked `docs`, `src`, or `tests` directories.
- Do not commit `tracks.csv`, `frame_index.csv`, or `video_metadata.json` unless they are tiny intentional documentation examples.
- Do not commit real videos, model weights, runs, `local_outputs`, dataset splits, or zip files.

## Next planned runtime steps

Pending runtime work:

- real ByteTrack/DeepSORT dependency integration
- real ByteTrack `tracks.csv` export
- synthetic vs ByteTrack track comparison
- Video Analysis Center integration for real video jobs
- Streamlit video pages
- FastAPI video jobs
- real video smoke demo

## Validate ByteTrack tracks with analytics and renderer

`v0.11.5` adds a validation wrapper for the post-tracking pipeline. It consumes
existing `detections.csv` and standard ByteTrack `tracks.csv`, then runs
analytics-only rerun and optionally renders a tracked preview.

```bash
.venv/bin/python -m src.validate_bytetrack_pipeline \
  --detections-csv /tmp/yolov8_real_smoke/detections.csv \
  --tracks-csv /tmp/yolov8_track_video_bytetrack/tracks.csv \
  --config-json /tmp/yolov8_real_smoke/suggested_analytics_config.json \
  --video local_videos/source/pexels_crosswalk_traffic_demo.mp4 \
  --output-dir /tmp/yolov8_bytetrack_pipeline_validation \
  --run-name bytetrack_validation \
  --video-id demo \
  --render-preview \
  --overlay-plan-json /tmp/yolov8_real_smoke/analytics_overlay_plan.json \
  --max-frames 300
```

This command does not rerun YOLO and does not rerun the tracker. It writes only
local validation outputs under `/tmp`; do not commit the generated CSV, JSON,
JSONL, or MP4 files.

Local v0.11.5 result:

- `track_rows=746`, `unique_tracks=25`, `frames_with_tracks=261`
- analytics rerun succeeded with `track_count=25`
- renderer wrote a readable 300-frame ByteTrack preview

## Compare synthetic and ByteTrack tracks

`v0.11.6` adds a comparison helper for existing synthetic and ByteTrack
`tracks.csv` outputs:

```bash
.venv/bin/python -m src.compare_tracking_outputs \
  --synthetic-tracks /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --bytetrack-tracks /tmp/yolov8_track_video_bytetrack/tracks.csv \
  --synthetic-summary /tmp/yolov8_real_smoke_analytics_rerun/suggested_config_rerun/video_analysis_summary.json \
  --bytetrack-summary /tmp/yolov8_bytetrack_pipeline_validation/analytics/bytetrack_validation/video_analysis_summary.json \
  --video-id demo \
  --output-json /tmp/yolov8_tracking_comparison.json
```

The command does not run YOLO, does not run ByteTrack, and does not render
video. Write `--output-json` to `/tmp` or another ignored path and do not commit
the generated comparison JSON.

## Browse Local Video Artifacts with Streamlit

`v0.12.0` adds a read-only Streamlit artifact browser:

```bash
.venv/bin/streamlit run app/streamlit_video_demo.py
```

Use it to inspect an existing Video Analysis Center run directory, an existing
tracked preview MP4, and an optional synthetic-vs-ByteTrack comparison JSON.

The page does not run YOLO, does not run ByteTrack, does not rerun analytics,
and does not render new tracked video. Keep generated outputs under `/tmp` or
another ignored local path and do not commit CSV, JSON, JSONL, MP4, weights, or
source videos.
