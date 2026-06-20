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
- FastAPI real image prediction endpoint
- Docker scaffold
- pure-Python video analytics MVP contracts and core testable logic
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

4. YOLOv8s 640x640 50 epochs retrain validation
   - Precision: 0.83909
   - Recall: 0.84059
   - mAP50: 0.87705
   - mAP50-95: 0.60405

5. YOLOv8s official test split evaluation
   - Precision: 0.865
   - Recall: 0.838
   - mAP50: 0.876
   - mAP50-95: 0.601

6. Strict same-split YOLOv8n vs YOLOv8s comparison
   - YOLOv8n official test: P 0.841, R 0.816, mAP50 0.859, mAP50-95 0.582
   - YOLOv8s official test: P 0.865, R 0.838, mAP50 0.876, mAP50-95 0.601
   - Delta: Precision +0.024, Recall +0.022, mAP50 +0.017, mAP50-95 +0.019

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
- FastAPI service with health/config/model-status endpoints and a real `/predict` image inference endpoint.
- API usage documentation.
- Dockerfile without model weights.
- `.dockerignore` excluding weights, dataset splits, local outputs, runs, and videos.
- Docker image is designed to exclude model weights and the full dataset.

### Video Analytics MVP

`v0.8.0-video-analytics-mvp` adds pure-Python video analytics MVP contracts and core testable logic. It includes geometry utilities, line counter, ROI counter, event rules, result writers, and a Video Analysis Center skeleton.

`v0.8.1-video-analysis-synthetic-pipeline` adds a synthetic end-to-end video analysis pipeline. It validates that tracks can flow through counting, ROI, events, result writers, and the Video Analysis Center without using real video or YOLO inference.

`v0.8.2-track-video-skeleton` adds a `track_video.py` skeleton CLI for synthetic detections-to-tracks conversion. It validates the CLI and `tracks.csv` contract without reading real video, running YOLO, or integrating ByteTrack/DeepSORT.

`v0.8.3-real-video-reading-skeleton` adds a video reader skeleton for safe video path validation, metadata extraction, and frame-index construction. It does not yet run YOLO, read frames for inference, or integrate ByteTrack/DeepSORT.

`v0.8.4-video-reader-track-video-integration` connects the video reader skeleton to `track_video.py`. The CLI now supports metadata-only video mode and synthetic detections-to-tracks mode, but still does not run YOLO, perform real tracking, or render tracked video.

`v0.8.5-cli-smoke-docs` documents safe smoke commands for the skeleton CLI. See [track_video.py CLI usage](docs/track_video_cli_usage.md) for synthetic detections-to-tracks mode and metadata-only video mode. The CLI remains a skeleton and does not run YOLO, ByteTrack/DeepSORT, or real tracking.

`v0.9.0-real-video-detection-tracking-foundation` adds CSV-first `predict_video.py` video detection export and a tracking adapter interface skeleton. It defines the `detections.csv` contract and placeholder ByteTrack/DeepSORT adapters, but does not yet integrate real tracker dependencies, run full `track_video.py` real tracking, or render tracked video.

`v0.9.1-predict-to-track-synthetic-runtime` connects `track_video.py` detections-to-tracks mode to the tracking adapter factory. The synthetic tracker is available through the adapter interface; ByteTrack/DeepSORT remain placeholders. See [track_video.py CLI usage](docs/track_video_cli_usage.md) and [Video analytics MVP](docs/video_analytics_mvp.md).

`v0.9.2-two-command-smoke-flow` documents and tests a two-command smoke flow from `predict_video.py` detections export to `track_video.py` synthetic tracking. It validates the file-contract chain without real ByteTrack or tracked video rendering. See [track_video.py CLI usage](docs/track_video_cli_usage.md) and [Video analytics MVP](docs/video_analytics_mvp.md).

`v0.9.3-video-analysis-job-skeleton` adds a Video Analysis Center job skeleton that organizes existing `detections.csv` and `tracks.csv` into a run directory. It writes `metadata.json` and `video_analysis_summary.json`, but does not run YOLO, run a tracker, or render tracked video. See [Video analytics MVP](docs/video_analytics_mvp.md).

`v0.9.4-three-step-video-analysis-job-flow` documents and tests the three-step video analysis job flow from `predict_video.py` to `track_video.py` to the Video Analysis Center. It validates the file-contract chain without real ByteTrack or tracked video rendering. See [track_video.py CLI usage](docs/track_video_cli_usage.md) and [Video analytics MVP](docs/video_analytics_mvp.md).

