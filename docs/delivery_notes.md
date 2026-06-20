# Delivery Notes

## Delivery Package Contents

- source code
- tests
- docs
- Dockerfile
- ignored local assets policy

## What Is Not Included

- model weights
- raw datasets
- local videos
- generated runs
- Docker image
- local outputs

## How to Prepare Local Weights

Put `best.pt` at `local_weights/best.pt`. Do not git add it. It is ignored.

Example:

```bash
mkdir -p local_weights
cp /path/to/best.pt local_weights/best.pt
```

## How to Run Locally

Streamlit:

```bash
streamlit run app.py
```

FastAPI:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## How to Run Docker

Build:

```bash
docker build -t yolov8-vehicle-pedestrian:latest .
```

Run FastAPI:

```bash
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Run Streamlit:

```bash
docker run --rm -p 8501:8501 \
  -e MODEL_PATH=/app/local_weights/best.pt \
  -v "$PWD/local_weights:/app/local_weights:ro" \
  yolov8-vehicle-pedestrian:latest \
  streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Mounted `/predict` curl:

```bash
curl -X POST "http://localhost:8000/predict?conf=0.25&imgsz=640&device=cpu" \
  -F "file=@sample.jpg"
```

See [Docker Deployment](docker_deployment.md) and
[Docker Actual Smoke Result](docker_actual_smoke_result.md).

## How to Run Tests

Documentation and acceptance checks:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache .venv/bin/python -m pytest tests/test_release_summary_docs.py tests/test_final_acceptance_checklist.py tests/test_docker_deployment_docs.py tests/test_docker_actual_smoke_result_docs.py -q
```

Full safe pytest matrix:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache .venv/bin/python -m pytest tests/test_geometry.py tests/test_line_counter.py tests/test_roi_counter.py tests/test_event_rules.py tests/test_track_writer.py tests/test_video_analysis_center.py tests/test_synthetic_video_analysis_pipeline.py tests/test_track_video.py tests/test_video_reader.py tests/test_predict_video.py tests/test_tracking_adapters.py tests/test_predict_to_track_smoke_flow.py tests/test_video_analysis_job.py tests/test_three_step_video_analysis_job_flow.py tests/test_four_step_video_analysis_flow.py tests/test_run_video_analysis_smoke.py tests/test_smoke_preflight.py tests/test_cli_module_invocation.py tests/test_analytics_only_rerun.py tests/test_render_tracked_video.py tests/test_bytetrack_discovery.py tests/test_track_video_bytetrack_spike.py tests/test_bytetrack_runtime_contract.py tests/test_validate_bytetrack_pipeline.py tests/test_video_demo_catalog.py tests/test_api.py tests/test_api_video_jobs.py tests/test_bad_cases_schema_docs.py tests/test_docker_deployment_docs.py tests/test_final_acceptance_checklist.py tests/test_docker_actual_smoke_plan.py tests/test_docker_actual_smoke_result_docs.py tests/test_release_summary_docs.py -q
```

Project checks:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache make check
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache make api-check
make danger-check
make list-large-docs
```

## Release Tags to Inspect

- v0.13.0-fastapi-basic-service-acceptance
- v0.13.1-fastapi-video-job-results-skeleton
- v0.14.0-bad-case-schema-report-foundation
- v0.14.1-docker-deployment-static-acceptance
- v0.14.2-final-acceptance-checklist
- v0.14.3-docker-actual-build-smoke-preflight
- v0.14.4-docker-actual-build-smoke
- v0.14.5-mounted-weight-container-predict-smoke
- v0.14.6-final-doc-consistency-pass

## Final Handoff Status

- Go for final local/Docker acceptance.
- Future work is clearly separated from the delivered package.
