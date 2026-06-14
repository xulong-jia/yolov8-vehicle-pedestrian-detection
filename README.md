# YOLOv8 Vehicle and Pedestrian Detection

## Overview

This project is a YOLOv8-based vehicle and pedestrian detection system. It covers the full workflow from dataset preparation and label validation to model experiments, image/video inference demos, qualitative error analysis, local application demos, and deployment scaffolding.

Current project scope includes:

- dataset preparation
- label validation and cleaning
- YOLOv8n / YOLOv8s experiments
- image inference and video inference demo
- qualitative error analysis
- Streamlit image detection demo
- batch prediction CLI
- FastAPI scaffold
- Docker scaffold
- project documentation and safety policy

## Key Features

### Dataset and Label Validation

- Roboflow YOLOv8 dataset format.
- Six target classes:
  - `Bus`
  - `Car`
  - `Motorcycle`
  - `Person`
  - `Truck`
  - `mini-truck`
- Dataset config: `dataset/data.yaml`.
- Label quality checks and dataset analysis utilities.
- Invalid polygon-like labels were converted or fixed during dataset cleaning.
- Full dataset split folders are local-only and not tracked in Git.

### Training and Evaluation

Completed experiments and recorded results:

1. YOLOv8n 416x416 10 epochs smoke test
   - mAP50: 0.797
   - mAP50-95: 0.511

2. YOLOv8n 640x640 50 epochs baseline
   - Precision: 0.81981
   - Recall: 0.82768
   - mAP50: 0.86422
   - mAP50-95: 0.59102

3. YOLOv8n official test split evaluation
   - Precision: 0.841
   - Recall: 0.816
   - mAP50: 0.859
   - mAP50-95: 0.582

4. YOLOv8s 640x640 50 epochs supplementary validation result
   - Precision: 0.839
   - Recall: 0.841
   - mAP50: 0.877
   - mAP50-95: 0.604
   - This is a validation split supplementary result, not a strict same-split test comparison.

### Inference and Demo

- Single-image prediction examples.
- 50-sample image inference analysis.
- Video inference demo with selected key frames.
- Local Streamlit image detection demo.
- Sample image selector from the error case gallery.
- Image upload workflow.
- Detection table with class, confidence, and bounding box coordinates.
- Downloadable detection CSV.
- Friendly error messages for missing weights, invalid images, model loading failures, and inference failures.

### Error Analysis

- Systematic qualitative error analysis.
- Error case gallery with representative prediction images.
- Error taxonomy for consistent review labels.
- Hard examples list for future review.
- Confidence threshold analysis.
- Per-class failure analysis.
- Confusion matrix interpretation.

### Engineering Utilities

- `configs/default.yaml` for default paths and inference settings.
- `src/check_setup.py` for local setup checks.
- `src/batch_predict.py` for batch image prediction CSV generation.
- `Makefile` targets for common checks and commands.
- GitHub Actions Python syntax check.
- Pytest test scaffold for utility functions.
- `requirements-dev.txt` for test/dev dependencies.
- `requirements-api.txt` for FastAPI scaffold dependencies.

### Deployment and Serving

- Local deployment guide.
- Model loading strategy.
- FastAPI scaffold with health/config/model-status endpoints.
- API usage documentation.
- Dockerfile without model weights.
- `.dockerignore` excluding weights, dataset splits, local outputs, runs, and videos.
- Docker image is designed to exclude model weights and the full dataset.

## Project Structure

```text
yolov8-vehicle-pedestrian-detection/
  app.py
  configs/
    default.yaml
  dataset/
    data.yaml
    train/                  # local-only, ignored
    valid/                  # local-only, ignored
    test/                   # local-only, ignored
  docs/
    colab_runs/
    error_case_gallery/
    predictions/
    video_demos/
    api_usage.md
    deployment_guide.md
    docker_deployment.md
    model_loading_strategy.md
    project_task_board.md
  local_outputs/            # generated local outputs, ignored
  local_weights/            # local model weights, ignored
  src/
    analyze_dataset.py
    api.py
    batch_predict.py
    check_setup.py
    evaluate.py
    predict_image.py
    predict_video.py
    train.py
    visualize_dataset.py
  tests/
    __init__.py
    test_batch_predict.py
    test_check_setup.py
  .dockerignore
  .gitignore
  Dockerfile
  Makefile
  README.md
  requirements.txt
  requirements-api.txt
  requirements-dev.txt
```

## Quick Start

### 1. Install Runtime Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Model Weights

Model weights are not included in GitHub. Place the YOLOv8n baseline weight locally at:

```text
local_weights/yolov8n_640_50epochs/best.pt
```

### 3. Run Setup Check

```bash
python3 src/check_setup.py
```

### 4. Run Streamlit Demo

```bash
streamlit run app.py
```

or:

```bash
make streamlit
```

### 5. Run Batch Prediction CLI

Example command:

```bash
python3 src/batch_predict.py --model local_weights/yolov8n_640_50epochs/best.pt --source docs/error_case_gallery/images --output-csv local_outputs/batch_predictions/detections.csv
```

