# P3 Experiment Roadmap

## Purpose

P3 tasks are optional future experiments. They do not affect the current phase completion status.

The current repository is already suitable as a staged project deliverable. P3 work should be added only when the required weights, dataset access, GPU resources, and safety checks are available.

## Current Completed Baseline

The current completed baseline includes:

- YOLOv8n 640 baseline
- YOLOv8n official test split evaluation
- YOLOv8s supplementary validation result
- YOLOv8s official test split evaluation
- strict YOLOv8n vs YOLOv8s same-split comparison
- Streamlit scaffold and demo improvements
- FastAPI scaffold
- real FastAPI `/predict` image inference endpoint
- Docker scaffold

## Completed P3 Work

### YOLOv8s Official Test Split Validation

- Status: completed.
- Output docs: `docs/evaluation/yolov8s_640_50epochs_official/summary.md`.
- Official test metrics: Precision `0.865`, Recall `0.838`, mAP50 `0.876`, mAP50-95 `0.601`.
- Weights remain local-only and are not committed.

### Strict YOLOv8n vs YOLOv8s Same-Split Comparison

- Status: completed.
- Output docs: `docs/strict_model_comparison.md`.
- Same-split delta for YOLOv8s over YOLOv8n: Precision `+0.024`, Recall `+0.022`, mAP50 `+0.017`, mAP50-95 `+0.019`.
- No speed benchmark is included in this comparison.

## Remaining Optional Experiments

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

1. ONNX Runtime check.
2. Speed benchmark.
3. Image size ablation.
4. YOLOv8m experiment.

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
- `docs/strict_model_comparison.md`
- `docs/evaluation/yolov8s_640_50epochs_official/summary.md`
- `docs/onnx_export.md`
- `docs/inference_speed_benchmark_plan.md`
- `docs/model_weight_policy.md`
