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
