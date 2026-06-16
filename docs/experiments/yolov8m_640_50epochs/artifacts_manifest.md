# Artifacts Manifest

- run_dir: `runs/detect/runs/detect/yolov8m_640_50epochs`
- weights_dir: `runs/detect/runs/detect/yolov8m_640_50epochs/weights`

## Selected Lightweight Artifacts
- `results.png`: available
- `confusion_matrix.png`: available
- `confusion_matrix_normalized.png`: available
- `BoxPR_curve.png`: available
- `BoxF1_curve.png`: available
- `BoxP_curve.png`: available
- `BoxR_curve.png`: available
- `labels.jpg`: available
- `labels_correlogram.jpg`: missing

## Storage Policy

- Full training run is backed up outside Git.
- Weights are backed up locally but are not committed.
- Only lightweight docs and selected plots should be committed later.