Notes:

- `local_outputs/` is ignored by Git.
- Large batch inference may benefit from GPU.
- Small local checks can use CPU.

### 6. Run FastAPI Scaffold

Install API dependencies:

```bash
pip install -r requirements-api.txt
```

Run locally:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Current API scope:

- `/health`, `/config`, and `/model-status` are available scaffold endpoints.
- `/predict` is a placeholder and does not run real inference.
- No model is loaded at import time.

### 7. Docker Scaffold

Build example:

```bash
docker build -t yolov8-vehicle-pedestrian-demo .
```

Run example:

```bash
docker run --rm -p 8501:8501 -v /absolute/path/to/best.pt:/models/best.pt:ro yolov8-vehicle-pedestrian-demo
```

Do not copy weights into the Docker image. Mount weights at runtime.

## Makefile Commands

- `make check`: run Python syntax checks for the main app and scripts.
- `make test`: run pytest tests under `tests/`.
- `make api-check`: run syntax check for `src/api.py`.
- `make streamlit`: start the local Streamlit demo.
- `make status`: show short Git status.
- `make danger-check`: check staged files for risky paths.
- `make list-large-docs`: list large files under `docs/`.

If pytest is not installed:

```bash
pip install -r requirements-dev.txt
```

## Results Summary

| Experiment | Split | Image Size | Epochs | Precision | Recall | mAP50 | mAP50-95 | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| YOLOv8n smoke test | validation | 416 | 10 | 0.786 | 0.749 | 0.797 | 0.511 | Quick Colab smoke test |
| YOLOv8n 640 baseline validation | validation | 640 | 50 | 0.81981 | 0.82768 | 0.86422 | 0.59102 | Main lightweight baseline |
| YOLOv8n official test | test | 640 | 50 | 0.841 | 0.816 | 0.859 | 0.582 | Official test split evaluation |
| YOLOv8s validation supplementary | validation | 640 | 50 | 0.839 | 0.841 | 0.877 | 0.604 | Supplementary result, not same-split benchmark |

## Timeline by Date

### 2026-06-11

- Initialized project structure.
- Added dataset YAML.
- Validated and cleaned labels.
- Added YOLOv8n smoke test results.

### 2026-06-12

- Added YOLOv8n 640 baseline results.
- Cleaned project references.
- Improved model weight path documentation.

### 2026-06-13

- Added image inference and error analysis.
- Added video demo documentation and key frames.
- Added YOLOv8s supplementary experiment summary.
- Added experiment comparison.
- Added error case gallery.
- Added Streamlit demo.
- Added project task board and governance docs.

### 2026-06-14

- Added P0/P1/P2 engineering documentation.
- Added Streamlit CSV and sample image improvements.
- Added error taxonomy, hard examples, and threshold analysis.
- Added config file, setup check, and batch prediction CLI.
- Added unit test scaffold and dependency split.
- Added model loading strategy and local deployment guide.
- Added Docker scaffold without model weights.
- Added FastAPI scaffold and API documentation.

## Documentation Index

- [Model card](docs/model_card.md)
- [Dataset card](docs/dataset_card.md)
- [Model weight policy](docs/model_weight_policy.md)
- [Project roadmap](docs/project_roadmap.md)
- [Report assets index](docs/report_assets.md)
- [Per-class failure analysis](docs/per_class_failure_analysis.md)
- [Confusion matrix interpretation](docs/confusion_matrix_interpretation.md)
- [Error taxonomy](docs/error_taxonomy.md)
- [Hard examples](docs/hard_examples.md)
- [Threshold analysis](docs/threshold_analysis.md)
- [Streamlit demo guide](docs/streamlit_demo.md)
- [Model loading strategy](docs/model_loading_strategy.md)
- [Local deployment guide](docs/deployment_guide.md)
- [Docker deployment guide](docs/docker_deployment.md)
- [API usage guide](docs/api_usage.md)
- [Project task board](docs/project_task_board.md)

## Safety and Git Policy

Do not commit:

- `local_weights/`
- `*.pt`
- `*.pth`
- `*.onnx`
- `dataset/train/`
- `dataset/valid/`
- `dataset/test/`
- `runs/`
- `local_outputs/`
- `local_videos/`
- `docs/video_demos/*.avi` or other large videos
- `.venv/`

Policy:

- Model weights are local-only.
- Full dataset splits are local-only.
- Generated outputs are local-only.
- GitHub contains code, docs, configs, summaries, and selected lightweight demo assets only.

## Current Limitations

- FastAPI `/predict` is currently a placeholder.
- Docker scaffold has not been built or deployed as a verified production image.
- YOLOv8s result is a supplementary validation result, not a strict same-split test benchmark.
- Full model weights are not included in the repository.
- Full dataset split folders are not included in the repository.

## Next Steps

- Implement a real FastAPI image inference endpoint.
- Add API tests.
- Add README badges if needed.
- Add a final project report.
- Optionally run GPU-based benchmarks for API or video inference.
