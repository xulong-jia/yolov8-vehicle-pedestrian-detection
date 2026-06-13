# Colab Official Validation Commands

This document provides the Google Colab GPU commands for official validation of the current YOLOv8n 640x640 50 epoch baseline.

Current task scope:

- Generate validation commands only.
- Do not run validation locally.
- Do not train a model.
- Do not run YOLO predict.
- Do not commit `.pt` weights.

## 1. Recommended Environment

This official validation step is recommended on Google Colab GPU.

Do not use local CPU/Mac for the official validation run unless Colab is unavailable and the runtime cost is acceptable.

## 2. Colab Environment Preparation

In Colab, select:

```text
Runtime -> Change runtime type -> GPU
```

Then run:

```bash
python --version
nvidia-smi
```

If `nvidia-smi` does not show a GPU, switch the Colab runtime to GPU before continuing.

## 3. Mount Google Drive

Use this if the project is stored in Google Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

## 4. Change to Project Directory

Adjust this path if the project is stored in a different Drive location:

```bash
cd /content/drive/MyDrive/yolov8-vehicle-pedestrian-detection
pwd
```

If the project was uploaded directly to Colab instead of Drive, change into that local Colab path instead.

## 5. Install Dependencies

Install Ultralytics:

```bash
pip install -U ultralytics
```

Optional environment check:

```bash
yolo checks
```

## 6. Baseline Weight Path

Current YOLOv8n 640x640 50 epoch baseline weight path:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

Confirm it exists in Colab:

```bash
test -f local_weights/yolov8n_640_50epochs/best.pt && echo "OK best.pt"
```

## 7. Dataset Split Selection

`dataset/data.yaml` includes:

```yaml
train: train/images
val: valid/images
test: test/images
```

Because a `test` split is available, the official validation should use:

```text
split=test
```

If a future dataset version does not include `test`, use `split=val` instead.

## 8. Official Validation Command

Run this on Google Colab GPU:

```bash
yolo detect val \
  model=local_weights/yolov8n_640_50epochs/best.pt \
  data=dataset/data.yaml \
  split=test \
  imgsz=640 \
  conf=0.25 \
  device=0 \
  project=runs/detect \
  name=val_yolov8n_640_50epochs_official \
  plots=True \
  save_json=False
```

Expected validation result directory:

```text
runs/detect/val_yolov8n_640_50epochs_official/
```

## 9. Files to Copy Back to docs/

After validation completes, copy useful lightweight outputs from:

```text
runs/detect/val_yolov8n_640_50epochs_official/
```

to:

```text
docs/evaluation/yolov8n_640_50epochs_official/
```

Recommended files:

- `results.png`
- `confusion_matrix.png`
- `confusion_matrix_normalized.png`, if generated
- `BoxPR_curve.png`
- `BoxF1_curve.png`
- `BoxP_curve.png`
- `BoxR_curve.png`
- `val_batch*_pred.jpg`
- `val_batch*_labels.jpg`
- `results.csv`

Example copy commands:

```bash
mkdir -p docs/evaluation/yolov8n_640_50epochs_official

cp runs/detect/val_yolov8n_640_50epochs_official/results.png docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/confusion_matrix.png docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/confusion_matrix_normalized.png docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/BoxPR_curve.png docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/BoxF1_curve.png docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/BoxP_curve.png docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/BoxR_curve.png docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/results.csv docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/val_batch*_pred.jpg docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
cp runs/detect/val_yolov8n_640_50epochs_official/val_batch*_labels.jpg docs/evaluation/yolov8n_640_50epochs_official/ 2>/dev/null || true
```

## 10. Post-Run Notes

- Keep `best.pt` and any other weight files out of GitHub.
- Do not commit the full `runs/` directory.
- Commit only selected lightweight evaluation artifacts under `docs/evaluation/yolov8n_640_50epochs_official/`.
- Record the validation metrics in a short summary Markdown file after copying the results.
