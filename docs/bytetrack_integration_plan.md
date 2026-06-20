# ByteTrack Integration Plan

`v0.11.0` is a ByteTrack discovery spike. It is not a complete real tracker integration.

The goal is to identify the safest next path for real multi-object tracking, define how ByteTrack-like outputs can be normalized into the existing `tracks.csv` contract, and keep the current synthetic tracker fallback intact.

## Current State

- Synthetic tracker is available through `create_tracker_adapter("synthetic")`.
- Real YOLO video detection can export `detections.csv`.
- Video Analysis Center can organize detections, tracks, analytics, and summary artifacts.
- Analytics-only rerun, overlay planning, and tracked preview rendering are available from existing `tracks.csv`.
- ByteTrack and DeepSORT adapters are still placeholders.

## Candidate Path A: Ultralytics `model.track(..., tracker="bytetrack.yaml")`

Pros:

- Fastest path to a real ByteTrack smoke spike.
- Uses the existing Ultralytics dependency already needed for YOLO inference.
- May directly expose track IDs through `result.boxes.id`.

Cons:

- Couples detection and tracking in one runtime call.
- May bypass the existing `detections.csv -> adapter -> tracks.csv` contract.
- Needs a careful export wrapper so `model.track` output still lands in the stable `tracks.csv` schema.

## Candidate Path B: External ByteTrack Adapter

Pros:

- Fits the adapter architecture more directly.
- Can reuse existing `detections.csv` input.
- Keeps detector export and tracker execution separated.

Cons:

- Adds dependency and platform compatibility risk.
- Tracker input format and state management are more complex.
- Requires separate dependency approval and installation.

## Recommendation

Use Ultralytics `model.track(..., tracker="bytetrack.yaml")` for the next short local spike.

Recommended next step:

- Run only a short local video segment or max-frame-limited smoke run after explicit approval.
- Export real ByteTrack-like rows to `tracks.csv` under `/tmp`.
- Do not commit generated outputs.
- Reuse `src.render_tracked_video` to render a short preview from the generated real ByteTrack tracks.
- Compare synthetic and ByteTrack track summaries before claiming tracking quality.

Suggested next version:

- `v0.11.1-ultralytics-bytetrack-short-video-spike`
- or `v0.11.1-bytetrack-track-csv-export`

## tracks.csv Contract

The real tracker export must preserve the current `tracks.csv` contract:

```text
video_id
frame_index
timestamp_sec
track_id
class_id
class_name
confidence
xmin
ymin
xmax
ymax
center_x
center_y
box_width
box_height
box_area
state
tracker_name
```

For Ultralytics `model.track` results, the expected source fields are:

- `result.boxes.xyxy` -> bbox coordinates
- `result.boxes.id` -> `track_id`
- `result.boxes.cls` -> `class_id`
- `result.boxes.conf` -> `confidence`
- `result.names` -> `class_name`
- frame index from wrapper metadata or enumerate index
- timestamp from wrapper metadata or an empty value until FPS integration is wired

Rows without a `track_id` should be skipped for the real tracker export because downstream line, ROI, and event analytics rely on stable IDs.

## Discovery Helper

`src/tracking/bytetrack_discovery.py` provides pure-Python helper functions:

- optional module availability checks with `importlib.util.find_spec`
- candidate path discovery summary
- fake Ultralytics track result normalization into `tracks.csv` rows
- direct ByteTrack-like object normalization into `tracks.csv` rows
- row contract validation

The helper does not import Ultralytics, OpenCV, torch, numpy, ByteTrack, or DeepSORT.

## Risk Controls

- Do not commit model weights.
- Do not commit local videos.
- Do not commit generated CSV, JSON, JSONL, MP4, runs, or local outputs.
- Do not default output paths into the repository.
- Keep the synthetic tracker fallback until real ByteTrack quality is validated.
- Treat discovery output as contract validation only, not MOT quality proof.
- Real ByteTrack quality needs a later short-video smoke run and visual review.

## Deferred Work

- Ultralytics `model.track` short local spike.
- Real ByteTrack `tracks.csv` export.
- Real ByteTrack tracked preview rendering.
- Synthetic vs ByteTrack track summary comparison.
- Streamlit video playback.
- FastAPI video artifact and job endpoints.

## v0.11.1 Ultralytics ByteTrack Short Video Spike

`v0.11.1` adds `src/track_video_bytetrack_spike.py`, a short-video spike CLI for Ultralytics `model.track(..., tracker="bytetrack.yaml")`.

The tool:

- reads a local model path and local video path
- lazy-loads Ultralytics only when executed
- runs `model.track` with `stream=True`, `persist=True`, and a required `--max-frames` limit
- exports ByteTrack-style rows to `/tmp/.../bytetrack_tracks.csv`
- can optionally call `src.render_tracked_video` to create a short tracked preview
- does not modify the existing synthetic tracker path
- is not full production integration

Example:

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
  --render-preview
