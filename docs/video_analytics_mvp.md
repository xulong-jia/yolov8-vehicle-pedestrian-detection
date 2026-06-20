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

## v0.9.6 Four-Step Local Flow

`v0.9.6-four-step-local-flow` documents and tests the current safe four-step chain:

1. `predict_video.py` exports `detections.csv`.
2. `track_video.py --tracker synthetic` exports `tracks.csv`.
3. `video_analysis_job.py` organizes the CSV artifacts into a `VideoAnalysisCenter` run directory.
4. `create_video_analysis_job_run(..., run_analytics=True, analytics_config=...)` executes line, ROI, and event analytics.

The flow verifies:

- `detections.csv`
- `tracks.csv`
- `count_events.csv`
- `roi_frame_counts.csv`
- `events.jsonl`
- `video_analysis_summary.json`

Tests use fake YOLO and pytest `tmp_path`; they do not load real weights, read real video, write repository outputs, or require GPU access. Real ByteTrack dependency integration, tracked video rendering, Streamlit video pages, FastAPI video jobs, and real video smoke demos remain pending.

## v0.9.7 Four-Step Smoke Runner

`v0.9.7-four-step-smoke-runner` adds `src/run_video_analysis_smoke.py`, a unified smoke runner for the current four-step local flow.

The runner:

- exports `detections.csv` through `predict_video.py`
- generates `tracks.csv` through `track_video.py` with the synthetic tracker
- creates a `VideoAnalysisCenter` job run
- calls `create_video_analysis_job_run(..., run_analytics=True, analytics_config=...)`
- writes outputs under the user-provided `--output-dir`

It may run YOLO through `predict_video.py` when used with real model weights and a real source video. It still uses the synthetic tracker, does not integrate real ByteTrack/DeepSORT, does not render tracked video, and does not connect Streamlit or FastAPI.

## v0.9.8 Real Local Smoke Preflight

`v0.9.8-real-local-smoke-preflight` adds `src/smoke_preflight.py`, a safe preflight checker for real local smoke runs.

The preflight checker validates:

- model path exists and is a file
- video path exists and is a file
- output directory path is safe without creating it
- optional `ultralytics` module availability
- optional `cv2` module availability

It prints command previews for the CSV detector, synthetic tracker, and unified smoke runner. It does not run YOLO, does not run tracking, does not create outputs, and does not write CSV/JSON artifacts. This prepares for a later actual real local smoke demo without committing generated files.

## v0.9.9 Real Local Smoke Run Result

`v0.9.9-real-local-smoke-result` documents the first real local smoke run result.

The run used the local YOLOv8s `best.pt` weight and the local `pexels_crosswalk_traffic_demo.mp4` video. Preflight completed with `ok=true`.

Observed result:

- `21988` detections
- `21988` synthetic track rows
- `34` synthetic tracks
- Video Analysis Center artifacts produced
- no line, ROI, or event trigger under the default smoke analytics config

The tracker is still synthetic. This is not real ByteTrack/DeepSORT tracking and does not produce tracked video rendering. Generated outputs stay local-only under `/tmp/yolov8_real_smoke` and are not committed.

The local result summary is retained here, in `docs/track_video_cli_usage.md`,
and in `docs/final_project_report.md`; the one-off result-history page has
been pruned.

## v0.10.0 CLI/Module Invocation Ergonomics

`v0.10.0-cli-module-invocation-ergonomics` standardizes module-style local invocation for smoke tools.

Recommended commands:

```bash
.venv/bin/python -m src.smoke_preflight ...
.venv/bin/python -m src.run_video_analysis_smoke ...
```

This avoids using the `PYTHONPATH=.` workaround as the primary path. The fallback remains available for direct script execution when needed. This step only documents and tests CLI/module invocation ergonomics; it does not integrate a real tracker, add ByteTrack/DeepSORT dependencies, or render tracked video.

## v0.10.1-v0.10.3 Analytics Tuning Lessons

The real smoke analytics work showed that line, ROI, and event-rule settings
must be reviewed against observed track geometry before counts are meaningful.
The one-off tuning and overlay helpers have been pruned from the mainline. The
retained guidance is to keep analytics config explicit, rerun analytics through
the Video Analysis Center when needed, and review geometry through tracked-video
and Streamlit outputs.

## v0.10.4 Tracked Video Rendering

`v0.10.4` adds `src/render_tracked_video.py`.

The renderer reads an existing source video and existing `tracks.csv`, then draws bbox rectangles, `track_id`, `class_name`, optional confidence labels, line overlays, and ROI overlays. It can use the suggested analytics config and overlay plan produced in earlier steps.

This step does not rerun YOLO, does not regenerate detections or tracks, does not change the tracker, does not integrate ByteTrack/DeepSORT, and does not prove MOT quality. Current tracks may still be synthetic.

Details: [Tracked Video Rendering](tracked_video_rendering.md)

## v0.11.0 ByteTrack Discovery Spike

`v0.11.0` adds `src/tracking/bytetrack_discovery.py` and [ByteTrack Integration Plan](bytetrack_integration_plan.md).

