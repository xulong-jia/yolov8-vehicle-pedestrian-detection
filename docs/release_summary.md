# Release Summary

## Release Identity

- Original final release: v1.0.0-final-release-summary
- Current latest documented state: v1.4.0-artifact-download-endpoints
- Based on original final tag: v0.14.6-final-doc-consistency-pass
- Project name: YOLOv8 Vehicle and Pedestrian Detection System
- Repository: yolov8-vehicle-pedestrian-detection
- Final status: Go for final local/Docker acceptance, subject to normal environment-specific deployment checks

## Post-Final Enhancements

After the original `v1.0.0-final-release-summary`, the repository added five
bounded enhancements:

- `v1.1.0-async-video-job`: FastAPI async video job execution and Streamlit
  Video Job Launcher.
- `v1.2.0-sqlite-video-job-index`: SQLite-backed video job metadata index under
  `local_outputs/api_video_jobs/video_jobs.sqlite3`.
- `v1.3.0-badcase-gt-eval-scaffold`: Bad Case metadata collection plus GT
  evaluation scaffold.
- `v1.3.2-sqlite-job-restart-smoke`: real local FastAPI process restart smoke
  for the SQLite video job metadata index, using attach-mode fake artifacts.
- `v1.4.0-artifact-download-endpoints`: safe FastAPI artifact download
  endpoints for files already registered in a job's `artifact_paths`.

The SQLite index is unit-tested and has been verified with a real local FastAPI
process restart smoke. Docker actual smoke was completed for the v0.14/v1.0 API
surface and has not yet been rerun for all v1.1-v1.4 API additions.

## What Is Delivered

- YOLOv8 image prediction
- YOLOv8 video prediction
- ByteTrack tracking runtime
- `tracks.csv` export
- tracked video rendering
- line counter
- ROI counter
- event rules
- VideoAnalysisCenter
- Streamlit local demo
- FastAPI basic endpoints
- FastAPI async video execution API
- SQLite-backed video job/result metadata index
- SQLite job metadata restart smoke result
- Bad Case schema/report foundation and metadata collection scaffold
- GT evaluation scaffold for tracking/counting/ROI/event artifacts
- FastAPI artifact download endpoints for registered video job artifacts
- Docker build/run smoke
- mounted-weight Docker `/predict` smoke
- final acceptance checklist

## Model and Dataset Summary

- Classes: Bus, Car, Motorcycle, Person, Truck, mini-truck
- YOLOv8s is selected as the balanced final recommendation.
- YOLOv8n is the fastest measured model.
- YOLOv8m experiment results are documented; YOLOv8m is not the default recommendation.
- Model weights are local-only and not committed.

## API Summary

Delivered endpoints:

- `GET /health`
- `GET /config`
- `GET /model-status`
- `POST /predict`
- `POST /api/videos/analyze`
- `GET /api/videos/jobs/{job_id}`
- `GET /api/videos/jobs/{job_id}/detections`
- `GET /api/videos/jobs/{job_id}/tracks`
- `GET /api/videos/jobs/{job_id}/analytics`
- `GET /api/videos/jobs/{job_id}/events`
- `GET /api/videos/jobs/{job_id}/artifacts/{artifact_name}/download`

`/predict` lazy-loads the model on first use. The video job/result API can
launch the existing four-step local video analysis flow, persist job metadata in
SQLite, and query status/results across service restarts. The SQLite index lives
under `local_outputs/api_video_jobs/video_jobs.sqlite3` and stores metadata only,
not artifact file contents. Artifact downloads stream files that are already
registered in job metadata; arbitrary path downloads are not supported.

## Bad Case and Evaluation Scaffold Summary

- `POST /api/bad-cases` records lightweight Bad Case metadata.
- `GET /api/bad-cases` lists collected Bad Case metadata.
- Default local collection paths are under `local_outputs/bad_cases/`.
- The evaluation scaffold can compare prediction CSV/JSONL artifacts against
  small reviewed GT templates for counting, ROI, events, and tracking
  engineering metrics.
- GT templates are documented in [Video Analytics GT Templates](evaluation/gt_templates.md).
- No full reviewed GT dataset or large generated evaluation output is committed.

## Docker Summary

- Docker build passed.
- FastAPI container smoke passed.
- Streamlit container smoke passed.
- Mounted-weight `/predict` passed.
- `best.pt` was mounted read-only from `local_weights/best.pt`.
- Docker image/layers are not committed.
- `local_weights/best.pt` is ignored and remains local-only.
- Result details: [Docker Actual Smoke Result](docker_actual_smoke_result.md)

## Validation Summary

- v1.0 release-doc safe pytest matrix: 300 passed, 1 warning.
- v1.3 scaffold safe pytest matrix: 337 passed, 1 warning.
- `make check`: passed.
- `make api-check`: passed.
- `make danger-check`: passed.
- `make list-large-docs`: only known demo AVI.
- Docker docs / acceptance tests passed.
- Docker Actual Smoke Passed.

## Asset Safety

- No `.pt` files committed.
- No videos committed except the known retained docs demo AVI.
- No `runs/` or `local_outputs/` committed.
- No `dataset/train`, `dataset/valid`, or `dataset/test` split committed.
- Docker image/layers are not committed.
- `local_weights` and local videos remain ignored/local.

## Known Limitations / Future Work

- reviewed real Bad Case labeling and curated GT dataset creation
- full GT-based tracking/counting/ROI/event evaluation on reviewed labels
- optional DeepSORT runtime
- production hardening/security/observability
- optional full-length production validation

## Suggested Evaluator Walkthrough

1. [README](../README.md)
2. [Final Project Report](final_project_report.md)
3. [Final Acceptance Checklist](final_acceptance_checklist.md)
4. [Docker Actual Smoke Result](docker_actual_smoke_result.md)
5. [API Usage](api_usage.md)
6. [Bad Case Report](bad_case_report.md)
7. [Video Analytics MVP](video_analytics_mvp.md)

## Final Recommendation

This repository is ready for final local/Docker acceptance review.

Do not commit `local_weights/best.pt` or generated artifacts.
