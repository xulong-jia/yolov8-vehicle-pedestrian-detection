# Final Project Report

## 1. Project Overview

This project is a YOLOv8 vehicle and pedestrian detection project for multi-class object detection. It focuses on model training, evaluation, inference demos, qualitative error analysis, and engineering preparation for local deployment.

The project has evolved from a baseline computer vision experiment into a more complete engineering-oriented repository with documented model behavior, safety policies, local demo tooling, CLI utilities, a real FastAPI image prediction endpoint, and Docker scaffold.

## 2. Dataset

The dataset uses Roboflow YOLOv8 format.

Classes:

- `Bus`
- `Car`
- `Motorcycle`
- `Person`
- `Truck`
- `mini-truck`

Dataset config:

- `dataset/data.yaml`

The full dataset split folders are local-only and ignored by Git:

- `dataset/train/`
- `dataset/valid/`
- `dataset/test/`

Label validation and cleaning were performed. After cleaning, no invalid class IDs were reported. Polygon-like invalid labels were converted or fixed so the dataset could be used in YOLOv8 training and evaluation workflows.

## 3. Model Experiments

### YOLOv8n 416x416 10 Epoch Smoke Test

- mAP50: 0.797
- mAP50-95: 0.511
- Purpose: quick training and infrastructure validation.

### YOLOv8n 640x640 50 Epoch Baseline

- Precision: 0.81981
- Recall: 0.82768
- mAP50: 0.86422
- mAP50-95: 0.59102

### YOLOv8n Official Test Split Evaluation

- Precision: 0.841
- Recall: 0.816
- mAP50: 0.859
- mAP50-95: 0.582

### YOLOv8s 640x640 50 Epoch Retrain Validation

- Precision: 0.83909
- Recall: 0.84059
- mAP50: 0.87705
- mAP50-95: 0.60405

This is the validation result from the YOLOv8s retraining run.

### YOLOv8s 640x640 Official Test Split Evaluation

- Precision: 0.865
- Recall: 0.838
- mAP50: 0.876
- mAP50-95: 0.601

This is the official test split evaluation for the retrained YOLOv8s model.

### Strict Same-Split YOLOv8n vs YOLOv8s Comparison

On the official test split, YOLOv8s improves over YOLOv8n by:

- Precision: +0.024
- Recall: +0.022
- mAP50: +0.017
- mAP50-95: +0.019

The comparison uses the same dataset config, test split, and image size.

### Image Size Ablation

Image size ablation was completed as a validation-only experiment using the YOLOv8n 640 50 epochs custom weight on the official test split. No training was run, and this does not compare separately trained 416/512/640 models.

| Image Size | Precision | Recall | mAP50 | mAP50-95 |
| ---: | ---: | ---: | ---: | ---: |
| 416 | 0.834 | 0.792 | 0.855 | 0.576 |
| 512 | 0.825 | 0.830 | 0.863 | 0.582 |
| 640 | 0.841 | 0.816 | 0.859 | 0.582 |

512 slightly leads on mAP50/mAP50-95, while 640 has the highest precision. The differences between 512 and 640 are small, so deployment choice should consider speed and latency as well as accuracy.

Reference: [Image size ablation](image_size_ablation.md)

### YOLOv8m 640x640 Model Scaling Experiment

YOLOv8m training and official test split evaluation were completed as a model-scaling experiment.

Training validation:

- Precision: 0.837
- Recall: 0.817
- mAP50: 0.870
- mAP50-95: 0.594

Official test:

- Precision: 0.852
- Recall: 0.820
- mAP50: 0.872
- mAP50-95: 0.594

YOLOv8m did not outperform YOLOv8s on the official test split. Compared with YOLOv8s, YOLOv8m changed by:

- Precision: -0.013
- Recall: -0.018
- mAP50: -0.004
- mAP50-95: -0.007

YOLOv8m should therefore be treated as a model-scaling experiment, not the default deployment model. YOLOv8m PyTorch speed benchmark and ONNX Runtime benchmark have not yet been run.

References:

- [YOLOv8m training summary](experiments/yolov8m_640_50epochs/summary.md)
- [YOLOv8m official test summary](evaluation/yolov8m_640_50epochs_official/summary.md)

### Model Family Selection

The model family comparison shows that YOLOv8s remains the recommended default model and the best current accuracy/latency trade-off. YOLOv8n remains the fastest measured model and is still useful when latency matters most. YOLOv8m is larger and did not improve official-test mAP50-95 over YOLOv8s, so it is not recommended as the default model based on current results.

Reference: [YOLOv8 model family comparison](model_family_comparison.md)

### Colab T4 Inference Speed Benchmark

Inference speed benchmark was completed on Google Colab Tesla T4 with CUDA device `cuda:0`, image size 640, 100 measured images, and 10 warmup images.

- YOLOv8n 640 50 epochs: 11.562 ms/image, 86.49 FPS.
- YOLOv8s 640 50 epochs retrain: 15.985 ms/image, 62.56 FPS.
- YOLOv8s latency ratio vs YOLOv8n: 1.383x.

Reference: [Inference speed benchmark](inference_speed_benchmark.md)

### ONNX Runtime Benchmark / Check

ONNX Runtime benchmark/check was completed on Google Colab Tesla T4. It used ONNX Runtime 1.26.0 with provider `CUDAExecutionProvider,CPUExecutionProvider`, image size 640, 100 measured images, and 10 warmup images.

- YOLOv8n ONNX Runtime: 10.994 ms/image, 90.96 FPS.
- YOLOv8s ONNX Runtime: 13.657 ms/image, 73.22 FPS.
- Output check: shape `[[1, 10, 8400]]`, finite `True`, non-empty `True`.
- No ONNX files are committed.
- No ONNX Runtime mAP/NMS evaluation was run.

