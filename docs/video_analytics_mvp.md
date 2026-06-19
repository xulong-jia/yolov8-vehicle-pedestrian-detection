# Video Analytics MVP

## Purpose

`v0.8.0-video-analytics-mvp` moves the project from a detection model engineering workflow toward a video analytics system. This phase starts with configuration, data contracts, and testable core logic contracts before adding real video runtime integration.

The MVP core should not depend on GPU access or real videos. Geometry, line counting, ROI counting, event rules, and summary output should be designed so they can be tested first with synthetic rows and toy tracks.

## Scope

Included in this MVP:

- Multi-object tracking contract
- Line crossing count contract
- ROI count contract
- Event rule contract
- Video Analysis Center output contract
- Synthetic unit tests first

Not included in this MVP:

- real ByteTrack/DeepSORT adapter integration
- track_video.py integration
- Streamlit video pages
- FastAPI async video jobs
- React frontend
- database integration
- real video benchmark

## Implemented in v0.8.0

`v0.8.0-video-analytics-mvp` completes the pure-Python video analytics MVP core. It adds contracts, deterministic analytics utilities, result writers, a result-directory skeleton, and synthetic unit tests without requiring GPU access, model weights, or real videos.

Implemented artifacts:

- `configs/tracking.yaml`
- `configs/analytics.yaml`
- geometry utilities in `src/analytics/geometry.py`
- line counter in `src/analytics/line_counter.py`
- ROI counter in `src/analytics/roi_counter.py`
- event rules in `src/analytics/event_rules.py`
- track and analytics artifact writers in `src/tracking/track_writer.py`
- Video Analysis Center skeleton in `src/services/video_analysis_center.py`
- synthetic unit tests for geometry, line counting, ROI counting, event rules, result writers, and Video Analysis Center behavior

Core implementation constraints:

- pure Python only for the v0.8.0 analytics core
- no `cv2`, `numpy`, `torch`, or `ultralytics` dependency in the core analytics modules
- no real tracker adapter
- no video decoding or model inference runtime
- no generated run outputs committed

Still out of scope for v0.8.0:

- real ByteTrack/DeepSORT adapter integration
- `track_video.py` integration
- Streamlit video result pages
- FastAPI video job endpoints
- React frontend
- database integration
- real video benchmark

Recommended next phases:

- after `v0.8.2`: add real video reading and YOLO frame inference skeletons before tracker adapter integration.
- `v0.9.0`: add real ByteTrack/DeepSORT integration plus Streamlit and FastAPI video analysis workflows.

## v0.8.1 Synthetic Pipeline

`v0.8.1-video-analysis-synthetic-pipeline` adds a synthetic end-to-end video analysis pipeline. It validates that synthetic tracks can flow through counting, ROI analysis, event rules, result writers, and the Video Analysis Center without running a detector or reading real video.

Pipeline scope:

- starts from synthetic tracks, not detector outputs
- sets `detection_count` to `0` because no detector is run
- uses `VideoAnalysisCenter` for run directory and artifact writing
- runs the line counter
- runs the ROI counter
- runs event rules
- writes result artifacts through the existing result writers

The pipeline is tested with pytest `tmp_path` and does not write to `local_outputs`, `results`, or `runs`.

Generated and validated artifacts:

- `metadata.json`
- `tracks.csv`
- `count_events.csv`
- `roi_frame_counts.csv`
- `events.jsonl`
- `video_analysis_summary.json`

Still out of scope after v0.8.1:

- real `track_video.py`
- ByteTrack/DeepSORT adapter
- real video inference
- Streamlit video pages
- FastAPI video jobs
- React frontend
- database integration
- real video benchmark

## v0.8.2 Track Video Skeleton

`v0.8.2-track-video-skeleton` adds `src/track_video.py` as a skeleton CLI for synthetic `detections.csv` to `tracks.csv` conversion. It validates the command-line entry point and tracking output contract before real video runtime integration.

Current CLI scope:

- supports synthetic `detections.csv` to `tracks.csv` conversion only
- verifies `tracks.csv` fields against the v0.8.0 tracking contract
- does not run YOLO
- does not read real video
- does not integrate ByteTrack/DeepSORT
- does not generate a real tracked video

The CLI writes `tracks.csv` with fields matching the v0.8.0 `tracks.csv` contract. Tests use pytest `tmp_path` and do not write to `local_outputs`, `results`, or `runs`.

Recommended next phases:

- `v0.8.3`: add a real video reading metadata skeleton.
- After that: integrate a ByteTrack/DeepSORT adapter.
- Then: connect Streamlit and FastAPI video workflows.

## v0.8.3 Real Video Reading Skeleton

`v0.8.3-real-video-reading-skeleton` adds `src/video_reader.py` as a safe video reading metadata layer. The module only validates video paths, reads video metadata, and builds frame-index rows before any YOLO inference or tracker integration.

Readable metadata:

- `fps`
- `width`
- `height`
- `frame_count`
- `duration_sec`
- `filename`
- `video_path`