`v0.9.5-analytics-on-tracks-job` adds analytics execution on existing tracks inside the Video Analysis Center job. Existing `tracks.csv` can now produce `count_events.csv`, `roi_frame_counts.csv`, `events.jsonl`, and an updated `video_analysis_summary.json`; it does not run YOLO, run a real tracker, or render tracked video. See [track_video.py CLI usage](docs/track_video_cli_usage.md) and [Video analytics MVP](docs/video_analytics_mvp.md).

`v0.9.6-four-step-local-flow` documents and tests a four-step local flow from detection export to synthetic tracking to Video Analysis Center analytics. It validates the file-contract chain through analytics artifacts without real ByteTrack or tracked video rendering. See [track_video.py CLI usage](docs/track_video_cli_usage.md) and [Video analytics MVP](docs/video_analytics_mvp.md).

`v0.9.7-four-step-smoke-runner` adds a unified four-step smoke runner. It orchestrates detection export, synthetic tracking, Video Analysis Center job creation, and analytics execution while still using the synthetic tracker and not rendering tracked video. See [track_video.py CLI usage](docs/track_video_cli_usage.md).

`v0.9.9-real-local-smoke-result` documents the first real local smoke run. It validates real YOLO detection export, synthetic tracking, and Video Analysis Center artifacts on a local demo video, producing `21,988` detections and `34` synthetic tracks. Outputs remain local-only and are not committed. The retained summary now lives in [Video analytics MVP](docs/video_analytics_mvp.md), [track_video.py CLI usage](docs/track_video_cli_usage.md), and the final report.

`v0.10.0-cli-module-invocation-ergonomics` documents and tests module-style CLI invocation for local smoke tools. Prefer `.venv/bin/python -m src.run_video_analysis_smoke ...` and `.venv/bin/python -m src.smoke_preflight ...` for local runs. See [track_video.py CLI usage](docs/track_video_cli_usage.md).

`v0.10.1` through `v0.10.3` captured local analytics tuning lessons: real smoke tracks need reviewed line, ROI, and event-rule settings before counts are meaningful. The one-off tuning and overlay helpers have been pruned; the useful guidance is folded into the main analytics, Video Analysis Center, rendering, and Streamlit documentation.

`v0.10.4-tracked-video-rendering` adds tracked video rendering from existing tracks. It renders local preview videos with bbox, track labels, line overlays, and ROI overlays without rerunning YOLO. See [Tracked Video Rendering](docs/tracked_video_rendering.md).

`v0.11.0-bytetrack-discovery-spike` adds a ByteTrack integration discovery helper and plan. It does not run real ByteTrack yet; it defines how Ultralytics `model.track`-style outputs can be normalized into the existing `tracks.csv` contract. See [ByteTrack Integration Plan](docs/bytetrack_integration_plan.md).

`v0.11.1-ultralytics-bytetrack-short-video-spike` adds `src/track_video_bytetrack_spike.py`, a max-frame-limited Ultralytics `model.track(..., tracker="bytetrack.yaml")` spike tool for exporting real ByteTrack-style `tracks.csv` under `/tmp`. The local attempt was blocked by missing `lap`; no generated CSV or preview video is committed. See [ByteTrack Integration Plan](docs/bytetrack_integration_plan.md).

`v0.11.2-lap-dependency-and-bytetrack-rerun` documents the first successful local ByteTrack short-video spike after installing `lap==0.5.13` into the local `.venv`. The 300-frame run produced `746` ByteTrack track rows, `25` unique tracks, and a local 300-frame ByteTrack tracked preview. Outputs are local-only under `/tmp` and are not committed. See [ByteTrack Integration Plan](docs/bytetrack_integration_plan.md).

`v0.11.3-bytetrack-runtime-integration-plan` prepares promotion of the ByteTrack spike into the standard `track_video.py` runtime. It adds a pure-Python runtime contract helper and folds the runtime contract into the retained [ByteTrack Integration Plan](docs/bytetrack_integration_plan.md). No real YOLO or ByteTrack rerun is performed in this step.

`v0.11.4-track-video-bytetrack-runtime` promotes the ByteTrack spike into the standard `track_video.py` runtime. It supports `.venv/bin/python -m src.track_video --tracker bytetrack ...` and writes real ByteTrack `tracks.csv` to the requested output directory. Local 300-frame validation produced `746` track rows and `25` unique tracks under `/tmp`; outputs are not committed.

`v0.12.0-streamlit-video-demo-page` adds a read-only Streamlit page for browsing existing ByteTrack, analytics, comparison, and tracked-preview artifacts. It does not run YOLO, run ByteTrack, rerun analytics, or render new videos. See [Streamlit Video Demo Page](docs/streamlit_video_demo.md).

