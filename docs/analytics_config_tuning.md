# Analytics Config Tuning

`v0.10.1-real-smoke-analytics-config-tuning` adds an analytics config suggester for real smoke runs.

The helper reads an existing `tracks.csv` and summarizes bounding-box, center, and bottom-center coordinate distributions. It then suggests line, ROI, and event-rule settings that can be used as a starting point for tuning a real smoke video's analytics config.

It does not rerun YOLO, does not run a tracker, does not render tracked video, and does not validate visual geometry.

## Command

```bash
.venv/bin/python -m src.analytics_config_suggester \
  --tracks-csv /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --video-id demo \
  --output-json /tmp/yolov8_real_smoke/suggested_analytics_config.json
```

Keep generated JSON under `/tmp` or another ignored local path. Do not commit `suggested_analytics_config.json`, `tracks.csv`, real videos, model weights, or generated smoke outputs.

## Output Structure

The JSON output contains:

- `summary`: row count, track count, class counts, frame/time ranges, bbox coordinate ranges, center/bottom-center ranges, percentiles, and sample track counts.
- `suggested_config.lines`: a heuristic counting line based on bottom-center coordinate percentiles.
- `suggested_config.rois`: a heuristic ROI polygon based on bottom-center coordinate percentiles.
- `suggested_config.event_rules`: conservative long-stay, crowd-warning, and wrong-direction suggestions.
- `notes`: limitations and manual review reminders.

## Limitations

- Heuristic only.
- Does not validate visual geometry.
- Synthetic tracks do not represent real MOT quality.
- The suggested line and ROI should be manually checked against the video frame.
- Not ByteTrack/DeepSORT.
- Not tracked video rendering.

## Recommended Next Steps

- Inspect the suggested line and ROI against representative video frames.
- Pass a tuned config into the analytics job in a future step.
- Optionally add visualization overlay later.
- Keep all generated tuning outputs out of Git.

## Analytics-only Rerun With Suggested Config

`v0.10.2` adds `src.analytics_only_rerun` for applying a suggested analytics config to existing smoke artifacts. It reads existing `detections.csv`, `tracks.csv`, and config JSON, creates a fresh Video Analysis Center run, and only re-executes analytics.

It does not rerun YOLO, does not rerun a tracker, does not regenerate detections or tracks, and does not render tracked video.

Example:

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

Outputs:

- `metadata.json`
- copied `detections.csv`
- copied `tracks.csv`
- `count_events.csv`
- `roi_frame_counts.csv`
- `events.jsonl`
- `video_analysis_summary.json`

Keep rerun outputs under `/tmp` or another ignored local path. Do not commit generated CSV, JSON, or JSONL artifacts.
