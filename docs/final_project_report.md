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

`v0.8.2-track-video-skeleton` adds a `track_video.py` skeleton CLI for synthetic detections-to-tracks conversion. It validates the CLI and `tracks.csv` contract without reading real video, running YOLO, or integrating ByteTrack/DeepSORT.

`v0.8.3-real-video-reading-skeleton` adds a video reader skeleton for safe video path validation, metadata extraction, and frame-index construction. It does not yet run YOLO, read frames for inference, or integrate ByteTrack/DeepSORT.

`v0.8.4-video-reader-track-video-integration` connects the video reader skeleton to `track_video.py`. The CLI now supports metadata-only video mode and synthetic detections-to-tracks mode, but still does not run YOLO, perform real tracking, or render tracked video.

`v0.8.5-cli-smoke-docs` documents safe smoke commands for the `track_video.py` skeleton. The commands validate current contracts without committing generated outputs or running real inference/tracking.

`v0.9.0-real-video-detection-tracking-foundation` adds CSV-first `predict_video.py` video detection export and a tracking adapter interface skeleton. It defines the `detections.csv` contract and placeholder ByteTrack/DeepSORT adapters while keeping tests based on fake detections and monkeypatched YOLO.

`v0.9.1-predict-to-track-synthetic-runtime` connects `track_video.py` detections-to-tracks mode to the tracking adapter factory. The synthetic tracker is available through the adapter interface; ByteTrack/DeepSORT remain placeholders.

`v0.9.2-two-command-smoke-flow` documents and tests a two-command smoke flow from `predict_video.py` detections export to `track_video.py` synthetic tracking. It validates the `detections.csv` to `tracks.csv` file-contract chain without real ByteTrack or tracked video rendering.

`v0.9.3-video-analysis-job-skeleton` adds a Video Analysis Center job skeleton that organizes existing `detections.csv` and `tracks.csv` into a run directory. It writes `metadata.json` and `video_analysis_summary.json`, but does not run YOLO, run a tracker, or render tracked video.

`v0.9.4-three-step-video-analysis-job-flow` documents and tests the three-step video analysis job flow from `predict_video.py` to `track_video.py` to the Video Analysis Center. It validates the file-contract chain without real ByteTrack or tracked video rendering.

`v0.9.5-analytics-on-tracks-job` adds analytics execution on existing tracks inside the Video Analysis Center job. Existing `tracks.csv` can now produce `count_events.csv`, `roi_frame_counts.csv`, `events.jsonl`, and an updated `video_analysis_summary.json`; it does not run YOLO, run a real tracker, or render tracked video.

`v0.9.6-four-step-local-flow` documents and tests a four-step local flow from detection export to synthetic tracking to Video Analysis Center analytics. It validates the file-contract chain through analytics artifacts without real ByteTrack or tracked video rendering.

`v0.9.7-four-step-smoke-runner` adds a unified four-step smoke runner. It orchestrates detection export, synthetic tracking, Video Analysis Center job creation, and analytics execution while still using the synthetic tracker and not rendering tracked video.

`v0.9.9-real-local-smoke-result` documents the first real local smoke run. It validates real YOLO detection export, synthetic tracking, and Video Analysis Center artifacts on a local demo video. The run produced `21,988` detections and `34` synthetic tracks. Outputs remain local-only and are not committed.

`v0.10.0-cli-module-invocation-ergonomics` documents and tests module-style CLI invocation for local smoke tools. The recommended local command is `.venv/bin/python -m src.run_video_analysis_smoke ...`; `src.smoke_preflight` is also callable with `.venv/bin/python -m src.smoke_preflight ...`.

`v0.10.1` through `v0.10.3` captured local analytics tuning lessons: line, ROI, and event-rule settings need visual review against real track geometry before counts are meaningful. The one-off tuning and overlay helpers have been pruned; the retained guidance is now part of the main analytics, Video Analysis Center, tracked rendering, and Streamlit demo documentation.

`v0.10.2-analytics-only-rerun-with-suggested-config` adds analytics-only rerun support. It applies suggested analytics config to existing `detections.csv` and `tracks.csv` without rerunning YOLO or tracking, producing fresh Video Analysis Center artifacts.

`v0.10.4-tracked-video-rendering` adds tracked video rendering from existing tracks. It renders local preview videos with bbox, track labels, line overlays, and ROI overlays without rerunning YOLO.