Writable artifacts:

- `video_metadata.json`
- `frame_index.csv`

Current boundaries:

- does not run YOLO
- does not integrate ByteTrack/DeepSORT
- does not save frame images
- does not generate annotated video
- does not create a real `track_video.py` runtime

OpenCV / `cv2` is imported lazily. If `cv2` is unavailable in the test environment, the tiny video metadata test is skipped instead of failing. Tests use pytest `tmp_path` and do not write to `local_outputs`, `results`, or `runs`.

Recommended next phases:

- `v0.8.4` or `v0.9.0`: connect `video_reader.py` to the `track_video.py` skeleton.
- Later: add YOLO frame inference.
- Later: add a ByteTrack/DeepSORT adapter.
- Later: connect Streamlit and FastAPI video workflows.

## Test Summary

The MVP is covered by synthetic unit tests:

- `tests/test_geometry.py`
- `tests/test_line_counter.py`
- `tests/test_roi_counter.py`
- `tests/test_event_rules.py`
- `tests/test_track_writer.py`
- `tests/test_video_analysis_center.py`
- `tests/test_synthetic_video_analysis_pipeline.py`
- `tests/test_track_video.py`
- `tests/test_video_reader.py`

## Current Baseline

`v0.7.0-yolov8m-experiment` completed the model experiment line needed before the video analytics phase:

- YOLOv8s recommended default
- YOLOv8m experiment completed
- detection model family comparison completed

## Configuration Files

- `configs/tracking.yaml` defines the future tracker defaults, supported tracker types, track output filenames, and `tracks.csv` fields. No tracker adapter is implemented in Step 1.
- `configs/analytics.yaml` defines class groups, geometry settings, a default counting line, a default ROI, event rule defaults, and analytics artifact names. No analytics runtime is implemented in Step 1.

## Data Contracts

### detections.csv

Fields:

```text
video_id, frame_index, timestamp_sec, detection_id, class_id, class_name, confidence, xmin, ymin, xmax, ymax
```

Purpose:

- Stores frame-level detection rows before tracking.
- Keeps bounding boxes as pixel coordinates.
- Provides stable input for future tracker adapters.

### tracks.csv

Fields:

```text
video_id, frame_index, timestamp_sec, track_id, class_id, class_name, confidence, xmin, ymin, xmax, ymax, center_x, center_y, box_width, box_height, box_area, state, tracker_name
```

Purpose:

- Stores object tracks after multi-object tracking.
- Provides stable input for line counting, ROI counting, event rules, and summary generation.
- Keeps `tracker_name` and `state` explicit so downstream modules can filter confirmed tracks.

### count_events.csv

Fields:

```text
video_id, line_id, frame_index, timestamp_sec, track_id, class_id, class_name, direction, center_x, center_y
```

Purpose:

- Stores one row per accepted crossing event.
- Uses `line_id + track_id + direction` as the core deduplication key.
- Supports downstream count summaries by line, class, direction, and time window.

### roi_frame_counts.csv

Fields:

```text
video_id, frame_index, timestamp_sec, roi_id, roi_name, class_name, object_count, unique_track_count
```

Purpose:

- Stores per-frame ROI occupancy.
- Supports class-level ROI counts and unique track counts.
- Uses configured pixel-coordinate polygons from `configs/analytics.yaml`.

### events.jsonl

Fields:

```text
event_id, event_type, video_id, frame_index, timestamp_sec, track_id, class_name, roi_id, line_id, severity, evidence
```

Purpose:

- Stores one JSON object per event rule result.
- Requires each event to include evidence that explains the trigger.
- Keeps `roi_id` and `line_id` nullable so one schema can cover ROI-based and line-based events.

### video_analysis_summary.json

Fields:

```text
video_id, run_name, created_at, input_video, config_paths, artifact_paths, detection_count, track_count, count_summary, roi_summary, event_summary, bad_case_links
```

Purpose:

- Summarizes a complete video analysis run for future UI and API readers.
- Records artifact paths without embedding large outputs.
- Provides the Video Analysis Center contract for Streamlit, FastAPI, and later frontend work.

## Implementation Plan

1. configs + contracts
2. geometry TDD
3. line counter TDD
4. ROI counter TDD
5. event rules TDD
6. track writer + Video Analysis Center skeleton
7. docs + task board
8. tag v0.8.0-video-analytics-mvp

## Risk Controls

- no weights committed
- no local videos committed
- no runs committed
- no local_outputs committed
- no dataset split committed
- synthetic test data only
- GPU not required for v0.8.0 core logic

## Acceptance Criteria

- `configs/tracking.yaml` exists.
- `configs/analytics.yaml` exists.
- Data contracts are documented for detection, tracking, counting, ROI, events, and video analysis summaries.
- Geometry / line / ROI / event / writer / Video Analysis Center tests are implemented with synthetic inputs.
- No generated artifacts are committed.
- `make check`, `make api-check`, and `make danger-check` pass.