Reference: [ONNX Runtime benchmark](onnx_runtime_benchmark.md)

## 4. Inference and Demo Work

The project includes selected image inference examples and a 50-sample inference analysis based on existing prediction outputs. It also includes video demo documentation and selected key frames for qualitative review.

Demo work includes:

- selected image inference examples
- 50-sample inference analysis
- video demo documentation and key frames
- Streamlit image detection demo
- sample image selector
- upload mode
- FastAPI real `/predict` image inference endpoint
- detection table
- CSV download
- friendly error handling

The Streamlit demo is intended for local qualitative inspection, not official metric evaluation.

## 5. Error Analysis

The project includes systematic qualitative error analysis and supporting review materials:

- qualitative error case gallery
- per-class failure analysis
- confusion matrix interpretation
- error taxonomy
- hard examples list
- confidence threshold analysis

Main observed risks and qualitative patterns:

- `Car` / `Truck` / `mini-truck` confusion
- crowded scenes
- small objects
- false positives and false negatives
- duplicate boxes

These analyses are qualitative and should be interpreted together with official validation metrics.

## 6. Engineering and Tooling

Engineering utilities include:

- `configs/default.yaml`
- `configs/tracking.yaml`
- `configs/analytics.yaml`
- setup check script: `src/check_setup.py`
- batch prediction CLI: `src/batch_predict.py`
- Makefile commands for checks and common workflows
- GitHub Actions syntax check
- pytest test scaffold
- dependency split:
  - `requirements.txt`
  - `requirements-dev.txt`
  - `requirements-api.txt`

The batch prediction CLI is designed to write generated outputs under `local_outputs/`, which is ignored by Git.

### Video Analytics MVP

`v0.8.0-video-analytics-mvp` adds pure-Python video analytics MVP contracts and core testable logic. It includes:

- geometry utilities
- line counter
- ROI counter
- event rules
- track and analytics result writers
- Video Analysis Center skeleton
- synthetic unit tests for the video analytics core

`v0.8.1-video-analysis-synthetic-pipeline` adds a synthetic end-to-end video analysis pipeline. It validates that tracks can flow through counting, ROI, events, result writers, and the Video Analysis Center without using real video or YOLO inference.

This MVP does not include real ByteTrack/DeepSORT integration, `track_video.py` runtime integration, Streamlit video result pages, FastAPI video jobs, database integration, or real video benchmarks.

Reference: [Video analytics MVP](video_analytics_mvp.md)

## 7. Deployment and Serving Preparation

Deployment and serving preparation includes:

- local deployment guide
- model loading strategy
- FastAPI service with real `/predict` image inference endpoint
- API usage documentation
- Dockerfile without weights
- `.dockerignore`

Model weights are mounted or provided locally. They are not committed to Git.

Important limitations:

- FastAPI `/predict` accepts multipart image upload and returns JSON detections.
- The YOLO model is lazy-loaded on the first prediction request.
- No model is loaded at API import time.
- Uploaded images and prediction outputs are not saved to the repository.
- Docker scaffold has not been claimed as production deployment.
- Docker image is designed not to include model weights or the full dataset.

## 8. Safety and Reproducibility

Repository safety rules:

- weights are local-only
- full dataset splits are local-only
- generated outputs are ignored
- large videos are ignored
- `danger-check` and `list-large-docs` are used before commits

GitHub tracks code, docs, configs, summaries, and selected lightweight demo assets only. It does not track model weights, full dataset splits, local generated outputs, local videos, or large video artifacts.

## 9. Current Limitations

- No production API inference endpoint yet.
- YOLOv8m PyTorch speed benchmark has not yet been run.
- YOLOv8m ONNX Runtime benchmark has not yet been run.
- No ONNX Runtime mAP/NMS evaluation.
- No real Docker build/run validation yet.
- Model weights, ONNX files, and full dataset split folders are intentionally not committed.
- v0.8.0 video analytics is a pure-Python MVP core and does not yet include real tracker integration or a video UI/API workflow.

## 10. Recommended Next Steps

- Run YOLOv8m PyTorch speed benchmark only if model-family latency completeness is needed.
- Run YOLOv8m ONNX Runtime benchmark only if deployment completeness is needed.
- Add ONNX Runtime mAP/NMS evaluation only if a separate evaluation protocol is defined.
- Continue video analytics with a `track_video.py` skeleton or real tracker adapter before adding Streamlit/FastAPI video workflows.
- Prepare presentation slides or portfolio summary.

## Related Documents

- [README](../README.md)
- [Project task board](project_task_board.md)
- [Model card](model_card.md)
- [Dataset card](dataset_card.md)
- [Model weight policy](model_weight_policy.md)
- [Project roadmap](project_roadmap.md)
- [Report assets index](report_assets.md)
- [Per-class failure analysis](per_class_failure_analysis.md)
- [Confusion matrix interpretation](confusion_matrix_interpretation.md)
- [Error taxonomy](error_taxonomy.md)
- [Hard examples](hard_examples.md)
- [Threshold analysis](threshold_analysis.md)
- [Streamlit demo guide](streamlit_demo.md)
- [Model loading strategy](model_loading_strategy.md)
- [Local deployment guide](deployment_guide.md)
- [Docker deployment guide](docker_deployment.md)
- [API usage guide](api_usage.md)
- [ONNX Runtime benchmark](onnx_runtime_benchmark.md)
- [Image size ablation](image_size_ablation.md)
- [YOLOv8 model family comparison](model_family_comparison.md)
- [Video analytics MVP](video_analytics_mvp.md)
- [YOLOv8m training summary](experiments/yolov8m_640_50epochs/summary.md)
- [YOLOv8m official test summary](evaluation/yolov8m_640_50epochs_official/summary.md)