This is discovery only. It does not install new dependencies, does not run real ByteTrack, does not run real DeepSORT, does not run YOLO, and does not generate `detections.csv`, `tracks.csv`, JSON artifacts, or tracked videos.

The discovery helper defines how ByteTrack-like outputs, especially Ultralytics `model.track(..., tracker="bytetrack.yaml")` outputs, can be normalized into the existing `tracks.csv` contract. It uses duck typing and fake test objects so tests do not depend on Ultralytics, OpenCV, torch, numpy, model weights, or real videos.

Recommended next step:

- `v0.11.1`: run an explicitly approved short local Ultralytics `model.track` spike.
- Export real ByteTrack-like rows to `tracks.csv` under `/tmp`.
- Reuse the existing tracked video renderer for a short preview.
- Keep the synthetic tracker fallback until real ByteTrack track quality is reviewed.

## v0.11.1 Ultralytics ByteTrack Short Video Spike

`v0.11.1` adds `src/track_video_bytetrack_spike.py`.

The tool runs a max-frame-limited Ultralytics `model.track(..., tracker="bytetrack.yaml")` spike, normalizes track results into the existing `tracks.csv` contract, and can pass those tracks to the existing tracked video renderer. Outputs are local-only under `/tmp`.

This is not full production integration. It does not promote ByteTrack into `track_video.py`, does not replace the synthetic tracker fallback, does not connect Streamlit/FastAPI, and does not claim tracking quality.

Local attempt result:

- attempted with local YOLOv8s weights and local demo video
- blocked by missing `lap`
- no `bytetrack_tracks.csv` or tracked preview MP4 was produced
- next step requires resolving the Ultralytics ByteTrack runtime dependency before rerun

## v0.11.2 Successful ByteTrack Short-Video Spike

`v0.11.2` verifies the missing local runtime dependency and reruns the short Ultralytics ByteTrack spike successfully.

Local environment:

- `lap==0.5.13`
- `ultralytics==8.4.64`
- `cv2==4.13.0`
- requirements files unchanged; dependency pin decision pending

Successful local results:

- `frames_seen=300`
- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- real ByteTrack-style tracks exported locally to `/tmp/yolov8_bytetrack_spike/bytetrack_tracks.csv`
- tracked preview rendered locally to `/tmp/yolov8_bytetrack_spike/bytetrack_tracked_preview_300.mp4`
- preview is cv2 readable with `frame_count=300`, `fps=29.97`, `width=1280`, `height=720`

This proves that the Ultralytics ByteTrack dependency path can run locally and that the existing renderer can consume real ByteTrack tracks. It is still not full production integration: ByteTrack is not promoted into `track_video.py`, `lap` is not pinned in requirements, analytics has not been rerun on ByteTrack tracks, synthetic vs ByteTrack comparison is pending, and full-length validation remains pending.

## v0.11.3 ByteTrack Runtime Integration Plan

`v0.11.3` prepares the transition from the short-video ByteTrack spike to a formal `track_video.py --tracker bytetrack` runtime.

This step adds:

- runtime contract guidance folded into `docs/bytetrack_integration_plan.md`
- `src/tracking/bytetrack_runtime_contract.py`
- fake unit tests for config validation, output path planning, track-row summarization, and future runtime plan objects

No real YOLO or ByteTrack rerun is performed in this step. ByteTrack is still not promoted into the standard `track_video.py` runtime. The recommended next implementation version is `v0.11.4-track-video-bytetrack-runtime`.

## v0.11.4 Track Video ByteTrack Runtime

`v0.11.4` promotes the verified ByteTrack spike into the standard `track_video.py` CLI.

Supported command shape:

```bash
.venv/bin/python -m src.track_video \
  --video-source local_videos/source/pexels_crosswalk_traffic_demo.mp4 \
  --model local_weights/yolov8s_640_50epochs/best.pt \
  --output-dir /tmp/yolov8_track_video_bytetrack \
  --tracker bytetrack \
  --max-frames 300 \
  --video-id demo
```

The runtime exports real ByteTrack `tracks.csv` rows to the user output directory. The local 300-frame validation produced `track_rows=746`, `unique_tracks=25`, `frames_with_rows=261`, with `Person=720` and `Bus=26`.

This step does not add UI/API workflow, does not make full-length runs the default, does not rerun analytics on ByteTrack tracks, and does not commit generated outputs.

## v0.11.5-v0.11.6 ByteTrack Validation Conclusions

The retained conclusion from the pruned validation-history docs is that standard
`track_video.py --tracker bytetrack` output can enter the existing downstream
pipeline:

- analytics-only rerun can consume ByteTrack `tracks.csv`.
- tracked-video rendering can consume ByteTrack `tracks.csv`.
- the local 300-frame validation produced `746` track rows, `25` unique tracks,
  and `261` frames with tracks.
- class counts were `Person=720` and `Bus=26`.
- analytics rerun observed `33` ROI frames and `24` long-stay events.
- the preview was cv2-readable at `300` frames, `29.97 FPS`, `1280x720`.

The synthetic-vs-ByteTrack comparison conclusion is unchanged: ByteTrack should
be used for runtime/demo because it carries real MOT `track_id` semantics, while
synthetic tracking remains a deterministic test and fallback path. No MOTA/IDF1
claim is made because no ground-truth tracking labels are available.

