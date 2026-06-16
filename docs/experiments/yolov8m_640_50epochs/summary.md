# YOLOv8m 640x640 50 Epochs Training

## Summary

- Date/time: 2026-06-16T14:34:51
- Environment: Google Colab GPU, Tesla T4
- Model: YOLOv8m pretrained base
- Dataset: `dataset/data.yaml`
- Training image size: 640
- Epochs: 50
- Batch: 4
- Run directory: `runs/detect/runs/detect/yolov8m_640_50epochs`
- Local weight backup: `local_weights/yolov8m_640_50epochs/`
- Important note: weights and full runs are local-only and must not be committed.

## Training Validation Metrics

- Precision: 0.837
- Recall: 0.817
- mAP50: 0.870
- mAP50-95: 0.594

## Per-Class Validation Metrics

| Class | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Bus | 168 | 242 | 0.878 | 0.798 | 0.869 | 0.666 |
| Car | 136 | 1197 | 0.855 | 0.750 | 0.830 | 0.495 |
| Motorcycle | 165 | 249 | 0.936 | 0.972 | 0.976 | 0.721 |
| Person | 354 | 1332 | 0.926 | 0.890 | 0.951 | 0.614 |
| Truck | 128 | 409 | 0.749 | 0.824 | 0.867 | 0.588 |
| mini-truck | 104 | 302 | 0.679 | 0.669 | 0.726 | 0.479 |

## Interpretation

- YOLOv8m completed 50 epochs without out-of-memory errors.
- Training validation mAP50-95 reached 0.594.
- This does not replace official test split evaluation.
- The next required step is official test split validation using `local_weights/yolov8m_640_50epochs/best.pt`.

## Storage Policy

- Do not commit `.pt` weights.
- Do not commit full `runs/` outputs.
- Do not commit dataset splits.
- Only lightweight docs and selected small plots should be committed.
