# track_video.py CLI Usage

`src/track_video.py` is currently a skeleton CLI for validating video analytics contracts.

Current boundaries:

- does not run YOLO
- does not read frames for detection inference
- does not integrate ByteTrack/DeepSORT
- does not generate tracked video

Current safe modes:

1. synthetic `detections.csv` to `tracks.csv`
2. video metadata-only mode

## Synthetic detections-to-tracks mode

Use this mode to validate field conversion from `detections.csv` to `tracks.csv`.

Input:

- existing or synthetic `detections.csv`

Output:

- `tracks.csv`

This mode does not read real video.

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
- ByteTrack/DeepSORT adapter
- tracked video rendering
- Video Analysis Center integration for real video jobs
- Streamlit video pages
- FastAPI video jobs
- real video smoke demo
