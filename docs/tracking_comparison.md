# Synthetic vs ByteTrack Tracking Comparison

`v0.11.6` compares synthetic tracks with real ByteTrack tracks for the same
local demo video. The goal is to explain the difference between deterministic
CSV-contract tracking and real multi-object tracking output before building
Streamlit/FastAPI demo surfaces.

Synthetic tracks remain useful for deterministic tests, fallback behavior, and
contract validation. ByteTrack tracks should be used for runtime/demo when real
MOT semantics matter.

## Command

```bash
.venv/bin/python -m src.compare_tracking_outputs \
  --synthetic-tracks /tmp/yolov8_real_smoke/tracking/tracks.csv \
  --bytetrack-tracks /tmp/yolov8_track_video_bytetrack/tracks.csv \
  --synthetic-summary /tmp/yolov8_real_smoke_analytics_rerun/suggested_config_rerun/video_analysis_summary.json \
  --bytetrack-summary /tmp/yolov8_bytetrack_pipeline_validation/analytics/bytetrack_validation/video_analysis_summary.json \
  --video-id demo \
  --output-json /tmp/yolov8_tracking_comparison.json
```

The tool reads existing CSV/JSON artifacts only. It does not run YOLO, does not
run ByteTrack, and does not render video. Do not commit `/tmp` comparison JSON
or source CSV files.

## Local Comparison Summary

Synthetic tracking summary:

- rows: `21988`
- tracks: `34`
- frames with rows: `1678`
- classes: `Person=21396`, `Bus=588`, `Motorcycle=4`

ByteTrack summary:

- rows: `746`
- tracks: `25`
- frames with rows: `261`
- classes: `Person=720`, `Bus=26`

Comparison:

- row delta: `-21242`
- ByteTrack-to-synthetic row ratio: `0.0339`
- unique track delta: `-9`
- frame coverage delta: `-1417`

Analytics comparison:

- synthetic analytics: `count_total=61`, `roi_frames=1283`, `events=14`
- ByteTrack analytics: `count_total=0`, `roi_frames=33`, `long_stay_events=24`

## Interpretation

- Synthetic tracks inflated row count because they follow detection rows.
- ByteTrack tracks are lower-volume but have real tracker-confirmed `track_id`
  semantics.
- Lower ByteTrack row count does not imply worse tracking; it reflects
  tracker-confirmed IDs and missed or unmatched frames.
- Analytics outputs differ because temporal continuity and track confirmation
  differ.
- Use ByteTrack for runtime/demo where real MOT matters.
- Keep synthetic tracking for deterministic tests, fallback behavior, and CSV
  contract validation.

## Limitations

- Only 300-frame local validation.
- No full-length comparison yet.
- No quantitative MOT metrics such as MOTA or IDF1.
- No manual visual scoring yet.
- No Streamlit/FastAPI UI comparison yet.

## Next Steps

- Run full-length ByteTrack validation.
- Add a Streamlit video demo page using ByteTrack outputs.
- Optionally create a synthetic-vs-ByteTrack visual side-by-side.
- Consider MOTA/IDF1 only if ground-truth tracking labels become available.
