# Local Deployment Guide

## Purpose

This guide explains how to run the project demo and utility scripts locally. It is a local deployment guide, not a cloud production deployment guide.

The project is designed to keep model weights, full datasets, generated outputs, and large videos outside Git.

## Prerequisites

- Python 3.11 recommended
- `pip`
- Local model weight file
- Optional virtual environment

## Install Dependencies

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

Optional development and test dependencies:

```bash
pip install -r requirements-dev.txt
```

Optional FastAPI scaffold dependencies:

```bash
pip install -r requirements-api.txt
```

Dependency files are split by purpose:

- `requirements.txt`: main demo and runtime dependencies
- `requirements-dev.txt`: development and test dependencies
- `requirements-api.txt`: FastAPI scaffold dependencies

## Model Weights

Model weights are not included in GitHub.

Expected local path:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

Do not commit model weights.

## Run Setup Check

From the project root:

```bash
python3 src/check_setup.py
```

This checks core paths, sample images, and tracked risk files without training or inference.

## Run Streamlit Demo

Run directly:

```bash
streamlit run app.py
```

Or through Makefile:

```bash
make streamlit
```

The Streamlit demo supports:

- uploaded image input
- sample image selector
- confidence threshold adjustment
- detection table
- CSV download

The demo does not save prediction outputs by default.

## Run Batch Prediction CLI

Example command:

```bash
python3 src/batch_predict.py --model local_weights/yolov8n_640_50epochs/best.pt --source docs/error_case_gallery/images --output-csv local_outputs/batch_predictions/detections.csv
```

Notes:

- Default output is CSV.
- Use `--save-images` only when annotated images are needed.
- Generated outputs should go under `local_outputs/`.
- `local_outputs/` is ignored by Git.

## Run Checks

Run Python syntax checks:

```bash
make check
```

Check staged files for risky paths:

```bash
make danger-check
```

List large files under `docs/`:

```bash
make list-large-docs
```

## What Not to Commit

Do not commit:

- weights
- full dataset
- `runs/`
- `local_outputs/`
- large videos
- ONNX exports

## Troubleshooting

### Model Not Found

Place the model at:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

or pass a different local path through the Streamlit model path field or the CLI `--model` argument.

### PyYAML Missing

`src/check_setup.py` can fall back to built-in defaults if PyYAML is missing, but installing project dependencies is recommended:

```bash
pip install -r requirements.txt
```

### Pytest Missing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Sample Images Missing

The Streamlit sample selector expects images under:

```text
docs/error_case_gallery/images/
```

If no sample images are found, use upload mode instead.

### Streamlit Not Installed

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

### No Detections Found

Try lowering the confidence threshold, checking the image quality, or testing another image. No detections in a single image should not be interpreted as an official model metric.

## Related Files

- `README.md`
- `docs/model_loading_strategy.md`
- `docs/model_weight_policy.md`
- `docs/streamlit_demo.md`
- `src/check_setup.py`
- `src/batch_predict.py`
- `Makefile`
