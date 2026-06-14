# API Usage

## Purpose

This document describes the FastAPI scaffold for a future YOLOv8 model inference service. It is not a production deployment and does not currently run real model inference.

## Current Scope

The current scaffold includes:

- health check
- config endpoint
- model status endpoint
- prediction endpoint placeholder

Current limitations:

- `/predict` does not run real inference.
- No model is loaded by default.
- No GPU is required for the current scaffold.
- No uploaded files are saved to disk.

## Install API Dependencies

Install FastAPI scaffold dependencies:

```bash
pip install -r requirements-api.txt
```

For development and tests:

```bash
pip install -r requirements-dev.txt
```

The dependency split is:

- `requirements.txt`: main demo and runtime dependencies
- `requirements-dev.txt`: development and test dependencies
- `requirements-api.txt`: FastAPI scaffold dependencies

## Run API Locally

Example command:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

This command is provided for local development. It was not run as part of the scaffold creation.

## Endpoints

### GET /health

Example:

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "service": "yolov8-vehicle-pedestrian-api"
}
```

### GET /config

Example:

```bash
curl http://localhost:8000/config
```

Example response:

```json
{
  "default_model_path": "local_weights/yolov8n_640_50epochs/best.pt",
  "model_path_env": "",
  "image_size": 640,
  "confidence": 0.25,
  "device": "cpu"
}
```

### GET /model-status

Example:

```bash
curl http://localhost:8000/model-status
```

This endpoint checks whether the configured model path exists. It does not load the model.

Example response:

```json
{
  "model_path": "local_weights/yolov8n_640_50epochs/best.pt",
  "exists": true,
  "loaded": false
}
```

### POST /predict

The current endpoint is a placeholder and intentionally does not run inference.

Example:

```bash
curl -X POST http://localhost:8000/predict
```

Expected behavior:

```json
{
  "detail": "Prediction endpoint scaffolded but real inference is intentionally disabled in this version."
}
```

The response status is HTTP 501.

## Model Path Strategy

Model path priority:

1. `MODEL_PATH` environment variable
2. `configs/default.yaml` value at `paths.default_model`
3. fallback path `local_weights/yolov8n_640_50epochs/best.pt`

Do not commit model weights.

For Docker-style local runs, weights can be mounted at:

```text
/models/best.pt
```

and exposed to the service with:

```bash
MODEL_PATH=/models/best.pt
```

## Future Work

- real image upload inference
- input validation
- response schema
- batch endpoint
- Docker API command
- GPU deployment option if needed

## Safety Notes

- do not commit weights
- do not commit datasets
- do not commit `local_outputs/`
- do not commit `runs/`
- do not commit videos
- do not expose private file paths in public docs

## Related Files

- `src/api.py`
- `docs/model_loading_strategy.md`
- `docs/deployment_guide.md`
- `docs/docker_deployment.md`
- `configs/default.yaml`
- `docs/model_weight_policy.md`
