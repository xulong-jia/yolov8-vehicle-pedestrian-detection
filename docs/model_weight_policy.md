# Model Weight Policy

## Purpose

This file defines how model weights should be stored locally and why they should not be committed to GitHub.

## Do Not Commit

Do not commit:

- `local_weights/`
- `*.pt`
- `*.pth`
- `*.onnx`
- `runs/`
- full exported model artifacts

## Expected Local Weight Paths

Current expected local weight paths:

- `local_weights/yolov8n_640_50epochs/best.pt`
- `local_weights/yolov8n_640_50epochs/last.pt`

Optional future weights should follow:

```text
local_weights/<experiment_name>/best.pt
```

## Why Weights Are Not Tracked

Weights are not tracked because:

- they are large binary files
- they increase repository size
- reproducibility should rely on documented commands, configs, metrics, and summaries instead of committed binaries
- code/docs should remain separate from local experiment artifacts

## How to Use Local Weights

- Place `best.pt` under the expected local path before evaluation or inference.
- The Streamlit app uses `local_weights/yolov8n_640_50epochs/best.pt` as its default model path.
- CLI scripts can use an explicit `--model` path.
- Users should verify the model path exists before inference.

## Safety Checks Before Commit

Run this before committing:

```bash
git diff --cached --name-only | grep -E '\.pt$|\.pth$|\.onnx$|\.mp4$|\.avi$|\.mov$|\.mkv$|^local_weights/|^local_videos/source/|^dataset/train/|^dataset/valid/|^dataset/test/|^runs/|^\.venv/' || true
```

No output means no obvious dangerous files are staged.

If output appears, stop and unstage those files before committing.

## Related Files

- `.gitignore`
- `app.py`
- `docs/streamlit_demo.md`
- `docs/project_task_board.md`