```

Local attempt result:

- attempted on local YOLOv8s weights and local demo video
- output directory: `/tmp/yolov8_bytetrack_spike`
- blocked before tracks export by missing dependency: `No module named 'lap'`
- generated output files: none
- no `bytetrack_tracks.csv` or preview MP4 is committed

Next fix:

- approve/install the missing ByteTrack runtime dependency required by Ultralytics, likely `lap`
- rerun the same short-video command under `/tmp`
- only after a successful short run, compare synthetic and ByteTrack track summaries

## v0.11.2 lap dependency verification and successful short spike

`v0.11.1` was blocked by the missing Ultralytics ByteTrack runtime dependency `lap`.
In `v0.11.2`, `lap==0.5.13` was installed into the local `.venv` and the 300-frame Ultralytics ByteTrack short-video spike succeeded.

This is a local dependency verification result, not a committed dependency pin. `requirements.txt`, `requirements-api.txt`, and `requirements-dev.txt` are unchanged. Generated outputs are local-only under `/tmp/yolov8_bytetrack_spike` and are not committed.

Successful local output summary:

- `frames_seen=300`
- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- preview video readable by OpenCV/cv2
- preview metadata: `frame_count=300`, `fps=29.97`, `width=1280`, `height=720`

Meaning:

- ByteTrack runtime dependency path is confirmed.
- Ultralytics `model.track(..., tracker="bytetrack.yaml")` can produce stable track IDs for this local video.
- The existing tracked video renderer can consume real ByteTrack `tracks.csv` output.

Limits:

- This remains a short-video spike, not full production integration.
- `lap` is not yet added to requirements.
- ByteTrack is not yet promoted into the stable `track_video.py` runtime path.
- Synthetic vs ByteTrack metrics comparison has not been done.
- Full-length ByteTrack validation has not been done.

Recommended next steps:

- Decide whether to add `lap` to requirements.
- Promote the ByteTrack spike into a stable track-video runtime path.
- Run analytics-only rerun on ByteTrack tracks.
- Render a longer or full-length ByteTrack preview.
- Compare synthetic and ByteTrack track summaries before claiming MOT quality.

## v0.11.3 Runtime Integration Plan and Contract Helper

`v0.11.3` adds `src/tracking/bytetrack_runtime_contract.py` and folds the
runtime integration contract into this retained ByteTrack integration plan.

This step does not run YOLO, does not rerun ByteTrack, does not render video, and does not promote ByteTrack into `track_video.py` yet. It captures the future `track_video.py --tracker bytetrack` runtime contract, path planning, config validation, and track-row summarization in a pure-Python helper with fake unit tests.

Recommended implementation step:

- `v0.11.4-track-video-bytetrack-runtime`
- add a short-video `track_video.py --tracker bytetrack` path
- keep `max_frames=300` as the safe default
- keep the synthetic tracker fallback
- keep generated outputs under `/tmp` and out of Git

## v0.11.4 Standard track_video ByteTrack Runtime

`v0.11.4` promotes the ByteTrack spike into the standard `track_video.py` CLI.
The runtime contract and command details are retained in this document.

The supported runtime command shape is now:

```bash
.venv/bin/python -m src.track_video \
  --video-source local_videos/source/pexels_crosswalk_traffic_demo.mp4 \
  --model local_weights/yolov8s_640_50epochs/best.pt \
  --output-dir /tmp/yolov8_track_video_bytetrack \
  --tracker bytetrack \
  --max-frames 300 \
  --video-id demo
```

Local validation produced standard `tracks.csv` output under `/tmp/yolov8_track_video_bytetrack` with `track_rows=746`, `unique_tracks=25`, `frames_with_rows=261`, and `class_counts` of `Person=720`, `Bus=26`. Generated outputs remain local-only and are not committed.

Still pending: `lap` requirements decision, analytics rerun on ByteTrack tracks, synthetic vs ByteTrack comparison, full-length validation, and UI/API integration.

## v0.11.5 ByteTrack Pipeline Validation

`v0.11.5` validates that the standard `track_video.py --tracker bytetrack`
`tracks.csv` can flow into analytics-only rerun and tracked-video rendering
without rerunning YOLO and without rerunning the tracker.

Local 300-frame result:

- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- analytics artifacts and a readable 300-frame preview were generated under `/tmp`

Still pending: synthetic vs ByteTrack comparison, full-length ByteTrack
validation, `lap` requirements decision, and UI/API integration.

The retained conclusion from the validation run is that standard
`track_video.py --tracker bytetrack` output can flow into analytics-only rerun
and tracked-video rendering without rerunning YOLO or ByteTrack. The local
analytics rerun reported `detection_count=21988`, `track_row_count=746`,
`track_count=25`, `33` ROI frames observed, and `24` long-stay events. The
preview was readable by cv2 with `300` frames, `29.97 FPS`, and `1280x720`.
Generated CSV, JSON, JSONL, and MP4 outputs stayed under `/tmp` and were not
committed.

The synthetic-vs-ByteTrack comparison conclusion is that ByteTrack should be
used for runtime/demo while synthetic tracking remains the deterministic test
and fallback path. No MOTA/IDF1 claim is made because ground-truth tracking
labels are not available.
