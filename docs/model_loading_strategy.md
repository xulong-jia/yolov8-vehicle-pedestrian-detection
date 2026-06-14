# Model Loading Strategy

## Purpose

This document defines how this project should load YOLOv8 model weights for local demos, command-line tools, and future API or Docker deployment while keeping model weights out of Git.

The core rule is simple: code and documentation can be tracked in Git, but trained model weights should remain local or be stored in external artifact storage.

## Default Local Model Path

Default local model path:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

This path is used as the default reference for local qualitative inference and demo workflows. The file itself is not included in the GitHub repository.

## Supported Loading Scenarios

- Streamlit app uses a user-provided model path with the default local path prefilled.
- Batch prediction CLI uses the `--model` argument.
- Future FastAPI service may use an environment variable such as `MODEL_PATH`.
- Future Docker deployment should mount weights as an external volume at runtime.

## Environment Variable Strategy

Recommended future environment variable:

```bash
MODEL_PATH=/models/best.pt
```

Future API or service code can read `MODEL_PATH` instead of hardcoding machine-specific paths.

Guidelines:

- Do not hardcode absolute user-specific paths.
- Do not commit `.env` files containing private local paths.
- Keep environment-specific model locations outside source code.
- Validate that the path exists before starting inference.

## Docker / Volume Strategy

Future Docker images should not copy local weights into the image.

Do not use:

```dockerfile
COPY local_weights/ /models/
```

Instead, mount weights at runtime:

```bash
docker run -v /local/path/to/weights:/models ...
```

The container can then read:

```text
/models/best.pt
```

This keeps the Docker image lightweight and avoids leaking private or large model artifacts.

## Git Safety Rules

Do not commit:

- `local_weights/`
- `*.pt`
- `*.pth`
- `*.onnx`
- `runs/`
- `local_outputs/`

Before committing, run:

```bash
make danger-check
```

The command should produce no output for staged files.

## Validation Checklist

Before running local inference or a future service, check:

- Model path exists.
- Model file extension is `.pt` for PyTorch inference.
- Dataset YAML exists if the workflow needs dataset metadata.
- Sample image or input image exists.
- `make danger-check` has no output before commit.
- Generated outputs stay under ignored local directories such as `local_outputs/`.

## Related Files

- `docs/model_weight_policy.md`
- `configs/default.yaml`
- `app.py`
- `src/batch_predict.py`
- `src/check_setup.py`
- `Makefile`
