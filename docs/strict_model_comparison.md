# Strict Same-Split Model Comparison

## Purpose

This document compares YOLOv8n and YOLOv8s under the same official test split, the same image size, and the same dataset config. It is intended to separate strict same-split test comparison from earlier supplementary validation-only comparisons.

## Comparison Scope

- Dataset: `dataset/data.yaml`
- Split: test
- Test images: 396
- Test instances: 1642
- Image size: 640
- Models:
  - YOLOv8n 640x640 50 epochs baseline
  - YOLOv8s 640x640 50 epochs retrain
- Metrics:
  - Precision
  - Recall
  - mAP50
  - mAP50-95

## Main Results

| Model | Split | Image Size | Precision | Recall | mAP50 | mAP50-95 | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| YOLOv8n 640 50 epochs | test | 640 | 0.841 | 0.816 | 0.859 | 0.582 | Official test split baseline |
| YOLOv8s 640 50 epochs retrain | test | 640 | 0.865 | 0.838 | 0.876 | 0.601 | Official test split evaluation after retrain |

## Delta Summary

| Metric | YOLOv8n | YOLOv8s | Absolute Delta |
| --- | ---: | ---: | ---: |
| Precision | 0.841 | 0.865 | +0.024 |
| Recall | 0.816 | 0.838 | +0.022 |
| mAP50 | 0.859 | 0.876 | +0.017 |
| mAP50-95 | 0.582 | 0.601 | +0.019 |

## Interpretation

YOLOv8s improves all listed metrics on the same official test split. The gains are moderate but consistent across Precision, Recall, mAP50, and mAP50-95.

YOLOv8s has more parameters and higher compute cost than YOLOv8n, so the improvement should be weighed against inference latency, memory use, and deployment constraints. This comparison is stricter than the previous validation-only YOLOv8s supplementary result because both models are now compared on the official test split.

## Per-Class Notes

The YOLOv8s official test split per-class metrics show:

- `Motorcycle`, `Person`, and `Truck` perform strongly.
- `mini-truck` remains the weakest class by mAP50-95.
- `Bus` has much higher precision than recall, indicating possible missed bus detections.
- `Car`, `Truck`, and `mini-truck` visual similarity should remain an analysis focus.

YOLOv8n official test per-class deltas are not included here because only the all-class YOLOv8n official test metrics are available in the tracked comparison summary.

## Caveats

- Training conditions may not be perfectly identical because YOLOv8s was retrained in Colab after the earlier YOLOv8n baseline.
- Dataset split and evaluation protocol are aligned for this comparison.
- No speed benchmark is included here.
- No model weights are committed.

## Related Files

- [YOLOv8s official test summary](evaluation/yolov8s_640_50epochs_official/summary.md)
- [YOLOv8s official test metrics](evaluation/yolov8s_640_50epochs_official/metrics.csv)
- [YOLOv8s retrain summary](experiments/yolov8s_640_50epochs_retrain/summary.md)
- [Experiment comparison](experiment_comparison.md)
- [Final project report](final_project_report.md)
- [Model weight policy](model_weight_policy.md)
