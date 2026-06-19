# ByteTrack Runtime Integration Plan

`v0.11.3` prepares the transition from the successful ByteTrack spike into a formal `track_video.py --tracker bytetrack` runtime path. This step adds planning and a pure-Python contract helper only. It does not rerun YOLO, does not rerun ByteTrack, does not render video, and does not copy local `/tmp` outputs.

## Current State

- `v0.11.0`: ByteTrack discovery is complete.
- `v0.11.1`: `src/track_video_bytetrack_spike.py` short-video spike tool is complete.
- `v0.11.2`: `lap` was verified locally and the 300-frame Ultralytics ByteTrack spike succeeded.

Successful local spike result:

- `lap==0.5.13` verified in the local `.venv`
- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- tracked preview readable by cv2: `300` frames, `29.97` FPS, `1280x720`
- outputs remained under `/tmp/yolov8_bytetrack_spike` and were not committed

## Still Not Complete

- requirements pin decision for `lap`
- formal `track_video.py --tracker bytetrack` runtime
- analytics rerun on ByteTrack tracks
- synthetic vs ByteTrack comparison
- full-length ByteTrack validation
- Streamlit/FastAPI video workflow integration

## Recommended Runtime Architecture

1. Keep the synthetic tracker as the default safe fallback.
2. Add a `track_video.py` video-source path for `--tracker bytetrack`.
3. Internally call Ultralytics `model.track(..., tracker="bytetrack.yaml", stream=True, persist=True)`.
4. Normalize `boxes.id` into the existing `TRACKS_FIELDS` / `tracks.csv` contract.
5. Write `tracks.csv` under the user-provided output directory.
6. Optionally call the renderer separately; do not render tracked video inside tracking by default.

Target CLI shape:

```bash
.venv/bin/python -m src.track_video \
  --video-source local_videos/source/pexels_crosswalk_traffic_demo.mp4 \
  --model local_weights/yolov8s_640_50epochs/best.pt \
  --output-dir /tmp/yolov8_track_video_bytetrack \
  --tracker bytetrack \
  --max-frames 300 \
  --video-id demo
```

## Dependency Decision

Ultralytics `bytetrack.yaml` requires `lap`. The project has verified `lap==0.5.13` locally, but it is not pinned in requirements yet.

Before productionizing, choose one path:

- A. document the local install step only
- B. add `lap` to requirements
- C. add optional extras for ByteTrack runtime dependencies

## Contract Helper

`src/tracking/bytetrack_runtime_contract.py` defines pure-Python planning helpers for the future runtime:

- `parse_frame_limit`
- `build_bytetrack_output_paths`
- `build_bytetrack_runtime_metadata`
- `summarize_track_rows`
- `validate_bytetrack_runtime_config`
- `build_track_video_bytetrack_plan`

The helper does not import Ultralytics, cv2, torch, or numpy. It does not create output directories and does not run inference or tracking.

## Test Strategy

- Use fake model/track objects in unit tests.
- Keep CI free of real YOLO, real video, GPU, and external tracker execution.
- Validate path construction, config validation, output summary fields, and future runtime plan objects.
- Keep real local smoke runs manual and write outputs to `/tmp`.

## Risk Controls

- No full-length run by default.
- No output CSV/MP4 commit.
- No source video or model weight commit.
- Use `/tmp` or ignored local output paths for manual smoke runs.
- Keep the synthetic tracker fallback until ByteTrack quality is reviewed.

## Recommended Next Version

`v0.11.4-track-video-bytetrack-runtime`

Minimum scope:

- implement `track_video.py --tracker bytetrack` short-video path
- require or default `max_frames=300`
- use fake tests only for automated coverage
- keep optional manual `/tmp` smoke validation separate from committed artifacts

## v0.11.4 Track Video ByteTrack Runtime

`v0.11.4` implements the formal `track_video.py --tracker bytetrack` runtime path.

Standard CLI:

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

Runtime behavior:

- requires `--video-source` and `--model`
- calls Ultralytics `model.track(..., tracker="bytetrack.yaml", stream=True, persist=True)`
- writes standard `tracks.csv` to the user-provided output directory
- keeps `max_frames=300` as the safe default
- does not render tracked video by default
- keeps synthetic tracker behavior unchanged

Local 300-frame standard CLI validation:

- output: `/tmp/yolov8_track_video_bytetrack/tracks.csv`
- tracks CSV lines: `747` including header
- `track_rows=746`
- `unique_tracks=25`
- `frames_with_rows=261`
- `class_counts`: `Person=720`, `Bus=26`

Still pending:

- `lap` requirements pin decision
- analytics rerun on ByteTrack tracks
- ByteTrack tracked video rendering through the standard pipeline
- synthetic vs ByteTrack comparison
- full-length validation
- Streamlit/FastAPI video workflow integration

## v0.11.5 ByteTrack Pipeline Validation

`v0.11.5` adds `src.validate_bytetrack_pipeline` to validate the standard
`track_video.py --tracker bytetrack` output with the existing analytics-only
rerun and tracked-video renderer.

Validation command:

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

Local result:

- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- analytics rerun succeeded with `track_row_count=746` and `track_count=25`
- ROI summary observed `33` frame/class rows
- event summary produced `24` long-stay events
- renderer wrote a readable 300-frame, `1280x720`, `29.97 FPS` preview

The validation does not rerun YOLO and does not rerun ByteTrack. Outputs remain
under `/tmp` and are not committed.

Still pending after v0.11.5:

- synthetic vs ByteTrack comparison
- full-length ByteTrack validation
- `lap` requirements pin decision
- Streamlit/FastAPI video workflow integration

## v0.11.6 Synthetic vs ByteTrack Comparison

`v0.11.6` adds `src.compare_tracking_outputs` and documents the comparison in
[Synthetic vs ByteTrack Tracking Comparison](tracking_comparison.md).

Local result:

- synthetic tracks: `21988` rows, `34` tracks
- ByteTrack tracks: `746` rows, `25` tracks, `261` frames with rows
- ByteTrack class counts: `Person=720`, `Bus=26`
- synthetic analytics: `count_total=61`, `roi_frames=1283`, `events=14`
- ByteTrack analytics: `roi_frames=33`, `long_stay_events=24`

Recommendation: use ByteTrack tracks for runtime/demo where real MOT matters,
while keeping synthetic tracks for deterministic tests and fallback. Full-length
ByteTrack validation and UI/API integration remain pending.
