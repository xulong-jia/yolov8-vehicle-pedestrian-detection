# ONNX Runtime Benchmark

## Scope

- Temporary ONNX export from custom YOLOv8n and YOLOv8s project weights.
- ONNX Runtime inference check and latency benchmark.
- Same test image subset and image size as the PyTorch benchmark.
- No mAP validation, no NMS evaluation, and no prediction images saved.
- ONNX files are temporary Colab artifacts and are not committed.

## Environment

- timestamp: `2026-06-16T11:20:41`
- platform: `Linux-6.6.122+-x86_64-with-glibc2.35`
- python_version: `3.12.13 (main, Mar  4 2026, 09:23:07) [GCC 11.4.0]`
- torch_version: `2.11.0+cu128`
- ultralytics_version: `8.4.68`
- onnx_version: `1.22.0`
- onnxruntime_version: `1.26.0`
- available_providers: `['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']`
- preferred_provider: `CUDAExecutionProvider`
- torch_cuda_available: `True`
- gpu_name: `Tesla T4`
- imgsz: `640`
- image_source: `dataset/test/images`
- image_count: `100`
- warmup_count: `10`

## ONNX Runtime Providers

- Available providers: `['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']`
- Preferred provider: `CUDAExecutionProvider`
- Actual providers are recorded per model in the results table.

## Protocol

- Test image source: `dataset/test/images`
- Warmup images: 10
- Measured images: 100
- Image size: 640
- Preprocessing: RGB, letterbox to 640x640, CHW, float32, normalized to 0-1, batch size 1.
- Timing method: wall-clock `time.perf_counter()` around ONNX Runtime `session.run()`.

## Results

| Model | Runtime | Provider | Images | Avg ms/image | Median ms/image | P95 ms/image | Min ms/image | Max ms/image | FPS |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| YOLOv8n 640 50 epochs | ONNX Runtime | `CUDAExecutionProvider,CPUExecutionProvider` | 100 | 10.994 | 9.393 | 16.948 | 8.386 | 41.599 | 90.96 |
| YOLOv8s 640 50 epochs retrain | ONNX Runtime | `CUDAExecutionProvider,CPUExecutionProvider` | 100 | 13.657 | 12.868 | 21.295 | 9.760 | 28.301 | 73.22 |

## Correctness / Check Summary

- YOLOv8n 640 50 epochs:
  - Output shapes on first image: `[[1, 10, 8400]]`
  - Output finite: `True`
  - Output non-empty: `True`
- YOLOv8s 640 50 epochs retrain:
  - Output shapes on first image: `[[1, 10, 8400]]`
  - Output finite: `True`
  - Output non-empty: `True`

## Interpretation

- Faster ONNX Runtime model by average latency: **YOLOv8n 640 50 epochs**.
- Average latency gap: 2.663 ms/image.
- Slower/faster latency ratio: 1.242x.
- Provider choice strongly affects latency; compare these numbers only when provider and hardware match.

## Comparison with Previous PyTorch Colab T4 Benchmark

| Model | PyTorch CUDA avg ms/image | PyTorch CUDA FPS |
| --- | ---: | ---: |
| YOLOv8n 640 50 epochs | 11.562 | 86.49 |
| YOLOv8s 640 50 epochs retrain | 15.985 | 62.56 |

## Caveats

- This is an ONNX Runtime inference benchmark/check, not an mAP validation.
- No ONNX Runtime NMS or mAP evaluation is included.
- No ONNX files are committed.
- Results depend on ONNX Runtime provider, hardware, Colab runtime, and preprocessing implementation.
- Model weights and dataset splits remain local-only artifacts.

## Output Files

- `docs/onnx_runtime_benchmark.md`
- `docs/onnx_runtime_benchmark.csv`
- `docs/onnx_runtime_benchmark_raw.json`
