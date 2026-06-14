# Model Card

## Model Overview

- Model name: YOLOv8n 640x640 50-epoch baseline
- Framework: Ultralytics YOLOv8
- Task: Vehicle and pedestrian object detection
- Classes: `Bus`, `Car`, `Motorcycle`, `Person`, `Truck`, `mini-truck`

## Intended Use

This model is intended for:

- educational computer vision project work
- local image and video object detection demos
- traffic-scene qualitative inspection
- the local Streamlit demo
- error analysis and experiment comparison

## Out-of-Scope Use

This model is not intended for:

- safety-critical autonomous driving
- law enforcement use
- production monitoring without further validation
- medical, legal, or safety-critical decisions

## Training Setup

- Base model: `yolov8n.pt`
- Image size: `640`
- Epochs: `50`
- Platform: Google Colab GPU
- Dataset config: `dataset/data.yaml`
- Expected local weight path: `local_weights/yolov8n_640_50epochs/best.pt`

## Evaluation Summary

YOLOv8n official test split metrics:

| Split | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| test | 396 | 1642 | 0.841 | 0.816 | 0.859 | 0.582 |

These metrics were produced from the official test split.

The corresponding summary directory is not currently tracked in the repository and may need to be restored or recreated. The metric values are recorded in `docs/experiment_comparison.md` and `docs/experiment_comparison.csv`.

## Per-Class Notes

- `Motorcycle` and `Person` performed strongly in the available analysis materials.
- `mini-truck` was the most challenging class.
- `Car` / `Truck` / `mini-truck` visual similarity is a known source of confusion.
- Per-class YOLOv8n official test metrics are not currently available in a tracked summary file, so they are not listed here.

## Known Limitations

- Small objects can be difficult to detect reliably.
- Crowded scenes can increase missed detections and duplicate-box candidates.
- False positives and false negatives are present in qualitative analysis examples.
- Duplicate boxes can appear in dense scenes.
- `Car` / `Truck` / `mini-truck` confusion is a recurring qualitative issue.
- Performance is dataset-specific.
- There is no guarantee of generalization to unseen traffic domains.

## Error Analysis and Demo Links

- Error case gallery: `docs/error_case_gallery/README.md`
- 10-sample image inference: `docs/predictions/yolov8n_640_50epochs/`
- 50-sample image inference: `docs/predictions/yolov8n_640_50epochs_50samples/`
- Streamlit app: `app.py`
- Streamlit demo guide: `docs/streamlit_demo.md`
- Video inference summary: `docs/video_demos/yolov8n_640_50epochs/video_inference_summary.md`

## Weight Policy

See `docs/model_weight_policy.md`.

- Model weights are not tracked in Git.
- `.pt`, `.pth`, and `.onnx` files must not be committed.
- Users must place weights locally before evaluation or inference.

## Related Documentation

- `README.md`
- `dataset/data.yaml`
- `docs/experiment_comparison.md`
- `docs/project_task_board.md`
