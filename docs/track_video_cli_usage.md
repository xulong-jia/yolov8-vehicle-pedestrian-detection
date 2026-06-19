# track_video.py CLI Usage

`src/track_video.py` is currently a skeleton CLI for validating video analytics contracts.

Current boundaries:

- does not run YOLO
- does not read frames for detection inference
- does not integrate ByteTrack/DeepSORT
- does not generate tracked video

Current safe modes:

1. synthetic `detections.csv` to `tracks.csv` through the tracker adapter factory
2. video metadata-only mode

## Synthetic detections-to-tracks mode

Use this mode to validate field conversion from `detections.csv` to `tracks.csv`.
Internally, `track_video.py` now obtains the tracker with `create_tracker_adapter(tracker_name)`.
The default tracker is `synthetic`.

Input:

- existing or synthetic `detections.csv`

Output:

- `tracks.csv`

This mode does not read real video.
It does not run YOLO and does not generate tracked video.

Smoke command:

```bash
cat > /tmp/synthetic_detections.csv <<'CSV'
video_id,frame_index,timestamp_sec,detection_id,class_id,class_name,confidence,xmin,ymin,xmax,ymax
demo,0,0.0,1,1,Car,0.91,0,0,10,20
demo,1,0.2,1,1,Car,0.89,1,0,11,20
CSV

python3 src/track_video.py \
  --detections-csv /tmp/synthetic_detections.csv \
  --output-dir /tmp/yolov8_track_video_skeleton \
  --tracker synthetic

ls -lh /tmp/yolov8_track_video_skeleton/tracks.csv
cat /tmp/yolov8_track_video_skeleton/tracks.csv
```

Expected output:

- `tracks.csv` exists
- `track_id` is stable from `detection_id`
- `center_x`, `center_y`, `box_width`, `box_height`, and `box_area` are populated
- `state` is `confirmed`
- `tracker_name` is `synthetic`

`--tracker bytetrack` and `--tracker deepsort` are recognized only as placeholder adapter names at this stage. They currently fail with `NotImplementedError` because the real ByteTrack/DeepSORT dependencies have not been integrated. Do not use them as successful smoke commands yet.

## Two-command smoke flow

Use this flow to connect the current CSV-first detector output to the safe synthetic tracker path. Keep generated files under `/tmp` and do not commit them.

Step 1: generate `detections.csv` with `predict_video.py`.

```bash
python3 src/predict_video.py \
  --model /absolute/path/to/best.pt \
  --source /absolute/path/to/video.mp4 \
  --output-csv /tmp/yolov8_video_smoke/detections.csv \
  --conf 0.25 \
  --imgsz 640 \
  --device cpu \
  --video-id demo
```

Step 2: convert `detections.csv` to `tracks.csv` with the synthetic tracker.

```bash
python3 src/track_video.py \
  --detections-csv /tmp/yolov8_video_smoke/detections.csv \
  --output-dir /tmp/yolov8_video_smoke/tracking \
  --tracker synthetic
```

Expected files:

- `/tmp/yolov8_video_smoke/detections.csv`
- `/tmp/yolov8_video_smoke/tracking/tracks.csv`

Step 1 runs YOLO if you provide a real model and real video. The automated test for this flow uses fake YOLO and `tmp_path` instead. Step 2 still uses the synthetic tracker and is not real ByteTrack/DeepSORT tracking. Keep model weights and videos local, write smoke outputs to `/tmp`, and do not commit `/tmp` outputs, generated `detections.csv`, generated `tracks.csv`, real videos, or model weights.

## Video metadata-only mode

Use this mode to validate video path reading, metadata extraction, and `frame_index.csv` creation.

This mode does not run detection, does not run tracking, and does not save frame images.

Smoke command:

```bash
VIDEO_PATH="/absolute/path/to/demo.mp4"

python3 src/track_video.py \
  --video-source "$VIDEO_PATH" \
  --output-dir /tmp/yolov8_video_metadata_only \
  --metadata-only \
  --sample-every-n 5 \
  --max-frames 20

ls -lh /tmp/yolov8_video_metadata_only/video_metadata.json
ls -lh /tmp/yolov8_video_metadata_only/frame_index.csv
cat /tmp/yolov8_video_metadata_only/video_metadata.json
head /tmp/yolov8_video_metadata_only/frame_index.csv
```

Expected output:

- `video_metadata.json` contains `fps`, `width`, `height`, `frame_count`, and `duration_sec`
- `frame_index.csv` contains sampled `frame_index` and `timestamp_sec`
- no frames, images, or videos are saved

## Recommended output policy

- For smoke commands, use `/tmp` or another external temp directory.
- Do not write generated outputs into Git-tracked `docs`, `src`, or `tests` directories.
- Do not commit `tracks.csv`, `frame_index.csv`, or `video_metadata.json` unless they are tiny intentional documentation examples.
- Do not commit real videos, model weights, runs, `local_outputs`, dataset splits, or zip files.

## Next planned runtime steps

Pending runtime work:

- real YOLO frame inference
- real ByteTrack/DeepSORT dependency integration
- tracked video rendering
- Video Analysis Center integration for real video jobs
- Streamlit video pages
- FastAPI video jobs
- real video smoke demo
