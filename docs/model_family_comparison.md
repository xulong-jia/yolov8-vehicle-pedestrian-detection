# YOLOv8 Model Family Comparison

## Purpose

This document compares YOLOv8n, YOLOv8s, and YOLOv8m on the same official test split. It focuses on official-test accuracy and uses the existing speed benchmarks to support deployment trade-off decisions.

## Evaluation Scope

- Dataset: `dataset/data.yaml`
- Split: official test
- Test images: 396
- Test instances: 1642
- Image size: 640
- Metrics: Precision, Recall, mAP50, mAP50-95
- Note: YOLOv8m speed benchmark has not yet been run.

## Official Test Accuracy

| Model | Precision | Recall | mAP50 | mAP50-95 | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| YOLOv8n 640 50 epochs | 0.841 | 0.816 | 0.859 | 0.582 | Official test split baseline |
| YOLOv8s 640 50 epochs retrain | 0.865 | 0.838 | 0.876 | 0.601 | Best current official-test accuracy |
| YOLOv8m 640 50 epochs | 0.852 | 0.820 | 0.872 | 0.594 | Model-scaling experiment; below YOLOv8s on mAP50-95 |

## Accuracy Delta vs YOLOv8s

| Metric | YOLOv8s | YOLOv8m | YOLOv8m - YOLOv8s |
| --- | ---: | ---: | ---: |
| Precision | 0.865 | 0.852 | -0.013 |
| Recall | 0.838 | 0.820 | -0.018 |
| mAP50 | 0.876 | 0.872 | -0.004 |
| mAP50-95 | 0.601 | 0.594 | -0.007 |

## Speed Context

| Model | PyTorch T4 avg ms/image | PyTorch T4 FPS | ONNX Runtime T4 avg ms/image | ONNX Runtime T4 FPS | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| YOLOv8n | 11.562 | 86.49 | 10.994 | 90.96 | Fastest measured model |
| YOLOv8s | 15.985 | 62.56 | 13.657 | 73.22 | Best current accuracy/latency trade-off |
| YOLOv8m | not measured | not measured | not measured | not measured | Speed benchmark not yet run |

## Interpretation

- YOLOv8s remains the best current official-test accuracy model among the measured n/s/m family.
- YOLOv8m did not improve over YOLOv8s on mAP50-95.
- YOLOv8m is larger and expected to be slower, while current measured accuracy is slightly lower than YOLOv8s.
- YOLOv8m should not replace YOLOv8s based on current results.
- YOLOv8n remains the fastest measured model and is still useful when latency matters most.

## Recommendation

- Default recommended model: YOLOv8s for best accuracy/latency trade-off.
- Use YOLOv8n for lightweight demo or faster inference.
- Do not use YOLOv8m as the default unless future speed or error analysis finds a specific reason.
- Optional next step: run YOLOv8m speed benchmark only if needed for completeness.

## Related Files

- [Strict model comparison](strict_model_comparison.md)
- [Inference speed benchmark](inference_speed_benchmark.md)
- [ONNX Runtime benchmark](onnx_runtime_benchmark.md)
- [Image size ablation](image_size_ablation.md)
- [YOLOv8m official test summary](evaluation/yolov8m_640_50epochs_official/summary.md)
- [YOLOv8m training summary](experiments/yolov8m_640_50epochs/summary.md)
- [YOLOv8s official test summary](evaluation/yolov8s_640_50epochs_official/summary.md)
