# Inference Speed Benchmark Plan

## Purpose

This plan defines how to evaluate inference speed across model variants, input sizes, devices, batch sizes, and model formats. It is a planning document only.

## Current Scope

- No benchmark is run in this task.
- No inference outputs are generated.
- Results should not be reported until measured under controlled settings.

## Metrics to Record

Record at least:

- hardware
- device: CPU / GPU
- model variant
- model format: PyTorch / ONNX
- image size
- batch size
- warmup iterations
- measured iterations
- mean latency
- median latency
- p95 latency
- FPS
- notes about I/O inclusion or exclusion

## Recommended Benchmark Protocol

1. Record hardware and software versions.
2. Use a fixed test image set.
3. Separate model warmup from measurement.
4. Separate pure inference time from preprocessing and postprocessing if possible.
5. Run multiple measured iterations.
6. Report confidence limitations and environment variability.

## Suggested Benchmark Matrix

| Model | Format | Device | Image Size | Notes |
| --- | --- | --- | ---: | --- |
| YOLOv8n | PyTorch | CPU | 640 | Local CPU baseline |
| YOLOv8n | PyTorch | GPU | 640 | Stable GPU environment recommended |
| YOLOv8n | ONNX | CPU | 640 | Requires local ONNX export first |
| YOLOv8s | PyTorch | GPU | 640 | Only if YOLOv8s weight is available |
| YOLOv8n | PyTorch | CPU / GPU | 416 / 640 | Optional image size comparison |

No actual benchmark results are reported in this document.

## Output Template

| Date | Hardware | Device | Model | Format | Image Size | Batch Size | Mean Latency ms | Median Latency ms | p95 Latency ms | FPS | Notes |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## GPU Reminder

- Small smoke tests can run on CPU.
- Meaningful GPU latency benchmarks should use a stable GPU environment.
- Colab GPU results must mention GPU type and session variability.

## Safety Notes

- Benchmark outputs should go under `local_outputs/`.
- Do not commit large generated outputs.
- Do not commit model weights.
- Do not commit ONNX files unless project policy changes.

## Related Files

- `src/batch_predict.py`
- `docs/onnx_export.md`
- `docs/model_loading_strategy.md`
- `docs/docker_deployment.md`
- `Makefile`