`v0.13.0-fastapi-basic-service-acceptance` completes the FastAPI basic service acceptance surface required by the execution manual: `GET /health`, `GET /config`, `GET /model-status`, and `POST /predict`. The API keeps YOLO loading lazy, routes model loading through `src/core/model_loader.py`, runs image inference through `src/services/image_inference_service.py`, and decodes uploads in memory without writing files. See [API usage guide](docs/api_usage.md).

`v0.13.1-fastapi-video-job-results-skeleton` adds the execution-manual FastAPI video job/result query skeleton: `POST /api/videos/analyze`, `GET /api/videos/jobs/{job_id}`, and result readers for detections, tracks, analytics, and events. The API uses an in-memory job registry and can attach to existing VideoAnalysisCenter run directories; it does not run YOLO, run ByteTrack/DeepSORT, execute analytics, render videos, or write generated artifacts from API calls. See [API usage guide](docs/api_usage.md).

`v0.14.0-bad-case-schema-report-foundation` adds the execution-manual Bad Case foundation. It defines the `bad_cases.csv` schema, adds a Bad Case report, and aligns the existing taxonomy, hard examples, and error gallery with a stable review contract. This does not collect a full real Bad Case dataset and does not add `/api/bad-cases`; those remain future work. See [Bad Case Schema](docs/bad_cases_schema.md) and [Bad Case Report](docs/bad_case_report.md).

`v0.14.1-docker-deployment-static-acceptance` aligns the Docker and deployment documentation with the final execution manual's Stage 8 acceptance items. It documents FastAPI and Streamlit Docker run commands, `MODEL_PATH` weight mounting, large-asset exclusions, and static checks for `Dockerfile` and `.dockerignore`. This is static acceptance only; actual `docker build` / `docker run` smoke remains pending. See [Docker deployment guide](docs/docker_deployment.md) and [Local deployment guide](docs/deployment_guide.md).

`v0.14.2-final-acceptance-checklist` adds the final acceptance checklist for the execution manual's Stage 8 and Chapter 21 acceptance areas. It consolidates evidence files, test commands, version tags, manual follow-up items, asset-safety checks, and a Conditional Go status for documentation/static acceptance. Docker build/run and mounted-weight container prediction were later closed by `v0.14.4` and `v0.14.5`. See [Final Acceptance Checklist](docs/final_acceptance_checklist.md).

`v0.14.3-docker-actual-build-smoke-preflight` adds the Docker actual smoke preflight plan. That preflight recorded Docker CLI/daemon unavailable (`docker_info_exit=127`), so no Docker build/run was executed in that step. See [Docker Actual Smoke Plan](docs/docker_actual_smoke_plan.md).

`v0.14.4-docker-actual-build-smoke` records the first actual Docker build/run smoke. The initial FastAPI container run failed because `fastapi` was missing inside the built image; the Dockerfile now installs `requirements-api.txt`, and the rerun passed `/health`, `/config`, `/model-status`, and `/api/videos/analyze`. Streamlit container smoke returned `HTTP/1.1 200 OK`. Mounted-weight `/predict` remains pending because `local_weights/best.pt` is not present. See [Docker Actual Smoke Result](docs/docker_actual_smoke_result.md).

`v0.14.5-mounted-weight-container-predict-smoke` closes the Docker deployment smoke loop. A local ignored `local_weights/best.pt` was mounted read-only into `/app/local_weights/best.pt`, `/predict` returned JSON with `image_name`, `image_size`, `model_path`, `num_detections`, and `detections`, and the final Docker actual smoke status is `Docker Actual Smoke Passed`. The temporary `/tmp` image and response were not committed. See [Docker Actual Smoke Result](docs/docker_actual_smoke_result.md).

This phase does not include DeepSORT integration, ByteTrack production hardening, Streamlit job launching, real async FastAPI video execution, database integration, full-length tracked video validation, or real video benchmarks.

Details: [Video analytics MVP](docs/video_analytics_mvp.md)

## Project Structure

