# Artifacts Manifest

- val_dir: `runs/detect/runs/detect/val_yolov8s_640_50epochs_official`

## Validation Artifacts
- `confusion_matrix.png`: available
- `confusion_matrix_normalized.png`: available
- `BoxPR_curve.png`: available
- `BoxF1_curve.png`: available
- `BoxP_curve.png`: available
- `BoxR_curve.png`: available

## Batch Images

- `val_batch*_labels.jpg`: remains in `runs/` if generated
- `val_batch*_pred.jpg`: remains in `runs/` if generated

## Storage Policy

- Full validation run remains in `runs/`.
- Only lightweight docs and selected plots should be committed later.
- Do not commit `.pt` files, full `runs/`, dataset splits, or zip backups.
