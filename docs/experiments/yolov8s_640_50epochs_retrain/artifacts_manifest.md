# Artifacts Manifest

- run_dir: `runs/detect/runs/detect/yolov8s_640_50epochs_retrain`

## Key Artifacts
- `weights/best.pt`: available
- `weights/last.pt`: available
- `results.csv`: available
- `args.yaml`: available
- `results.png`: available
- `confusion_matrix.png`: available
- `PR_curve.png`: missing
- `F1_curve.png`: missing
- `P_curve.png`: missing
- `R_curve.png`: missing
- `labels.jpg`: available
- `labels_correlogram.jpg`: missing

## Batch Images

- `train_batch*.jpg`: remains in `runs/` if generated
- `val_batch*.jpg`: remains in `runs/` if generated

## Storage Policy

- Large artifacts remain in `runs/` and `local_weights/`.
- Only lightweight docs and selected lightweight plots should be committed later.
- Do not commit `best.pt`, `last.pt`, full `runs/`, dataset splits, or zip backups.
