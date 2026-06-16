# YOLOv8m 640x640 Official Test Split Evaluation

## Summary

- Date/time: 2026-06-16T14:38:57
- Environment: Google Colab GPU, Tesla T4
- Model path: `local_weights/yolov8m_640_50epochs/best.pt`
- Dataset: `dataset/data.yaml`
- Split: test
- Test images: 396
- Test instances: 1642
- Image size: 640
- Validation run directory: `runs/detect/runs/detect/val_yolov8m_640_50epochs_official`
- Important note: weights and full validation runs are local-only and must not be committed.

## All-Class Official Test Metrics

- Precision: 0.852
- Recall: 0.820
- mAP50: 0.872
- mAP50-95: 0.594

## Per-Class Official Test Metrics

| Class | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Bus | 103 | 146 | 0.926 | 0.776 | 0.88 | 0.682 |
| Car | 61 | 479 | 0.873 | 0.797 | 0.894 | 0.549 |
| Motorcycle | 66 | 104 | 0.916 | 0.962 | 0.985 | 0.722 |
| Person | 178 | 613 | 0.945 | 0.877 | 0.929 | 0.611 |
| Truck | 58 | 186 | 0.823 | 0.85 | 0.902 | 0.618 |
| mini-truck | 49 | 114 | 0.63 | 0.658 | 0.643 | 0.381 |

## Initial Interpretation

- YOLOv8m official test mAP50-95 is 0.594.
- This does not outperform the previously documented YOLOv8s official test mAP50-95 of 0.601.
- YOLOv8m should therefore be treated as a model-scaling experiment rather than an immediate replacement for YOLOv8s.
- A model-family comparison should be updated before making a final project decision.

## Caveats

- This is official test split evaluation only.
- Speed benchmark for YOLOv8m has not yet been run.
- ONNX Runtime check for YOLOv8m has not yet been run.
- No model weights or full runs are committed.
