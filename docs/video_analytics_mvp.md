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
- after `v0.9.0`: integrate real ByteTrack/DeepSORT dependencies, then add Streamlit and FastAPI video analysis workflows.

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

- `v0.8.4`: connect `video_reader.py` to the `track_video.py` skeleton.
- Later: add YOLO frame inference.
- Later: add a ByteTrack/DeepSORT adapter.
- Later: connect Streamlit and FastAPI video workflows.

## v0.8.4 Video Reader + Track Video Skeleton Integration

`v0.8.4-video-reader-track-video-integration` connects `video_reader.py` to the `track_video.py` skeleton. The CLI now has a metadata-only video path through the existing skeleton while preserving the synthetic detections-to-tracks contract.

Current `track_video.py` modes:

1. synthetic `detections.csv` to `tracks.csv`
2. `--video-source --metadata-only` to `video_metadata.json` plus `frame_index.csv`

Metadata-only mode supports:

- `--video-source`
- `--metadata-only`
- `--sample-every-n`
- `--max-frames`

Metadata-only outputs:

- `video_metadata.json`
- `frame_index.csv`

Current boundaries:

- does not run YOLO
- does not integrate ByteTrack/DeepSORT
- does not read frames for inference
- does not generate annotated video or tracked video
- does not write to `local_outputs`, `results`, or `runs`

Tests use pytest `tmp_path` and keep generated files outside the repository tree.

Recommended next phases:

- `v0.8.5`: add lightweight synthetic CLI demo docs or sample command docs.
- `v0.9.0`: add CSV-first YOLO video detection export plus a tracker adapter interface skeleton.
- Later: connect Streamlit and FastAPI video workflows.

## v0.8.5 CLI Smoke Documentation

`v0.8.5-cli-smoke-docs` adds `docs/track_video_cli_usage.md`. It documents the current safe `track_video.py` skeleton CLI modes and gives smoke commands that write generated outputs to `/tmp` rather than the repository tree.

Documented modes:

- synthetic `detections.csv` to `tracks.csv`
- video metadata-only mode

This is a documentation-only step. It adds no new runtime code and still does not run YOLO, integrate ByteTrack/DeepSORT, or perform real video tracking.

## v0.9.0 Real Video Detection and Tracking Foundation

`v0.9.0-real-video-detection-tracking-foundation` adds the first real-video detection and tracking foundation pieces while keeping the runtime safe and testable. It introduces CSV-first video detection export and a tracking adapter interface skeleton without integrating real ByteTrack/DeepSORT dependencies or rendering tracked videos.

Detection foundation:

- `src/predict_video.py` defaults to writing `detections.csv`.
- YOLO is lazy-loaded so importing the module does not require `ultralytics`.
- Tests use monkeypatch/fake YOLO and do not require real model weights, GPU access, or real inference.
- The default path does not save annotated video.
- Annotated video output remains explicit opt-in behavior only.

`detections.csv` fields:

```text
video_id, frame_index, timestamp_sec, detection_id, class_id, class_name, confidence, xmin, ymin, xmax, ymax
```

Tracking adapter foundation:

- `BaseTrackerAdapter`
- `SyntheticTrackerAdapter`
- `ByteTrackAdapter` placeholder
- `DeepSORTAdapter` placeholder
- `create_tracker_adapter`
- `detections_to_tracker_input`
- `tracker_outputs_to_track_rows`

`SyntheticTrackerAdapter` validates the `detections.csv` to `tracks.csv` contract conversion with fake detections. `ByteTrackAdapter` and `DeepSORTAdapter` are placeholders only; their `update(...)` methods raise `NotImplementedError` because the real tracker dependencies are not integrated yet.

Still out of scope after v0.9.0:

- real ByteTrack dependency integration
- real DeepSORT dependency integration
- full `track_video.py` real runtime
- tracked video rendering
- Streamlit video pages
- FastAPI video jobs
- real video smoke demo

Recommended next phases:

- `v0.9.1`: connect `predict_video.py` CSV output to `track_video.py` synthetic tracker mode or the Video Analysis Center.
- `v1.0` candidate: integrate a real ByteTrack adapter and run a controlled real video smoke demo without committing generated artifacts.

## v0.9.1 Predict-to-Track Synthetic Runtime

`v0.9.1-predict-to-track-synthetic-runtime` connects the `track_video.py` `detections.csv` to `tracks.csv` path to the tracking adapter factory. The CLI still operates in a safe skeleton mode, but the synthetic tracking path now goes through the same adapter interface that future real trackers will use.

Current behavior:

- `track_video.py` obtains trackers with `create_tracker_adapter(tracker_name)`.
- The current successful runtime tracker is `synthetic`.
- The synthetic tracker writes `tracks.csv` from existing or synthetic `detections.csv` rows.
- `bytetrack` and `deepsort` are still placeholder adapters.
- Calling `update(...)` on `bytetrack` or `deepsort` raises `NotImplementedError`.
- Metadata-only video mode does not call the tracker adapter factory.

