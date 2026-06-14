# ONNX Export Guide

## Purpose

ONNX export can help with:

- model portability
- deployment preparation
- potential ONNX Runtime inference
- edge or server inference preparation

This guide documents a safe local export workflow for future use.

## Current Scope

- This guide documents how to export a model to ONNX.
- No ONNX file is included in Git.
- No ONNX export needs to be run for this documentation task.
- Exported files should stay local-only.

## Default Source Weight

Default local source weight:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

Weights are not committed to Git. This path can be replaced with another user-provided local weight path.

## Recommended Local Output Path

Recommended local ONNX output path:

```text
local_outputs/onnx/yolov8n_640_50epochs/best.onnx
```

Notes:

- `local_outputs/` is ignored by Git.
- `*.onnx` is ignored by Git.
- Do not commit exported ONNX files.

## Example Export Command

Example command:

```bash
yolo export model=local_weights/yolov8n_640_50epochs/best.pt format=onnx imgsz=640 opset=12
```

Do not run this command as part of this documentation task.

Ultralytics may place the exported file next to the source model by default. If needed, move the generated `.onnx` file to:

```text
local_outputs/onnx/
```

and keep it local-only.

## Optional Python Export Example

Example code:

```python
from ultralytics import YOLO

model = YOLO("local_weights/yolov8n_640_50epochs/best.pt")
model.export(format="onnx", imgsz=640, opset=12)
```

Do not run this code as part of this documentation task.

## Verification Checklist

- Model weight exists locally.
- Export command completed.
- ONNX file exists locally.
- ONNX file is not tracked by Git.
- `git status` does not include `.onnx`.
- `make danger-check` has no output before commit.

## Git Safety

Do not commit:

- `*.onnx`
- `local_weights/`
- `local_outputs/`
- `runs/`

## Future Work

- ONNX Runtime inference test.
- ONNX output consistency check.
- Latency benchmark.
- Docker / ONNX Runtime deployment variant.

## Related Files

- `docs/model_weight_policy.md`
- `docs/model_loading_strategy.md`
- `docs/deployment_guide.md`
- `docs/docker_deployment.md`
- `configs/default.yaml`
- `Makefile`
