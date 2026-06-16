# YOLOv8m Experiment Plan

## Purpose

The YOLOv8m experiment is an optional model scaling step. Its purpose is to:

- evaluate whether a larger model brings a meaningful accuracy improvement on the official test split
- compare YOLOv8m against YOLOv8n and YOLOv8s on accuracy and latency
- decide whether the larger model is worth the additional deployment cost

## Current Baselines

YOLOv8n official test:

- Precision: 0.841
- Recall: 0.816
- mAP50: 0.859
- mAP50-95: 0.582

YOLOv8s official test:

- Precision: 0.865
- Recall: 0.838
- mAP50: 0.876
- mAP50-95: 0.601

PyTorch T4 speed:

- YOLOv8n: 11.562 ms/image, 86.49 FPS
- YOLOv8s: 15.985 ms/image, 62.56 FPS

ONNX Runtime T4 speed:

- YOLOv8n: 10.994 ms/image, 90.96 FPS
- YOLOv8s: 13.657 ms/image, 73.22 FPS

Image size ablation:

- 416: mAP50 0.855, mAP50-95 0.576
- 512: mAP50 0.863, mAP50-95 0.582
- 640: mAP50 0.859, mAP50-95 0.582

## Proposed Training Configuration

Suggested configuration, not yet executed:

- model: `yolov8m.pt`
- data: `dataset/data.yaml`
- epochs: 50
- imgsz: 640
- batch: start with 4 or auto, depending on T4 memory
- device: 0
- project: `runs/detect`
- name: `yolov8m_640_50epochs`
- plots: True

Notes:

- This requires GPU.
- This should be run in Colab T4 or better.
- If OOM occurs, reduce batch size.
- Do not commit weights or full runs outputs.

## Required Evaluation After Training

After training, the following checks should be completed before making any project decision:

1. Validation summary from the training run
2. Official test split validation
3. Strict comparison against YOLOv8n and YOLOv8s
4. PyTorch inference speed benchmark on the same 100 test images
5. Optional ONNX Runtime check/benchmark
6. Error analysis only if metrics justify the additional review work

## Expected Output Docs

Only lightweight documentation and selected small artifacts should be committed, for example:

- `docs/experiments/yolov8m_640_50epochs/summary.md`
- `docs/evaluation/yolov8m_640_50epochs_official/summary.md`
- `docs/model_family_comparison.md`
- `docs/model_family_comparison.csv`
- optional `docs/yolov8m_speed_benchmark.md`
- optional `docs/yolov8m_speed_benchmark.csv`
- optional `docs/yolov8m_speed_benchmark_raw.json`
- optional `docs/yolov8m_onnx_runtime_benchmark.md`
- optional `docs/yolov8m_onnx_runtime_benchmark.csv`
- optional `docs/yolov8m_onnx_runtime_benchmark_raw.json`

Do not commit:

- `.pt`
- `.onnx`
- `runs/`
- dataset splits
- zip files
- `local_outputs/`

## Decision Criteria

YOLOv8m should only be kept as a meaningful project upgrade if it provides clear value over YOLOv8s:

- mAP50-95 improves at least +0.010 to +0.020 over YOLOv8s
- latency cost is acceptable for the target demo or deployment scenario
- per-class improvements are consistent, not likely random variation
- mini-truck, Bus, or Car/Truck/mini-truck confusion improves in a useful way

## Risks

- T4 out-of-memory errors
- longer training time
- marginal gains over YOLOv8s
- more complicated artifact handling
- latency may be too high for deployment

## Recommended Next Step

Do not run YOLOv8m immediately unless the goal is model scaling research.

If continuing, start with a Colab dry run that checks GPU memory, dataset availability, and safe output paths before training. Preserve `v0.6.0-image-size-ablation` as the current stable version before starting any YOLOv8m work.