`v0.11.0-bytetrack-discovery-spike` adds a ByteTrack integration discovery helper and plan. It does not run real ByteTrack yet; it documents candidate integration paths and validates how Ultralytics `model.track`-style outputs can be normalized into the existing `tracks.csv` contract.

`v0.11.1-ultralytics-bytetrack-short-video-spike` adds a short-video Ultralytics `model.track(..., tracker="bytetrack.yaml")` spike tool that writes ByteTrack-style `tracks.csv` under `/tmp` and can reuse the tracked video renderer for preview output. The first local attempt was blocked by missing `lap`, so no real ByteTrack tracks are committed or claimed as validated.

`v0.11.2-lap-dependency-and-bytetrack-rerun` documents the first successful local ByteTrack short-video spike after installing `lap==0.5.13` into the local `.venv`. The 300-frame run produced `746` ByteTrack track rows, `25` unique tracks, and a local 300-frame ByteTrack tracked preview. Outputs remain local-only under `/tmp` and are not committed.

`v0.11.3-bytetrack-runtime-integration-plan` prepares promotion of the ByteTrack spike into the standard `track_video.py` runtime. It adds a pure-Python runtime contract helper and a formal ByteTrack runtime integration plan. No real YOLO or ByteTrack rerun is performed in this step.

`v0.11.4-track-video-bytetrack-runtime` promotes the ByteTrack spike into the standard `track_video.py` runtime. It supports `.venv/bin/python -m src.track_video --tracker bytetrack ...` and writes real ByteTrack `tracks.csv` to the requested output directory. Local 300-frame validation produced `746` track rows and `25` unique tracks under `/tmp`; outputs are not committed.

This MVP does not include DeepSORT integration, ByteTrack production hardening, full-length tracked video validation, Streamlit video result pages, FastAPI video jobs, database integration, or real video benchmarks.

References:

- [Video analytics MVP](video_analytics_mvp.md)
- [ByteTrack integration plan](bytetrack_integration_plan.md)
- [track_video.py CLI usage](track_video_cli_usage.md)

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
- Docker actual build/run smoke passed locally, including FastAPI, Streamlit,
  and mounted-weight `/predict` checks.
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

- FastAPI image `/predict` exists and the Docker-mounted `/predict` smoke
  passed with a local ignored `best.pt`.
- YOLOv8m PyTorch speed benchmark has not yet been run.
- YOLOv8m ONNX Runtime benchmark has not yet been run.
- No ONNX Runtime mAP/NMS evaluation.
- Docker actual build/run smoke passed locally in `v0.14.4` and `v0.14.5`.
- Model weights, ONNX files, and full dataset split folders are intentionally not committed.
- Real async video execution API, Streamlit job launching, production
  security/observability hardening, real Bad Case collection, and optional
  DeepSORT runtime remain future work.

## 10. Recommended Next Steps

- Run YOLOv8m PyTorch speed benchmark only if model-family latency completeness is needed.
- Run YOLOv8m ONNX Runtime benchmark only if deployment completeness is needed.
- Add ONNX Runtime mAP/NMS evaluation only if a separate evaluation protocol is defined.
- Continue video analytics with YOLO frame inference planning before adding tracker adapters and Streamlit/FastAPI video workflows.
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
## v0.11.5 ByteTrack Pipeline Validation

The project now validates the post-tracking pipeline for standard ByteTrack
output. `src.validate_bytetrack_pipeline` consumes existing YOLO detections and
standard ByteTrack tracks, runs analytics-only rerun, and optionally renders a
tracked preview without rerunning YOLO or rerunning ByteTrack.

Local validation summary:

- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `track_count=25`
- ROI frames observed: `33`
- long-stay events: `24`
- preview readable by cv2: `300` frames, `29.97 FPS`, `1280x720`

Generated CSV, JSON, JSONL, and MP4 outputs stayed under `/tmp` and were not
committed. This validation summary is retained in the main ByteTrack,
video-analytics, CLI, and final-report documentation; the one-off validation
history page has been pruned.

## v0.11.6 Synthetic vs ByteTrack Comparison

The project now includes a synthetic-vs-ByteTrack comparison helper. The local
comparison reported `21988` synthetic rows across `34` tracks versus `746`
ByteTrack rows across `25` tracks and `261` frames with rows.

