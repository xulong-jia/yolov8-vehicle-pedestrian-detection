# Tracked Video Rendering

`v0.10.4` adds a tracked video renderer for local preview videos.

The renderer reads an existing source video and an existing `tracks.csv`, then draws tracked boxes and labels. It can also draw line and ROI overlays from a suggested analytics config or overlay plan.

It does not rerun YOLO, does not regenerate detections or tracks, does not integrate ByteTrack/DeepSORT, and does not prove MOT quality.

## Inputs

- source video
- existing `tracks.csv`
- optional suggested analytics config JSON
- optional overlay plan JSON

## Output

- tracked preview video, for example `/tmp/yolov8_real_smoke/tracked_preview_300.mp4`

Keep output videos under `/tmp` or another ignored local path. Do not commit generated preview videos.

## Command

```bash
.venv/bin/python -m src.render_tracked_video \
  --video /absolute/path/to/video.mp4 \
  --tracks-csv /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --output-video /tmp/yolov8_real_smoke/tracked_preview_300.mp4 \
  --config-json /tmp/yolov8_real_smoke/suggested_analytics_config.json \
  --max-frames 300
```

## Rendered Content

- bbox rectangle
- `track_id`
- `class_name`
- confidence when present
- line overlay
- ROI overlay

## Local Smoke Preview

A local 300-frame preview was rendered to `/tmp/yolov8_real_smoke/tracked_preview_300.mp4`.

Summary:

- `frames_written`: `300`
- `track_rows_loaded`: `21988`
- `unique_tracks`: `34`
- `frames_with_tracks`: `1678`
- `line_overlay_count`: `1`
- `roi_overlay_count`: `1`
- output size: `16M` (`16440663` bytes)

The generated video is local-only and is not committed.

## Limitations

- Current tracks may be synthetic.
- This is visualization, not proof of MOT quality.
- Not ByteTrack/DeepSORT yet.
- Output video is local-only and must not be committed.
- For long videos, use `--max-frames` first.

## Next Steps

- render full-length preview
- support tracked video from real ByteTrack
- add static thumbnail or frame extraction
- integrate with Streamlit/FastAPI later
