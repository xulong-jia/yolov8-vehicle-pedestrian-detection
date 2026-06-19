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
