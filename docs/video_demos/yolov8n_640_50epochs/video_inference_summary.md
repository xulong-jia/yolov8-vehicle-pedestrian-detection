# YOLOv8n 640x640 50 Epoch Video Inference Summary

## Demo Status

Video inference was run on Google Colab GPU and the result was downloaded as a zip archive.

## Model

- Model: YOLOv8n 640x640 50 epoch baseline
- Model weights: `local_weights/yolov8n_640_50epochs/best.pt`
- Inference environment: Google Colab GPU
- Inference parameters: `imgsz=640`, `conf=0.25`, `device=0`

## Input Video

- Input video: `pexels_crosswalk_traffic_demo.mp4`
- Source platform: Pexels
- Source metadata: `local_videos/README.video_sources.md`
- Original video GitHub policy: do not commit the original video by default
- Input duration: 57.057 seconds
- Input resolution: 1280x720
- Input FPS: 29.97
- Input file size: 50.97 MB

## Colab Output

- Colab result path: `runs/detect/runs/video_demos/yolov8n_640_50epochs_pexels_crosswalk`
- Downloaded zip: `~/Desktop/yolov8n_640_50epochs_pexels_video_demo.zip`
- Extracted output video: `docs/video_demos/yolov8n_640_50epochs/pexels_crosswalk_traffic_demo.avi`
- Output video size: 404,163,426 bytes (385 MB / 404.16 MB decimal)
- Output video metadata from local OpenCV read: 1280x720, 29 FPS, 1710 frames, about 58.97 seconds

The `.avi` output is large and is ignored by `.gitignore`, so it should be kept locally unless a smaller compressed version is created and explicitly approved for GitHub.

## Key Frames

Representative frames were extracted for lightweight documentation:

- `docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_start.jpg`
- `docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_middle.jpg`
- `docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_end.jpg`

## Notes

- This video demo is a qualitative visual demonstration only.
- It does not represent full test-set Precision, Recall, mAP50, or mAP50-95.
- Because the output is a large `.avi`, converting it to `.mp4` is recommended before considering any video upload or GitHub inclusion.
- Until conversion and file size are reviewed, submit the summary and key-frame screenshots, and keep the video file local.
