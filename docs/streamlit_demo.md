# Streamlit Image Detection Demo

## Purpose

This demo provides a lightweight local Streamlit interface for single-image YOLOv8 vehicle and pedestrian detection. It is intended for qualitative inspection and presentation, not official model evaluation.

## Requirements

Install project dependencies:

```bash
pip install -r requirements.txt
```

The demo uses:

- Streamlit
- Ultralytics YOLOv8
- PIL
- NumPy
- Pandas

## Model Weight Location

Default model path:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

The model weight is local-only and should not be committed to GitHub.

If the file is missing, the app shows:

```text
Model weight not found. Please place best.pt at local_weights/yolov8n_640_50epochs/best.pt
```

## How to Run

From the project root:

```bash
streamlit run app.py
```

## How to Use

1. Confirm `best.pt` exists at `local_weights/yolov8n_640_50epochs/best.pt`, or enter a different local model path in the app.
2. Choose a confidence threshold. The default is `0.25`; the supported range is `0.05` to `0.95`.
3. Upload a local image.
4. Review the original image, detection result image, and detection table.

The detection table includes:

- class name
- confidence
- xmin
- ymin
- xmax
- ymax

## Notes About Local-Only Model Weights

Do not commit model weights to GitHub:

- `.pt`
- `.pth`
- `.onnx`

Keep trained weights under `local_weights/` or external storage.

## Troubleshooting

- If the app cannot find the model, place `best.pt` at `local_weights/yolov8n_640_50epochs/best.pt` or update the model path field.
- If Streamlit is not installed, run `pip install -r requirements.txt`.
- If image loading fails, try a standard image format such as `.jpg` or `.png`.
- If no detections appear, lower the confidence threshold and try again.

## Limitation

This demo is for single-image qualitative inference only. It is not official evaluation and does not replace full validation metrics such as Precision, Recall, mAP50, or mAP50-95.
