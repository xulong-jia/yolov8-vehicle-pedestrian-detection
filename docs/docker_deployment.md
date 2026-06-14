# Docker Deployment

## Purpose

This document describes the Docker scaffold for local Streamlit or future API deployment preparation. The Docker image is designed to include application code and lightweight documentation assets only.

The image does not include model weights, the full dataset, generated outputs, or large videos.

## Safety Design

- Weights are mounted at runtime.
- Docker image does not include `local_weights/`.
- Docker image does not include full dataset splits.
- Docker image does not include `runs/` or `local_outputs/`.
- Large videos are excluded.
- The dataset directory is ignored for Docker build context; the image does not include dataset files.

## Build Command

Example command:

```bash
docker build -t yolov8-vehicle-pedestrian-demo .
```

Do not treat this as a completed deployment record unless the image has actually been built and tested.

## Run Streamlit Container

Example command:

```bash
docker run --rm -p 8501:8501 -v /absolute/path/to/best.pt:/models/best.pt:ro yolov8-vehicle-pedestrian-demo
```

Replace `/absolute/path/to/best.pt` with the real local model weight path on the host machine.

Inside the container, the default environment variable is:

```text
MODEL_PATH=/models/best.pt
```

The current Streamlit app still allows the model path to be entered in the UI. A future update can connect the app or API service directly to `MODEL_PATH`.

## What Is Not Included

- `local_weights/`
- `dataset/train/`
- `dataset/valid/`
- `dataset/test/`
- `runs/`
- `local_outputs/`
- video demos
- raw local videos

## Development Notes

- Do not copy model weights into the Docker image.
- Do not commit `.env` files.
- Do not commit Docker build cache or generated outputs.
- Future FastAPI service can reuse the same mount-based model path strategy.
- Keep deployment artifacts lightweight and reproducible.

## Validation Checklist

Before committing Docker-related changes, run:

```bash
make check
make danger-check
make list-large-docs
```

Also check staged files before committing:

```bash
git diff --cached --name-only | grep -E '\.pt$|\.pth$|\.onnx$|\.mp4$|\.avi$|\.mov$|\.mkv$|^local_weights/|^local_videos/source/|^dataset/train/|^dataset/valid/|^dataset/test/|^runs/|^\.venv/|^local_outputs/' || true
```

The risk check should produce no output.

## Related Files

- `Dockerfile`
- `.dockerignore`
- `docs/model_loading_strategy.md`
- `docs/deployment_guide.md`
- `docs/model_weight_policy.md`
- `configs/default.yaml`
