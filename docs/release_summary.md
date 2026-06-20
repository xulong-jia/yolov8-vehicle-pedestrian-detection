# Release Summary

## Release Identity

- Original final release: v1.0.0-final-release-summary
- Current latest documented state: v1.8.5-final-freeze-identity-cleanup
- Based on original final tag: v0.14.6-final-doc-consistency-pass
- Project name: YOLOv8 Vehicle and Pedestrian Detection System
- Repository: yolov8-vehicle-pedestrian-detection
- Final status: Go for final local/Docker acceptance, subject to normal environment-specific deployment checks

## Post-Final Enhancements

After the original `v1.0.0-final-release-summary`, the repository added fifteen
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
- `v1.4.1-docker-v1-api-smoke-refresh`: Docker runtime smoke refresh for the
  v1.1-v1.4 API additions.
- `v1.5.0-api-key-and-structured-logging`: optional API key auth,
  `X-Request-ID` request correlation, and standard-library structured logs.
- `v1.6.0-reviewed-bad-case-collection`: small reviewed Bad Case sample
  collection for detector, tracker, counter, ROI, and event examples.
- `v1.7.0-gt-quantitative-evaluation`: small reviewed GT sample pack and
  scaffold-generated quantitative metrics for counting, ROI, events, and
  tracking engineering metrics.
- `v1.8.0-react-video-job-frontend`: minimal optional Vite + React +
  TypeScript frontend for FastAPI status, video jobs, artifact links, and Bad
  Case metadata.
- `v1.8.1-final-polish-and-frontend-audit-note`: final documentation polish,
  stale status correction, and frontend audit note.
- `v1.8.2-non-technical-user-launcher`: macOS/Windows launcher scripts and a
  plain-language ordinary user guide for starting the existing local app.
- `v1.8.3-non-technical-ui-labels`: localized React UI labels for ordinary
  local users.
- `v1.8.4-react-cors-support`: FastAPI CORS support for local React and
  Streamlit development origins.
- `v1.8.5-final-freeze-identity-cleanup`: final freeze identity, ignore
  policy, and React UI badge cleanup only.

The SQLite index is unit-tested and has been verified with a real local FastAPI
process restart smoke. Docker actual smoke was refreshed for the v1.1-v1.4 API
surface.

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
- Small reviewed Bad Case sample collection
- GT evaluation scaffold for tracking/counting/ROI/event artifacts
- Small reviewed GT quantitative evaluation sample pack
- FastAPI artifact download endpoints for registered video job artifacts
- Docker v1 API smoke refresh
- Optional API key authentication and request/operation structured logs
- Minimal optional React frontend for FastAPI video jobs and Bad Cases
- Final documentation polish and frontend dependency audit note
- macOS/Windows non-technical user launcher scripts
- Local React/Streamlit CORS support for FastAPI development origins
- Final freeze identity/ignore/UI badge cleanup only
- Ordinary user startup guide
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
- `docs/error_case_gallery/reviewed_bad_cases.csv` provides a small reviewed
  metadata sample with 24 cases across detector, tracker, counter, ROI, and
  event modules.
- The evaluation scaffold can compare prediction CSV/JSONL artifacts against
  small reviewed GT templates for counting, ROI, events, and tracking
  engineering metrics.
- `docs/evaluation/reviewed_gt_samples/` and
  `docs/evaluation/reviewed_gt_eval_result/` demonstrate a small reviewed
  GT-to-prediction-to-metrics loop.
- GT templates are documented in [Video Analytics GT Templates](evaluation/gt_templates.md).
- No full reviewed GT dataset or large generated evaluation output is committed.
- Reviewed sample metrics: counting `MAE=1.0`, ROI `frame_count_mae=1.0`,
  event `precision=0.5`, event `recall=0.6666666666666666`, and tracking
  `gt_required_for_idf1=true`.

## Docker Summary

- Docker build passed.
- FastAPI container smoke passed.
- Streamlit container smoke passed.
- Mounted-weight `/predict` passed.
- `best.pt` was mounted read-only from `local_weights/best.pt`.
- Docker image/layers are not committed.
- `local_weights/best.pt` is ignored and remains local-only.
- Result details: [Docker Actual Smoke Result](docker_actual_smoke_result.md)
- Docker v1 API smoke was refreshed in `v1.4.1` for FastAPI API capabilities.
  It does not cover the later React frontend runtime.
- React CORS support was completed in `v1.8.4` for local development origins.

## Frontend Audit Summary

The optional React frontend builds successfully with `npm run build`. During
the final `v1.8.1` polish pass, `npm audit` reported 1 moderate and 1 high
finding in the Vite/esbuild development/build dependency path. The npm
suggested fix requires a semver-major upgrade to Vite 8, so `npm audit fix
--force` was not run in this documentation-only freeze step.

Production deployment should review and upgrade frontend dependencies in a
separate dependency-refresh phase.

## Non-Technical Launcher Summary

`v1.8.2-non-technical-user-launcher` adds:

- `scripts/start_app_macos.command`
- `scripts/start_app_windows.bat`
- `docs/non_technical_user_guide.md`

The launchers check for `.venv` and `local_weights/best.pt`, start the existing
FastAPI and Streamlit services, optionally start the React frontend when
`frontend/node_modules` exists, and open the local browser pages. This stage is
an ease-of-use wrapper only. It does not change YOLO, ByteTrack, DeepSORT,
analytics, Docker, or API behavior.

## Final Freeze Identity Cleanup Summary

`v1.8.5-final-freeze-identity-cleanup` is a final delivery identity pass. It
updates current/latest documentation state, repository ignore policy, and the
React UI badge. It does not change core YOLO, ByteTrack, DeepSORT, Docker,
FastAPI runtime, analytics, evaluation, or training behavior.

The `npm audit` status remains unchanged: 1 moderate and 1 high finding in the
Vite/esbuild development/build dependency path. The semver-major Vite 8 fix was
not forced in this final cleanup scope.

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
- No tracked videos are part of the final delivery state; local/demo videos
  remain ignored unless explicitly reviewed as lightweight documentation.
- No `runs/` or `local_outputs/` committed.
- No `dataset/train`, `dataset/valid`, or `dataset/test` split committed.
- Docker image/layers are not committed.
- `local_weights` and local videos remain ignored/local.

## Known Limitations / Future Work

- large reviewed Bad Case labeling and larger reviewed GT dataset expansion
- large-scale GT benchmark for tracking/counting/ROI/event evaluation beyond
  the small reviewed sample
- optional DeepSORT runtime
- OAuth/JWT, multi-user permissions, and external monitoring
- production React dashboard/video player hardening
- frontend dependency major-version refresh before production deployment
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

This repository is ready for final local/Docker acceptance review at
`v1.8.5-final-freeze-identity-cleanup`.

Do not commit `local_weights/best.pt` or generated artifacts.
