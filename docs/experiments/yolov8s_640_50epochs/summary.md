# YOLOv8s 640x640 50 Epochs Experiment

## Training Setup

- Model: YOLOv8s
- Image size: 640
- Epochs: 50
- Batch size: 8
- Workers: 2
- Device: Google Colab GPU, Tesla T4
- Dataset: Roboflow vehicle-pedestrian detection dataset
- Train split: 2770 images
- Validation split: 791 images
- Output directory in Colab: `runs/detect/runs/detect/yolov8s_640_50epochs_batch8_py`
- Training time: 0.999 hours

## Final Validation Metrics

| Class | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| all | 791 | 3731 | 0.839 | 0.841 | 0.877 | 0.604 |
| Bus | 168 | 242 | 0.875 | 0.807 | 0.860 | 0.662 |
| Car | 136 | 1197 | 0.837 | 0.796 | 0.841 | 0.511 |
| Motorcycle | 165 | 249 | 0.925 | 0.984 | 0.987 | 0.730 |
| Person | 354 | 1332 | 0.929 | 0.898 | 0.955 | 0.621 |
| Truck | 128 | 409 | 0.785 | 0.839 | 0.872 | 0.595 |
| mini-truck | 104 | 302 | 0.683 | 0.722 | 0.747 | 0.506 |

## Key Observations

- YOLOv8s achieved stronger validation performance than the earlier YOLOv8n baseline on the validation split.
- Motorcycle remained the strongest class, with mAP50 = 0.987 and mAP50-95 = 0.730.
- Person also performed strongly, with mAP50 = 0.955.
- mini-truck remained the weakest class, but its mAP50-95 reached 0.506, which is substantially better than the YOLOv8n official test result for mini-truck.
- The model size increased from the YOLOv8n baseline to approximately 22.5MB for YOLOv8s best.pt.
- The final model weights are not included in GitHub and should remain local or in external storage.

## Notes

This result is based on the validation split during YOLOv8s training. For a strict comparison against the YOLOv8n official test split validation, YOLOv8s should also be evaluated on `split=test` using its `best.pt`.
