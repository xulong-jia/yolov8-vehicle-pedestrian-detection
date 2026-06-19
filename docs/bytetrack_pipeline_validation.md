# ByteTrack Pipeline Validation

`v0.11.5` validates that the standard `track_video.py --tracker bytetrack`
output can be consumed by the existing analytics-only rerun and tracked-video
renderer.

This validation does not rerun YOLO and does not rerun the tracker. It starts
from already generated local artifacts:

- `detections.csv` from the previous real YOLO smoke run
- `tracks.csv` from the standard `track_video.py --tracker bytetrack` runtime
- suggested analytics config from the real smoke analytics tuning helper
- source video only for rendering the preview

## Tool

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

Outputs are local-only and must not be committed:

- analytics artifacts under `/tmp/yolov8_bytetrack_pipeline_validation/analytics/`
- compatibility copy `/tmp/yolov8_bytetrack_pipeline_validation/bytetrack_tracks_for_analytics.csv`
- preview video `/tmp/yolov8_bytetrack_pipeline_validation/bytetrack_tracked_preview_300.mp4`

The compatibility copy only fills missing `timestamp_sec` values from
`frame_index` so the existing long-stay analytics rule can run. The original
ByteTrack `tracks.csv` is not modified.

## Local Validation Result

The local v0.11.5 validation succeeded.

Tracks summary:

- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`

Analytics summary:

- `detection_count=21988`
- `track_row_count=746`
- `track_count=25`
- line count total: `0`
- ROI frames observed: `33`
- ROI max count: `1`
- event total: `24`
- event type: `long_stay=24`

Preview summary:

- preview opened by cv2: `True`
- preview frames: `300`
- preview FPS: `29.97`
- preview size: `1280x720`
- first frame readable: `True`
- preview file size: about `15M`
- output directory size: about `18M`

## Limits

- Still a 300-frame validation, not full-length validation.
- No Streamlit or FastAPI integration.
- No synthetic-vs-ByteTrack quality comparison yet.
- Analytics config is still heuristic and should be reviewed visually before
  claiming production counting accuracy.