`v0.12.2` prunes the one-off ByteTrack validation-history documents after
folding the useful results into the mainline documentation.

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
- `tests/test_analytics_only_rerun.py`
- `tests/test_render_tracked_video.py`
- `tests/test_bytetrack_discovery.py`
- `tests/test_track_video_bytetrack_spike.py`

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

## v0.11.5 ByteTrack Pipeline Validation

`v0.11.5` validates the post-tracking pipeline for standard ByteTrack output.
The new `src.validate_bytetrack_pipeline` helper consumes existing
`detections.csv` and `tracks.csv`, runs analytics-only rerun, and optionally
renders a tracked preview.

The helper does not rerun YOLO and does not rerun ByteTrack. It keeps generated
analytics artifacts and preview video under `/tmp`.

Local 300-frame validation result:

- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- `detection_count=21988`
- `track_count=25`
- ROI frames observed: `33`
- long-stay events: `24`
- preview readable by cv2: `300` frames, `29.97 FPS`, `1280x720`

The helper creates a local compatibility copy when ByteTrack rows have blank
`timestamp_sec` values so the existing long-stay analytics can run. The source
tracks file is not modified.

## v0.11.6 Synthetic vs ByteTrack Comparison

`v0.11.6` compares the earlier synthetic tracking output with standard
ByteTrack output.

Local summary:

- synthetic tracks: `21988` rows, `34` tracks
- ByteTrack tracks: `746` rows, `25` tracks, `261` frames with rows
- ByteTrack classes: `Person=720`, `Bus=26`
- synthetic analytics: `count_total=61`, `roi_frames=1283`, `events=14`
- ByteTrack analytics: `roi_frames=33`, `long_stay_events=24`

Interpretation:

- Synthetic tracks are useful for deterministic tests and fallback.
- ByteTrack tracks should be used for runtime/demo where real MOT semantics
  matter.
- No MOTA/IDF1 claim is made because no ground-truth tracking labels are
  available.

## v0.12.0 Streamlit Video Demo Page

`v0.12.0` adds a read-only Streamlit page for browsing existing local
ByteTrack, analytics, comparison, and tracked-preview artifacts.

Implemented artifacts:

- `src/services/video_demo_catalog.py`
- `tests/test_video_demo_catalog.py`
- `app/streamlit_video_demo.py`
- `docs/streamlit_video_demo.md`

The page can display:

- `video_analysis_summary.json` metrics
- `tracks.csv` summary and preview rows
- `count_events.csv` preview rows
- `roi_frame_counts.csv` preview rows
- `events.jsonl` preview rows
- tracked preview video playback when a local MP4 path is provided
- synthetic-vs-ByteTrack comparison JSON when provided

Safety boundary:

- does not run YOLO
- does not run ByteTrack
- does not run analytics
- does not render new videos
- does not copy `/tmp` artifacts into the repository
- tests use synthetic `tmp_path` artifacts only

Recommended next phases:

- full-length ByteTrack validation if a longer local run is needed
- FastAPI video job endpoint after the CLI workflow is stable
- Streamlit job-launch controls only after output policy and runtime safety are
  finalized

## v0.13.0 FastAPI Basic Service Acceptance

`v0.13.0` adds the execution-manual FastAPI basics:

- `GET /health`
- `GET /config`
- `GET /model-status`
- `POST /predict`

The API is ready for single-image service acceptance. `src.api` does not load
YOLO on import, and status/config endpoints do not load weights. `/predict`
uses the lazy `src/core/model_loader.py` path and
`src/services/image_inference_service.py` for in-memory image decoding and
inference.

Video analysis endpoints are planned later. `v0.13.0` does not add async video
jobs, result-query endpoints, database integration, Docker production
validation, or Streamlit job launching.

## v0.13.1 FastAPI Video Job Result Skeleton

`v0.13.1` adds a FastAPI skeleton for the execution-manual video job and result
query surface:

- `POST /api/videos/analyze`
- `GET /api/videos/jobs/{job_id}`
- `GET /api/videos/jobs/{job_id}/detections`
- `GET /api/videos/jobs/{job_id}/tracks`
- `GET /api/videos/jobs/{job_id}/analytics`
- `GET /api/videos/jobs/{job_id}/events`

The implementation is deliberately non-executing. `POST /api/videos/analyze`
creates an in-memory job record and can attach it to an existing
VideoAnalysisCenter run directory. Result endpoints read existing artifacts:

- `detections.csv`
- `tracks.csv`
- `count_events.csv`
- `roi_frame_counts.csv`
- `events.jsonl`
- `video_analysis_summary.json`

This step does not run YOLO, run ByteTrack/DeepSORT, execute analytics, render
tracked video, create local output directories, use a database, or start
background workers. Tests use FastAPI `TestClient` and synthetic pytest
`tmp_path` artifacts.

Next recommended FastAPI work:

- add real async job execution only after a runtime policy is defined
- add rules/ROI/bad-case/evaluation APIs
- add Docker/deployment validation after the API surface is stable
