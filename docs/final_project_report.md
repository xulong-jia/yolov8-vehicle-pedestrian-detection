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
- No inference speed benchmark yet.
- No image size ablation yet.
- No YOLOv8m experiment yet.
- No ONNX export yet.
- No real Docker build/run validation yet.
- Model weights and full dataset split folders are intentionally not committed.

## 10. Recommended Next Steps

- Add speed benchmark.
- Run image size ablation if GPU resources are available.
- Run YOLOv8m experiment if compute budget and tracking time are available.
- Add ONNX Runtime check if ONNX export is performed locally.
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
