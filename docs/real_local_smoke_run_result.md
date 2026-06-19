# Real Local Smoke Run Result

This document records the first real local smoke run for the video analytics pipeline.
It is a local validation record only. Generated outputs remain under `/tmp` and are not committed to Git.

## Environment

- Python: `.venv/bin/python`
- ultralytics: `8.4.64`
- cv2: `4.13.0`

## Inputs

- Model: local YOLOv8s `best.pt`
  - `/Users/jiaxulong/Documents/yolov8-vehicle-pedestrian-detection/local_weights/yolov8s_640_50epochs/best.pt`
- Video: local `pexels_crosswalk_traffic_demo.mp4`
  - `/Users/jiaxulong/Documents/yolov8-vehicle-pedestrian-detection/local_videos/source/pexels_crosswalk_traffic_demo.mp4`
- Output directory:
  - `/tmp/yolov8_real_smoke`

## Preflight

Preflight completed with `ok=true`.

Checks passed:

- model path
- video path
- output directory path
- `ultralytics` availability
- `cv2` availability

## Run Command

The first real local run used `PYTHONPATH=.` as a workaround for script-path execution:

```bash
PYTHONPATH=. .venv/bin/python src/run_video_analysis_smoke.py \
  --model local_weights/yolov8s_640_50epochs/best.pt \
  --source local_videos/source/pexels_crosswalk_traffic_demo.mp4 \
  --output-dir /tmp/yolov8_real_smoke \
  --video-id demo \
  --run-name demo_run \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu
```

Directly running `.venv/bin/python src/run_video_analysis_smoke.py ...` may trigger:

```text
ModuleNotFoundError: No module named 'src'
```

For the current local command, add `PYTHONPATH=.`. A future step can improve this with a module entrypoint or package invocation.

## Invocation Note

The recommended local invocation style is now module-based:

```bash
.venv/bin/python -m src.smoke_preflight ...
.venv/bin/python -m src.run_video_analysis_smoke ...
```

Direct script execution can be affected by Python import path behavior. If `.venv/bin/python src/run_video_analysis_smoke.py ...` reports `ModuleNotFoundError: No module named 'src'`, use `.venv/bin/python -m src.run_video_analysis_smoke ...` first. The `PYTHONPATH=.` script form remains a fallback.

## Output Artifacts

The smoke run produced these local-only artifacts:

- `/tmp/yolov8_real_smoke/detections.csv`
- `/tmp/yolov8_real_smoke/tracking/tracks.csv`
- `/tmp/yolov8_real_smoke/video_analysis/demo_run/metadata.json`
- `/tmp/yolov8_real_smoke/video_analysis/demo_run/detections.csv`
- `/tmp/yolov8_real_smoke/video_analysis/demo_run/tracks.csv`
- `/tmp/yolov8_real_smoke/video_analysis/demo_run/count_events.csv`
- `/tmp/yolov8_real_smoke/video_analysis/demo_run/roi_frame_counts.csv`
- `/tmp/yolov8_real_smoke/video_analysis/demo_run/events.jsonl`
- `/tmp/yolov8_real_smoke/video_analysis/demo_run/video_analysis_summary.json`

Do not commit these generated CSV, JSON, or JSONL files.

## Result Summary

- `detection_count`: `21988`
- `track_row_count`: `21988`
- `track_count`: `34`
- `count_summary.total_count`: `0`
- `roi_summary.frames_observed`: `0`
- `event_summary.total_events`: `0`
- `detections.csv`: `21989` lines including header
- `tracks.csv`: `21989` lines including header
- `count_events.csv`: `1` line, header only
- `roi_frame_counts.csv`: `1` line, header only
- `events.jsonl`: `0` lines
- Output size: `13M`

## Interpretation

- Real YOLO detection export worked.
- The synthetic tracker converted detections to track rows.
- The Video Analysis Center job and artifacts were produced.
- The default smoke analytics config did not trigger line, ROI, or event counts.
- This validates the real local detection-to-analysis file pipeline, not real MOT quality.

## Limitations

- Tracker is synthetic.
- No ByteTrack/DeepSORT integration.
- No tracked video rendering.
- No Streamlit/FastAPI video workflow.
- Outputs are local-only and ignored or not committed.

