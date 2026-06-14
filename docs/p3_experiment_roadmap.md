# P3 Experiment Roadmap

## Purpose

P3 tasks are optional future experiments. They do not affect the current phase completion status.

The current repository is already suitable as a staged project deliverable. P3 work should be added only when the required weights, dataset access, GPU resources, and safety checks are available.

## Current Completed Baseline

The current completed baseline includes:

- YOLOv8n 640 baseline
- YOLOv8n official test split evaluation
- YOLOv8s supplementary validation result
- Streamlit scaffold and demo improvements
- FastAPI scaffold
- Docker scaffold

## Optional Experiments

### YOLOv8s Official Test Split Validation

- Goal: evaluate YOLOv8s on the official test split using the same metric protocol as YOLOv8n.
- Prerequisites: YOLOv8s `best.pt` must be available locally or retrained.
- Requires GPU: recommended.
- Expected output docs: `docs/evaluation/yolov8s_640_50epochs_official/`.
- Risk level: medium.

### Strict YOLOv8n vs YOLOv8s Same-Split Comparison

- Goal: compare YOLOv8n and YOLOv8s under the same split and metric protocol.
- Depends on YOLOv8s official test split validation.
- No fair comparison should be claimed until same split and same metric protocol are available.
- Requires GPU: indirectly yes.
- Risk level: medium.

### Image Size Ablation

- Goal: compare image sizes such as 416, 640, and an optional larger size.
- Requires controlled config and consistent experiment setup.
- Requires GPU: recommended.
- Risk level: high.

### YOLOv8m Experiment

- Goal: evaluate a larger model variant.
- Requires more compute and careful result tracking.
- Requires GPU: yes.
- Risk level: high.

### ONNX Export and Runtime Check

- Starts with `docs/onnx_export.md`.
- No GPU is required for the guide.
- ONNX Runtime check can run on CPU.
- Risk level: low to medium.

### Inference Speed Benchmark

- Starts with `docs/inference_speed_benchmark_plan.md`.
- GPU is optional depending on target environment.
- Risk level: medium.

## Recommended Order

1. ONNX export guide.
2. Benchmark plan.
3. YOLOv8s official test validation, only if weight is available.
4. Strict model comparison.
5. ONNX Runtime check.
6. Speed benchmark.
7. Image size ablation.
8. YOLOv8m experiment.

## Stop Conditions

Do not continue an optional experiment when:

- GPU is unavailable for GPU-dependent tasks.
- Required weights are unavailable.
- Dataset access is unavailable.
- There is a risk of committing large outputs.
- Metrics would be unfair or misleading.

## Related Files

- `docs/final_project_report.md`
- `docs/project_task_board.md`
- `docs/experiment_comparison.md`
- `docs/onnx_export.md`
- `docs/inference_speed_benchmark_plan.md`
- `docs/model_weight_policy.md`