The key conclusion is that synthetic tracks are appropriate for deterministic
tests and fallback behavior, while ByteTrack tracks should be used for
runtime/demo because they carry real MOT `track_id` semantics. No MOTA/IDF1
claim is made because no ground-truth tracking labels are available.

## v0.12.0 Streamlit Video Demo Page

The project now includes a read-only Streamlit video artifact browser. It can
display existing ByteTrack tracks, Video Analysis Center summaries, analytics
CSV/JSONL previews, tracked preview video playback, and synthetic-vs-ByteTrack
comparison JSON without running YOLO, running ByteTrack, rerunning analytics, or
rendering new videos.

This closes an important demo gap: the local ByteTrack validation artifacts can
now be reviewed through a lightweight UI while generated CSV, JSON, JSONL, MP4,
weights, and source videos remain local-only and uncommitted. See
[Streamlit Video Demo Page](streamlit_video_demo.md).

## v0.13.0 FastAPI Basic Service Acceptance

The project now includes the FastAPI basic service surface required by the
execution manual:

- `GET /health`
- `GET /config`
- `GET /model-status`
- `POST /predict`

The API is intentionally thin. It does not import or load YOLO at app import
time, and `/health`, `/config`, and `/model-status` do not load model weights.
Model loading is isolated in `src/core/model_loader.py` with lazy caching, and
image decoding plus inference are handled in
`src/services/image_inference_service.py`. Uploaded images are decoded in memory
and are not written to the repository.

FastAPI tests use `TestClient`, in-memory images, and monkeypatched services, so
they do not load real weights or run real inference. Video analyze jobs, result
query endpoints, database integration, and Docker validation remain future work.

## v0.13.1 FastAPI Video Job Result Skeleton

`v0.13.1` adds the first FastAPI video workflow surface from the execution
manual:

- `POST /api/videos/analyze`
- `GET /api/videos/jobs/{job_id}`
- `GET /api/videos/jobs/{job_id}/detections`
- `GET /api/videos/jobs/{job_id}/tracks`
- `GET /api/videos/jobs/{job_id}/analytics`
- `GET /api/videos/jobs/{job_id}/events`

This is intentionally a safe skeleton. The API creates an in-memory job record
and can attach that record to an existing VideoAnalysisCenter run directory. The
result endpoints read existing `detections.csv`, `tracks.csv`,
`count_events.csv`, `roi_frame_counts.csv`, `events.jsonl`, and
`video_analysis_summary.json` artifacts. The API does not run YOLO, run
ByteTrack/DeepSORT, execute analytics, render videos, create local outputs, use
a database, or start background workers.

Tests use FastAPI `TestClient` and pytest `tmp_path` artifacts. They verify job
creation, result lookup, missing-artifact errors, row limits, and that video job
endpoints do not import the real prediction, tracking, or rendering modules.

## v0.14.0 Bad Case Schema and Report Foundation

`v0.14.0` adds the Bad Case foundation required by the final execution manual.
The new `docs/bad_cases_schema.md` defines a stable `bad_cases.csv` contract
with required fields for module attribution, case type, expected result, actual
result, root cause, tags, evidence path, and `added_to_eval_set`.

The new `docs/bad_case_report.md` connects that schema to the existing
taxonomy, hard examples, and error case gallery:

- `docs/error_taxonomy.md`
- `docs/hard_examples.md`
- `docs/error_case_gallery/README.md`
- `docs/error_case_gallery/cases.csv`

This reduces the final acceptance gap around Bad Case reporting, but it does
not claim that a full real Bad Case dataset has already been collected. The
current gallery CSV remains a small hand-written documentation sample. Future
work should collect reviewed real cases, add `/api/bad-cases`, link Bad Cases
to evaluation reports, and build a selected regression set.

## v0.14.1 Docker Deployment Static Acceptance

`v0.14.1` aligns Docker and deployment documentation with the final execution
manual's Stage 8 acceptance items. The update documents:

- Docker build command.
- FastAPI Docker run command with `MODEL_PATH` and read-only `local_weights`
  volume mount.
- Streamlit Docker run command with the same mounted-weight policy.
- FastAPI smoke commands for `/health`, `/config`, `/model-status`, `/predict`,
  and the video job skeleton.
- Artifact attach guidance for existing Video Analysis Center runs mounted into
  the container.
- `.dockerignore` exclusions for weights, source videos, dataset splits,
  generated outputs, archives, and large video formats.

