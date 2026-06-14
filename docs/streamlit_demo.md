# Streamlit Image Detection Demo

## Purpose

This demo provides a lightweight local Streamlit interface for single-image YOLOv8 vehicle and pedestrian detection. It is intended for qualitative inspection and presentation, not official model evaluation.

The demo supports both uploaded images and local sample images from the project documentation assets.

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
3. Choose an input mode:
   - `Upload image`
   - `Use sample image`
4. Upload a local image or select a sample image.
5. Review the original image, detection result image, and detection table.

The detection table includes:

- class ID
- class name
- confidence
- xmin
- ymin
- xmax
- ymax

## Sample Image Selector

The app can scan the following directory for local sample images:

```text
docs/error_case_gallery/images/
```

Supported sample image formats:

- `.jpg`
- `.jpeg`
- `.png`

If sample images are available, the app shows a select box for choosing one. If the directory is missing or empty, the app shows:

```text
No sample images found. Please use image upload instead.
```

The sample selector does not copy images and does not create new image files.

## Downloadable Prediction CSV

When detections are available, the app shows a CSV download button below the detection table.

The downloaded CSV includes:

- class_id
- class_name
- confidence
- xmin
- ymin
- xmax
- ymax

If there are no detections above the selected confidence threshold, the app shows:

```text
No detections available for CSV download.
```

## Output Behavior

Prediction images are rendered in memory by Streamlit. The demo does not save prediction images, labels, `runs/` outputs, or CSV files to disk automatically.

## Notes About Local-Only Model Weights

Do not commit model weights to GitHub:

- `.pt`
- `.pth`
- `.onnx`

Keep trained weights under `local_weights/` or external storage.

Do not commit large inference outputs, videos, or generated `runs/` directories.

## Error Message Behavior

The app uses concise user-facing error messages instead of long tracebacks:

- Missing model weight: shows the expected local path `local_weights/yolov8n_640_50epochs/best.pt` and reminds users not to commit weights.
- Missing sample image directory or empty sample list: recommends upload mode.
- Unsupported or corrupted image: reports that the image could not be read.
- Model loading failure: shows a short model loading error message.
- Inference failure: shows a short inference error message.

## Troubleshooting

- If the app cannot find the model, place `best.pt` at `local_weights/yolov8n_640_50epochs/best.pt` or update the model path field.
- If no sample images are listed, use upload mode or check that `docs/error_case_gallery/images/` exists.
- If Streamlit is not installed, run `pip install -r requirements.txt`.
- If image loading fails, try a standard image format such as `.jpg` or `.png`.
- If no detections appear, lower the confidence threshold and try again.

## Limitation

This demo is for single-image qualitative inference only. It is not official evaluation and does not replace full validation metrics such as Precision, Recall, mAP50, or mAP50-95.
