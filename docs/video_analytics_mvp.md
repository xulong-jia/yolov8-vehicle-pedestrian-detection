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
- Streamlit video pages
- FastAPI async video jobs
- React frontend
- database integration
- real video benchmark

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
- Future geometry / line / ROI / event tests can be written against contracts.
- No generated artifacts are committed.
- `make check`, `make api-check`, and `make danger-check` pass.