This is static acceptance only. No Docker image was built, no Docker container
was run, no YOLO/ByteTrack/analytics/render step was executed, and no generated
CSV, JSON, JSONL, MP4, weights, or source videos were committed. Actual Docker
build/run smoke remains pending manual verification.

## v0.14.2 Final Acceptance Checklist

`v0.14.2` adds `docs/final_acceptance_checklist.md` as the consolidated final
acceptance record for the execution manual's Stage 8 and Chapter 21 acceptance
areas. The checklist summarizes:

- project metadata and version/tag history
- evidence files for dataset, training/evaluation, prediction, tracking,
  analytics, rendering, Streamlit, FastAPI, Bad Case, and Docker/deployment
- test command matrix for docs, API, analytics, and static project checks
- asset-safety checks for weights, local videos, dataset splits, generated
  outputs, and large documentation assets
- manual pending acceptance items
- initial documentation/static acceptance status

This step did not claim actual Docker build/run completion. Docker build,
FastAPI container smoke, Streamlit container smoke, and mounted-weight
container prediction were later closed by `v0.14.4` and `v0.14.5`.

## v0.14.3 Docker Actual Build Smoke Preflight

`v0.14.3` adds `docs/docker_actual_smoke_plan.md` as the preflight record for
the execution manual's actual Docker build/run acceptance items. The current
preflight result is:

- Docker CLI unavailable.
- `docker --version` command not found.
- `docker info` returned `docker_info_exit=127`.
- Current blocker: Docker CLI/daemon unavailable.

No Docker build was run, no Docker container was started, no YOLO/ByteTrack
pipeline was executed, and no generated outputs were created. The smoke plan
documents the exact future build command, FastAPI container smoke, Streamlit
container smoke, mounted-weight `/predict` smoke, success criteria, failure
handling, and go/no-go rules.

## v0.14.4 Docker Actual Build Smoke

`v0.14.4` records the first actual Docker build/run smoke in
`docs/docker_actual_smoke_result.md`.

Observed result:

- Docker CLI available at `/usr/local/bin/docker`.
- Docker version: `29.5.3`.
- `docker info` exit code: `0`.
- Docker Desktop server architecture: `aarch64`.
- Docker image build passed for `yolov8-vehicle-pedestrian:latest`.
- Initial FastAPI container smoke failed because `fastapi` was missing inside
  the built image.
- The Dockerfile now installs `requirements-api.txt` alongside
  `requirements.txt`.
- After rebuilding, FastAPI `/health`, `/config`, `/model-status`, and
  `/api/videos/analyze` passed inside the container.
- Streamlit container smoke passed and returned `HTTP/1.1 200 OK`.
- Mounted-weight `/predict` was skipped because `local_weights/best.pt` was not
  present.

## v0.14.5 Mounted-Weight Container Predict Smoke

`v0.14.5` closes the mounted-weight Docker `/predict` acceptance item.

Observed result:

- Local ignored `local_weights/best.pt` was mounted read-only into the container
  at `/app/local_weights/best.pt`.
- Weight sha256:
  `1eb1360fc3d59cc955384912389ea835e218ba62af72bcf96386e0ea6f34af47`.
- FastAPI `/health`, `/config`, and `/model-status` passed before predict;
  model status showed `exists=true` and `loaded=false`.
- `/predict` returned JSON containing `image_name`, `image_size`,
  `model_path`, `num_detections`, and `detections`.
- The smoke image was a temporary blank `/tmp` image and was not committed.
- Model status after predict showed `exists=true` and `loaded=true`.
- No weights, temporary image, response JSON, Docker image layers, or generated
  outputs were committed.

Final Docker status:

- Docker actual smoke: passed for local acceptance.
- Production hardening, real async video execution, and optional DeepSORT remain
  future work.

No Docker image layers, model weights, videos, CSV, JSON, JSONL, MP4,
`runs`, `local_outputs`, or `/tmp` outputs were committed. Final local/Docker
acceptance is Go, subject to normal environment-specific deployment checks.

## v0.14.6 Final Documentation Consistency Pass

`v0.14.6` reconciles final documentation after the `v0.14.5` Docker actual
smoke closure. It updates README, final report, final checklist, task board,
and deployment documentation so they consistently state that Docker image
build, FastAPI container smoke, Streamlit container smoke, and mounted-weight
container `/predict` all passed locally. Future work is limited to production
hardening, real async video execution, real Bad Case collection, optional
DeepSORT runtime, and optional full-length production validation.
