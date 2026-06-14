# YOLOv8s 640x640 50 Epoch Retrain

## Summary

- Date/time: 2026-06-14T08:40:33
- Environment: Google Colab GPU, Tesla T4
- Dataset: `dataset/data.yaml`
- Split used for training: train/valid
- Model: `yolov8s.pt`
- Epochs: 50
- Image size: 640
- Batch: 8
- Output run directory: `runs/detect/runs/detect/yolov8s_640_50epochs_retrain`
- Weight backup path: `local_weights/yolov8s_640_50epochs/best.pt`

## Important Notes

- Weights are local-only and must not be committed.
- Full `runs/` outputs remain local/Colab-only.
- This is a validation result from training, not official test split evaluation.

## Final Validation Metrics

- Precision: 0.83909
- Recall: 0.84059
- mAP50: 0.87705
- mAP50-95: 0.60405