Still out of scope after v0.9.1:

- real ByteTrack dependency integration
- real DeepSORT dependency integration
- full real video tracking runtime
- tracked video rendering
- Streamlit video pages
- FastAPI video jobs
- real video smoke demo

Recommended next phases:

- `v0.9.2`: connect `predict_video.py` `detections.csv` output with `track_video.py` synthetic tracker in a documented two-command smoke flow.
- Later: integrate the real ByteTrack dependency behind the existing adapter interface.

## v0.9.2 Two-Command Smoke Flow

`v0.9.2-two-command-video-analysis-smoke-flow` documents and tests the current safe two-command predict-to-track path:

1. `predict_video.py` generates `detections.csv`.
2. `track_video.py` reads `detections.csv` and uses the synthetic tracker to generate `tracks.csv`.

The automated smoke test uses fake YOLO results and pytest `tmp_path`, so it does not load real model weights, read a real video, write repository outputs, or require GPU access.

Still pending after v0.9.2:

- real ByteTrack dependency integration
- real DeepSORT dependency integration
- tracked video rendering
- Video Analysis Center integration for real video jobs
- Streamlit video pages
- FastAPI video jobs
- real video smoke demo

## v0.9.3 Video Analysis Job Skeleton

`v0.9.3-video-analysis-job-skeleton` adds `src/services/video_analysis_job.py`. The module organizes existing `detections.csv` and `tracks.csv` artifacts into a `VideoAnalysisCenter` run directory.

The job skeleton copies these artifacts into the run directory:

- `detections.csv`
- `tracks.csv`

It writes:

- `metadata.json`
- `video_analysis_summary.json`

The summary includes:

- `detection_count`
- `track_row_count`
- `track_count`
- `artifact_paths`
- `count_summary`
- `roi_summary`
- `event_summary`
- `bad_case_links`

Current boundaries:

- does not run YOLO
- does not run tracker
- does not integrate real ByteTrack/DeepSORT dependencies
- does not generate tracked video
- does not connect Streamlit or FastAPI

Recommended next phases:

- `v0.9.4`: document a three-step local flow: `predict_video.py` to `track_video.py` synthetic tracker to `video_analysis_job`.
- Later: run analytics on real tracks.
- Later: integrate the real ByteTrack dependency.

## v0.9.4 Three-Step Video Analysis Job Flow

`v0.9.4-three-step-video-analysis-job-flow` documents and tests the current safe three-step chain:

1. `predict_video.py` generates `detections.csv`.
2. `track_video.py` with the synthetic tracker generates `tracks.csv`.
3. `video_analysis_job.py` organizes the CSV artifacts into a `VideoAnalysisCenter` run directory.

The run directory contains:

- `metadata.json`
- copied `detections.csv`
- copied `tracks.csv`
- `video_analysis_summary.json`

The flow verifies that `detections.csv` and `tracks.csv` are copied into the run directory and that `metadata.json` plus `video_analysis_summary.json` are written. Tests use fake YOLO and pytest `tmp_path`; they do not load real model weights, read real video, write repository outputs, or require GPU access. This phase does not integrate real ByteTrack/DeepSORT, does not generate tracked video, and does not connect Streamlit or FastAPI.

Still pending after v0.9.4:

- real ByteTrack dependency integration
- real DeepSORT dependency integration
- tracked video rendering
- analytics execution on real tracks
- Streamlit video pages
- FastAPI video jobs
- real video smoke demo

Recommended next phases:

- analytics execution on real tracks
- real ByteTrack dependency integration
- tracked video rendering
- real video smoke demo

## v0.9.5 Analytics on Tracks Job

`v0.9.5-analytics-on-tracks-job` extends `src/services/video_analysis_job.py` so `create_video_analysis_job_run(..., run_analytics=True, analytics_config=...)` can execute analytics from an existing `tracks.csv`.

Current supported outputs:

- line counter -> `count_events.csv`
- ROI counter -> `roi_frame_counts.csv`
- event rules -> `events.jsonl`
- updated `video_analysis_summary.json`

The summary now updates:

- `count_summary`
- `roi_summary`
- `event_summary`
- `artifact_paths`

The default `run_analytics=False` behavior remains compatible with the earlier job skeleton: it only organizes existing `detections.csv` and `tracks.csv` and writes metadata plus summary files.

Current boundaries:

- does not run YOLO
- does not run tracker
- does not integrate real ByteTrack/DeepSORT dependencies
- does not generate tracked video
- does not connect Streamlit or FastAPI

Recommended next phases:

- documented four-step local flow: `predict_video.py` -> `track_video.py` synthetic tracker -> `video_analysis_job` with analytics
- later: real ByteTrack dependency integration
- later: tracked video rendering
- later: real video smoke demo

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
- `tests/test_predict_video.py`
- `tests/test_tracking_adapters.py`
- `tests/test_predict_to_track_smoke_flow.py`
- `tests/test_video_analysis_job.py`
- `tests/test_three_step_video_analysis_job_flow.py`

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
