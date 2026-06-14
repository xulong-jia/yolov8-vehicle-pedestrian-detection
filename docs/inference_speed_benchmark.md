# Inference Speed Benchmark

## Scope

- Same hardware: Google Colab Tesla T4
- Same device: CUDA GPU
- Same test image subset
- Same image size: 640
- Same Python environment
- Custom project weights only
- No prediction outputs saved

## Environment

- timestamp: `2026-06-14T10:26:32`
- platform: `Linux-6.6.122+-x86_64-with-glibc2.35`
- python_version: `3.12.13 (main, Mar  4 2026, 09:23:07) [GCC 11.4.0]`
- torch_version: `2.11.0+cu128`
- ultralytics_version: `8.4.67`
- cuda_available: `True`
- device: `cuda:0`
- gpu_name: `Tesla T4`
- imgsz: `640`
- image_source: `dataset/test/images`
- image_count: `100`
- warmup_count: `10`

## Protocol

- Test image source: `dataset/test/images`
- Warmup images: 10
- Measured images: 100
- Image size: 640
- Timing method: wall-clock `time.perf_counter()` with CUDA synchronization before and after each timed inference
- Ultralytics prediction outputs were not saved

## Results

| Model | Weight path | Device | Images | Avg ms/image | Median ms/image | P95 ms/image | Min ms/image | Max ms/image | FPS |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| YOLOv8n 640 50 epochs | `local_weights/yolov8n_640_50epochs/best.pt` | cuda:0 | 100 | 11.562 | 11.208 | 13.079 | 9.478 | 21.188 | 86.49 |
| YOLOv8s 640 50 epochs retrain | `local_weights/yolov8s_640_50epochs/best.pt` | cuda:0 | 100 | 15.985 | 15.522 | 19.847 | 13.380 | 26.755 | 62.56 |

## Interpretation

- Faster model by average latency: **YOLOv8n 640 50 epochs**.
- Average latency gap: 4.424 ms/image.
- Slower/faster latency ratio: 1.383x.
- YOLOv8s is more accurate on the official test split, but this benchmark quantifies the latency cost on the same Colab T4 hardware.
- Do not compare these numbers directly to CPU, Apple Silicon, or other GPU results unless hardware and protocol match.

## Related Accuracy Context

- YOLOv8n official test: P 0.841, R 0.816, mAP50 0.859, mAP50-95 0.582
- YOLOv8s official test: P 0.865, R 0.838, mAP50 0.876, mAP50-95 0.601
- Strict delta: +0.024 precision, +0.022 recall, +0.017 mAP50, +0.019 mAP50-95

## Caveats

- This is an inference latency benchmark, not a training benchmark.
- Results are hardware-dependent.
- No ONNX Runtime benchmark is included.
- No model weights are committed.
- Dataset splits and weights remain local-only artifacts.

## Output Files

- `docs/inference_speed_benchmark.md`
- `docs/inference_speed_benchmark.csv`
- `docs/inference_speed_benchmark_raw.json`