```text
yolov8-vehicle-pedestrian-detection/
  app.py
  configs/
    analytics.yaml
    default.yaml
    tracking.yaml
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
    video_analytics_mvp.md
  local_outputs/            # generated local outputs, ignored
  local_weights/            # local model weights, ignored
  src/
    analytics/
    core/
    services/
    tracking/
    analyze_dataset.py
    api.py
    batch_predict.py
    check_setup.py
    evaluate.py
    predict_image.py
    predict_video.py
    video_reader.py
    train.py
    visualize_dataset.py
  tests/
    __init__.py
    test_event_rules.py
    test_geometry.py
    test_line_counter.py
    test_roi_counter.py
    test_track_writer.py
    test_video_analysis_center.py
    test_video_reader.py
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

### 6. Run FastAPI Service

Install API dependencies:

```bash
pip install -r requirements-api.txt
```

Run locally:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Current API scope:

- `/health`, `/config`, and `/model-status` are available.
- `/predict` accepts multipart image upload and returns JSON detections.
- YOLO is lazy-loaded from `MODEL_PATH` or the configured default model path on the first prediction request.
- Uploaded images and prediction outputs are not saved to the repository.
- No model is loaded at import time.

### 7. Docker / Deployment Static Acceptance

Build example:

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

Run FastAPI example:

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Run Streamlit example:

```bash
docker run --rm -p 8501:8501 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Do not copy weights into the Docker image. Mount weights read-only at runtime.
`v0.14.1` adds static Docker deployment acceptance; actual Docker build/run
smoke remains pending unless performed explicitly.
`v0.14.3` adds a Docker actual smoke preflight plan; actual build/run remains
blocked until Docker CLI and daemon are available.
`v0.14.5` records the mounted-weight container `/predict` smoke: image build,
FastAPI container smoke, Streamlit container smoke, and mounted-weight
`/predict` all passed. The local model weight was mounted read-only and was not
committed.

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
| YOLOv8s retrain validation | validation | 640 | 50 | 0.83909 | 0.84059 | 0.87705 | 0.60405 | Retrain validation result |
| YOLOv8s official test | test | 640 | 50 | 0.865 | 0.838 | 0.876 | 0.601 | Official test split evaluation |
| YOLOv8m training validation | validation | 640 | 50 | 0.837 | 0.817 | 0.870 | 0.594 | Model-scaling training validation |
| YOLOv8m official test | test | 640 | 50 | 0.852 | 0.820 | 0.872 | 0.594 | Official test split evaluation; below YOLOv8s |

Strict same-split result:

- YOLOv8s improves over YOLOv8n on the official test split by Precision `+0.024`, Recall `+0.022`, mAP50 `+0.017`, and mAP50-95 `+0.019`.

Model family comparison:

- YOLOv8s remains the recommended default model and best current accuracy/latency trade-off.
- YOLOv8m completed training and official test evaluation, but did not outperform YOLOv8s on official test mAP50-95.
- YOLOv8m vs YOLOv8s official test delta: Precision `-0.013`, Recall `-0.018`, mAP50 `-0.004`, mAP50-95 `-0.007`.
- YOLOv8n remains the fastest measured model.
- YOLOv8m PyTorch speed benchmark has not yet been run.
- YOLOv8m ONNX Runtime benchmark has not yet been run.
- Details: [YOLOv8 model family comparison](docs/model_family_comparison.md)

Image size ablation:

- Type: validation-only, no training.
- Model: YOLOv8n 640 50 epochs custom weight.
- Split: official test.
- Image sizes: 416, 512, 640.
- 416: Precision `0.834`, Recall `0.792`, mAP50 `0.855`, mAP50-95 `0.576`.
- 512: Precision `0.825`, Recall `0.830`, mAP50 `0.863`, mAP50-95 `0.582`.
- 640: Precision `0.841`, Recall `0.816`, mAP50 `0.859`, mAP50-95 `0.582`.
- 512 slightly leads on mAP50/mAP50-95; 640 has the highest precision.
- Details: [Image size ablation](docs/image_size_ablation.md)

Inference speed benchmark:

- Hardware: Google Colab Tesla T4, `cuda:0`
- Image size: 640
- Protocol: 100 measured images, 10 warmup images
- YOLOv8n 640 50 epochs: `11.562 ms/image`, `86.49 FPS`
- YOLOv8s 640 50 epochs retrain: `15.985 ms/image`, `62.56 FPS`
- YOLOv8s latency ratio vs YOLOv8n: `1.383x`
- Details: [Inference speed benchmark](docs/inference_speed_benchmark.md)

ONNX Runtime benchmark/check:

- Runtime: ONNX Runtime `1.26.0`
- Provider: `CUDAExecutionProvider,CPUExecutionProvider`
- Hardware: Google Colab Tesla T4
- Image size: 640
- Protocol: 100 measured images, 10 warmup images
- YOLOv8n ONNX Runtime: `10.994 ms/image`, `90.96 FPS`
- YOLOv8s ONNX Runtime: `13.657 ms/image`, `73.22 FPS`
- Output check: shape `[[1, 10, 8400]]`, finite `True`, non-empty `True`
- Details: [ONNX Runtime benchmark](docs/onnx_runtime_benchmark.md)
- No ONNX files are committed, and this is not ONNX Runtime mAP/NMS evaluation.

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
- Implemented real FastAPI `/predict` image inference endpoint.
- Added YOLOv8s retrain validation and official test split evaluation docs.
- Added strict same-split YOLOv8n vs YOLOv8s comparison.
- Added Colab T4 inference speed benchmark.
- Added ONNX Runtime benchmark/check documentation.
- Added YOLOv8n image size ablation documentation.
- Added YOLOv8m training and official test lightweight docs.
- Added YOLOv8 model family comparison.

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
- [Docker Actual Smoke Plan](docs/docker_actual_smoke_plan.md)
- [Docker Actual Smoke Result](docs/docker_actual_smoke_result.md)
- [API usage guide](docs/api_usage.md)
- [YOLOv8s retrain summary](docs/experiments/yolov8s_640_50epochs_retrain/summary.md)
- [YOLOv8s official test summary](docs/evaluation/yolov8s_640_50epochs_official/summary.md)
- [YOLOv8m training summary](docs/experiments/yolov8m_640_50epochs/summary.md)
- [YOLOv8m official test summary](docs/evaluation/yolov8m_640_50epochs_official/summary.md)
- [Strict model comparison](docs/strict_model_comparison.md)
- [YOLOv8 model family comparison](docs/model_family_comparison.md)
- [Image size ablation](docs/image_size_ablation.md)
- [Inference speed benchmark](docs/inference_speed_benchmark.md)
- [ONNX Runtime benchmark](docs/onnx_runtime_benchmark.md)
- [Video analytics MVP](docs/video_analytics_mvp.md)
- [ByteTrack integration plan](docs/bytetrack_integration_plan.md)
- [Tracked Video Rendering](docs/tracked_video_rendering.md)
- [Streamlit Video Demo Page](docs/streamlit_video_demo.md)
- [Bad Case Schema](docs/bad_cases_schema.md)
- [Bad Case Report](docs/bad_case_report.md)
- [Final Acceptance Checklist](docs/final_acceptance_checklist.md)
- [Project task board](docs/project_task_board.md)

## v0.11.5 ByteTrack Pipeline Validation

`v0.11.5` validates that standard `track_video.py --tracker bytetrack` output
can flow into analytics-only rerun and tracked-video rendering without rerunning
YOLO or the tracker. The local 300-frame validation used `746` ByteTrack rows,
`25` unique tracks, and generated local-only analytics artifacts plus a readable
300-frame preview under `/tmp`. The retained summary now lives in
[ByteTrack integration plan](docs/bytetrack_integration_plan.md),
[Video analytics MVP](docs/video_analytics_mvp.md), and the final report.

## v0.11.6 Synthetic vs ByteTrack Comparison

`v0.11.6` compares synthetic and ByteTrack tracking outputs. The comparison
shows that ByteTrack tracks are much sparser but carry real MOT semantics, so
ByteTrack should be used for runtime/demo while synthetic tracking remains the
deterministic fallback/test path.

## v0.12.0 Streamlit Video Demo Page

`v0.12.0` adds a read-only Streamlit video artifact browser. It can display an
existing Video Analysis Center run, ByteTrack `tracks.csv` summaries, analytics
CSV/JSONL previews, an existing tracked preview video, and optional
synthetic-vs-ByteTrack comparison JSON. It does not run YOLO, ByteTrack,
analytics, or video rendering. See
[Streamlit Video Demo Page](docs/streamlit_video_demo.md).

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

- Docker deployment static acceptance is documented, and Docker build/FastAPI/Streamlit container smoke has run locally.
- Docker actual smoke result is documented; mounted-weight `/predict` passed with a local ignored `best.pt`.
- Final acceptance is Go for final local/Docker acceptance, subject to normal environment-specific deployment checks.
- Full real Bad Case collection and `/api/bad-cases` are not implemented yet.
- YOLOv8m PyTorch speed benchmark has not yet been run.
- YOLOv8m ONNX Runtime benchmark has not yet been run.
- No ONNX Runtime mAP/NMS evaluation has been completed.
- Full model weights are not included in the repository.
- ONNX files are not included in the repository.
- Full dataset split folders are not included in the repository.

## Next Steps

- Add README badges if needed.
- Update presentation or portfolio summary materials.
- Optionally run YOLOv8m PyTorch speed benchmark if model-family latency completeness is needed.
- Optionally run YOLOv8m ONNX Runtime benchmark if deployment completeness is needed.
- Optionally run ONNX Runtime mAP/NMS evaluation only if a separate evaluation protocol is defined.
- Continue video analytics after v0.8.5 with YOLO frame inference planning before tracker adapter and Streamlit/FastAPI workflow integration.
