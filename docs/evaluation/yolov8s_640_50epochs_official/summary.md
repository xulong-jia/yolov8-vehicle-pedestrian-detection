# YOLOv8s 640x640 Official Test Split Evaluation

## Summary

- Date/time: 2026-06-14T08:47:08
- Environment: Google Colab GPU, Tesla T4
- Model path: `local_weights/yolov8s_640_50epochs/best.pt`
- Dataset: `dataset/data.yaml`
- Split: test
- Test images: 396
- Test labels: 396
- Test instances: 1642
- Image size: 640
- Validation run directory: `runs/detect/runs/detect/val_yolov8s_640_50epochs_official`
- Important note: weights are local-only and must not be committed.
- This is the official test split evaluation for the retrained YOLOv8s model.

## All-Class Test Metrics

- Precision: 0.865
- Recall: 0.838
- mAP50: 0.876
- mAP50-95: 0.601

## Per-Class Test Metrics

| Class | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Bus | 103 | 146 | 0.956 | 0.742 | 0.862 | 0.643 |
| Car | 61 | 479 | 0.876 | 0.826 | 0.904 | 0.568 |
| Motorcycle | 66 | 104 | 0.896 | 0.99 | 0.979 | 0.731 |
| Person | 178 | 613 | 0.954 | 0.887 | 0.938 | 0.622 |
| Truck | 58 | 186 | 0.852 | 0.866 | 0.906 | 0.632 |
| mini-truck | 49 | 114 | 0.657 | 0.719 | 0.669 | 0.408 |