## Next Steps

- Fix CLI/module invocation ergonomics or keep documenting the `PYTHONPATH=.` requirement.
- Optionally add a script entrypoint or `python -m src.run_video_analysis_smoke` workflow.
- Tune the smoke analytics config for a real video.
- Integrate real ByteTrack later.
- Add tracked video rendering later.

## v0.10.1 Follow-up

The first real smoke run produced analytics artifacts, but the default smoke analytics config did not trigger line, ROI, or event counts. `src.analytics_config_suggester` was added to suggest line, ROI, and event-rule settings from the existing `tracks.csv` coordinate distribution.

See [Analytics Config Tuning](analytics_config_tuning.md).

## v0.10.2 Analytics-only Rerun Follow-up

The default smoke config did not trigger counts. The v0.10.1 suggester produced a suggested line, ROI, and event-rule config from the existing `tracks.csv`. The v0.10.2 analytics-only rerun applies that config to existing `detections.csv` and `tracks.csv` without rerunning YOLO or the tracker.

Local-only rerun summary from `/tmp/yolov8_real_smoke_analytics_rerun`:

- `count_events.csv`: `62` lines including header
- `roi_frame_counts.csv`: `1347` lines including header
- `events.jsonl`: `14` lines
- `count_summary.total_count`: `61`
- `count_summary.by_direction`: `positive=31`, `negative=30`
- `roi_summary.frames_observed`: `1283`
- `roi_summary.max_count`: `27`
- `event_summary.total_events`: `14`
- `event_summary.by_type`: `long_stay=14`

These are statistics only. Generated CSV, JSON, and JSONL files remain local-only and are not committed.

## v0.10.3 Overlay Plan Follow-up

The overlay plan validates suggested line and ROI geometry before any renderer is added. It reads existing `tracks.csv` and `suggested_analytics_config.json`, infers coordinate ranges from bbox data, and reports line/ROI placement recommendations.

Local-only overlay plan summary from `/tmp/yolov8_real_smoke/analytics_overlay_plan.json`:

- `row_count`: `21988`
- `track_count`: `34`
- `class_counts`: `Bus=588`, `Motorcycle=4`, `Person=21396`
- `inferred_frame_bounds`: `width_hint=1280`, `height_hint=720`
- line `line_main`: `recommendation=ok`, `orientation=horizontal`, `within_bbox_bounds=true`, `within_bottom_bounds=true`
- ROI `roi_main`: `recommendation=ok`, `within_bbox_bounds=true`, `covers_center_distribution=true`, `covers_bottom_distribution=true`

This is a JSON plan only. It does not render video, does not validate true video frame metadata, and the generated `/tmp` JSON is not committed.

## v0.10.4 Tracked Preview Follow-up

The tracked video renderer produced a local 300-frame preview from the existing source video and existing `tracks.csv`. It did not rerun YOLO, did not regenerate detections or tracks, and did not use ByteTrack/DeepSORT.

Local-only preview:

- output path: `/tmp/yolov8_real_smoke/tracked_preview_300.mp4`
- `frames_written`: `300`
- `track_rows_loaded`: `21988`
- `unique_tracks`: `34`
- `frames_with_tracks`: `1678`
- `line_overlay_count`: `1`
- `roi_overlay_count`: `1`
- output size: `16M` (`16440663` bytes)

The output video is local-only and is not committed.

## v0.11.1 ByteTrack Short Spike Follow-up

`src.track_video_bytetrack_spike` was added to run a max-frame-limited Ultralytics `model.track(..., tracker="bytetrack.yaml")` spike and export ByteTrack-style `tracks.csv` under `/tmp`.

Local attempt:

- model: local YOLOv8s `best.pt`
- video: local `pexels_crosswalk_traffic_demo.mp4`
- output dir: `/tmp/yolov8_bytetrack_spike`
- max frames: `300`
- requested preview: enabled

Result:

- blocked before tracks export by missing dependency: `No module named 'lap'`
- generated output files: none
- no `bytetrack_tracks.csv` was produced
- no ByteTrack tracked preview MP4 was produced

This does not change the earlier synthetic-tracker smoke result. The next step is to resolve the missing Ultralytics ByteTrack runtime dependency before rerunning the short spike.
