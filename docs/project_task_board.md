# Project Task Board

## Usage

- `[x]` means completed.
- `[ ]` means pending.
- After completing a task, update the checkbox and add the commit hash.
- Do not track model weights, full dataset, large videos, or full runs outputs in Git.

## Current Completed Milestones / 当前已完成里程碑

- [x] Project rename and repository cleanup / 项目改名与仓库清理 — Priority: P0 — Status: Done — Output: `README.md`, `.gitignore` — Commit: `cebfe11`
- [x] Dataset YAML and metadata setup / 数据集 YAML 与元数据配置 — Priority: P0 — Status: Done — Output: `dataset/data.yaml`, `dataset/*.md`, `dataset/*.txt` — Commit: TBD
- [x] Dataset label cleaning and validation / 数据集标签清洗与验证 — Priority: P0 — Status: Done — Output: `results/metrics/` — Commit: `78ed58e`
- [x] YOLOv8n 416x416 10-epoch smoke test / YOLOv8n 416x416 10 轮快速验证 — Priority: P0 — Status: Done — Output: `docs/colab_runs/yolov8n_416_10epochs/` — Commit: `86d0f22`
- [x] YOLOv8n 640x640 50-epoch baseline / YOLOv8n 640x640 50 轮基线实验 — Priority: P0 — Status: Done — Output: `docs/colab_runs/yolov8n_640_50epochs/` — Commit: `0e0abdc`
- [x] YOLOv8n official test split validation / YOLOv8n 官方测试集验证 — Priority: P0 — Status: Done — Output: `Not currently tracked in repository; summary needs to be restored or recreated` / `当前仓库未跟踪，需要后续恢复或重建 summary` — Commit: TBD
- [x] Full test set inference / 完整测试集推理 — Priority: P0 — Status: Done — Output: `Not currently tracked in repository; summary needs to be restored or recreated` / `当前仓库未跟踪，需要后续恢复或重建 summary` — Commit: TBD
- [x] Confidence threshold comparison / 置信度阈值对比 — Priority: P0 — Status: Done — Output: `Not currently tracked in repository; summary needs to be restored or recreated` / `当前仓库未跟踪，需要后续恢复或重建 summary` — Commit: TBD
- [x] Day 4 / Day 5 / Day 6 image inference and error analysis / Day 4 至 Day 6 图片推理与误差分析 — Priority: P0 — Status: Done — Output: `docs/predictions/yolov8n_640_50epochs/`, `docs/predictions/yolov8n_640_50epochs_50samples/` — Commit: `59a7f09`, `60f212c`, `8938a46`
- [x] Video inference demo / 视频推理演示 — Priority: P1 — Status: Done — Output: `docs/video_demos/yolov8n_640_50epochs/` — Commit: `a53dd13`
- [x] YOLOv8s supplementary experiment summary / YOLOv8s 补充实验总结 — Priority: P1 — Status: Done — Output: `docs/experiments/yolov8s_640_50epochs/summary.md` — Commit: `6bd40f5`
- [x] Experiment comparison summary / 实验对比总结 — Priority: P1 — Status: Done — Output: `docs/experiment_comparison.md`, `docs/experiment_comparison.csv` — Commit: `dfd95b1`
- [x] Qualitative error case gallery / 定性误差案例图库 — Priority: P1 — Status: Done — Output: `docs/error_case_gallery/` — Commit: `4341333`
- [x] Streamlit image detection demo / Streamlit 图片检测演示 — Priority: P1 — Status: Done — Output: `app.py`, `docs/streamlit_demo.md` — Commit: `2964d0d`
- [x] README documentation for latest features / README 最新功能文档更新 — Priority: P1 — Status: Done — Output: `README.md` — Commit: `95a0cc9`

## P0 — Project Governance and Documentation / 项目治理与文档

- [x] Create model card / 创建模型卡 — Priority: P0 — Status: Done — Output: `docs/model_card.md` — Commit: `3a4affa`
- [x] Create dataset card / 创建数据集卡 — Priority: P0 — Status: Done — Output: `docs/dataset_card.md` — Commit: `3a4affa`
- [x] Create model weight policy / 创建模型权重管理策略 — Priority: P0 — Status: Done — Output: `docs/model_weight_policy.md` — Commit: `3a4affa`
- [x] Create project roadmap / 创建项目路线图 — Priority: P0 — Status: Done — Output: `docs/project_roadmap.md` — Commit: `24a4bb8`
- [x] Create report assets index / 创建报告素材索引 — Priority: P0 — Status: Done — Output: `docs/report_assets.md` — Commit: `24a4bb8`

## P0 — Evaluation and Analysis / 评估与分析

- [x] Create per-class failure analysis / 创建按类别失败分析 — Priority: P0 — Status: Done — Output: `docs/per_class_failure_analysis.md` — Commit: `24a4bb8`
- [x] Create confusion matrix interpretation / 创建混淆矩阵解读 — Priority: P0 — Status: Done — Output: `docs/confusion_matrix_interpretation.md` — Commit: `24a4bb8`

## P0 — Engineering and Reproducibility / 工程化与可复现性

- [x] Add GitHub Actions Python syntax check / 添加 GitHub Actions Python 语法检查 — Priority: P0 — Status: Done — Output: `.github/workflows/python-check.yml` — Commit: `2d2f1ea`
- [x] Add Makefile for common commands / 添加常用命令 Makefile — Priority: P0 — Status: Done — Output: `Makefile` — Commit: `2d2f1ea`

## P1 — Demo Improvements / 演示功能改进

- [x] Add Streamlit sample image selector / 添加 Streamlit 样例图片选择器 — Priority: P1 — Status: Done — Output: `app.py`, `docs/streamlit_demo.md` — Commit: `ed042c0`
- [x] Add downloadable prediction CSV in Streamlit / 添加 Streamlit 可下载预测结果 CSV — Priority: P1 — Status: Done — Output: `app.py`, `docs/streamlit_demo.md` — Commit: `ed042c0`
- [x] Improve Streamlit error messages / 优化 Streamlit 错误提示 — Priority: P1 — Status: Done — Output: `app.py` — Commit: `ed042c0`

## P1 — Additional Analysis / 补充分析

- [x] Create error taxonomy v2 / 创建错误类型体系 v2 — Priority: P1 — Status: Done — Output: `docs/error_taxonomy.md` — Commit: `6d01ff1`
- [x] Create hard examples list / 创建困难样本清单 — Priority: P1 — Status: Done — Output: `docs/hard_examples.csv`, `docs/hard_examples.md` — Commit: `6d01ff1`
- [x] Create threshold analysis report / 创建阈值分析报告 — Priority: P1 — Status: Done — Output: `docs/threshold_analysis.md` — Commit: `6d01ff1`

## P2 — Engineering Extensions / 工程扩展

- [x] Add local setup check script / 添加本地环境检查脚本 — Priority: P2 — Status: Done — Output: `src/check_setup.py` — Commit: `df2408c`
- [x] Add batch prediction CLI / 添加批量预测命令行工具 — Priority: P2 — Status: Done — Output: `src/batch_predict.py` — Commit: `df2408c`
- [x] Add basic unit tests / 添加基础单元测试 — Priority: P2 — Status: Done — Output: `tests/` — Commit: `b04aa5f`
- [x] Add config file / 添加配置文件 — Priority: P2 — Status: Done — Output: `configs/default.yaml` — Commit: `df2408c`
- [x] Split dependencies if needed / 按需拆分依赖 — Priority: P2 — Status: Done — Output: `requirements-api.txt`, `requirements-dev.txt` — Commit: `a7d7417`

## P2 — Deployment and Serving / 部署与服务化

- [x] Add FastAPI inference service / 添加 FastAPI 推理服务 — Priority: P2 — Status: Done — Output: `src/api.py` — Commit: `a7d7417`
- [x] Implement real FastAPI image prediction endpoint / 实现真实 FastAPI 图片推理接口 — Priority: P2 — Status: Done — Output: `src/api.py`, `docs/api_usage.md`, `tests/test_api.py`, `requirements-api.txt`, `Makefile` — Commit: `15d3519`
- [x] Add API documentation / 添加 API 文档 — Priority: P2 — Status: Done — Output: `docs/api_usage.md` — Commit: `a7d7417`
- [x] Add local deployment guide / 添加本地部署指南 — Priority: P2 — Status: Done — Output: `docs/deployment_guide.md` — Commit: `13def7c`
- [x] Add Dockerfile without weights / 添加不包含权重的 Dockerfile — Priority: P2 — Status: Done — Output: `Dockerfile`, `.dockerignore`, `docs/docker_deployment.md` — Commit: `7361e23`
- [x] Create model loading strategy / 创建模型加载策略 — Priority: P2 — Status: Done — Output: `docs/model_loading_strategy.md` — Commit: `13def7c`

## v0.8.0-video-analytics-mvp / 视频分析 MVP

- [x] Step 1 configs + contracts / Step 1 配置与数据契约 — Priority: P0 — Status: Done — Output: `configs/tracking.yaml`, `configs/analytics.yaml`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md` — Commit: TBD
- [x] Step 2 geometry TDD / Step 2 几何工具 TDD — Priority: P0 — Status: Done — Output: `src/analytics/__init__.py`, `src/analytics/geometry.py`, `tests/test_geometry.py` — Commit: TBD
- [x] Step 3 line counter TDD / Step 3 穿线计数 TDD — Priority: P0 — Status: Done — Output: `src/analytics/line_counter.py`, `tests/test_line_counter.py` — Commit: TBD
- [x] Step 4 ROI counter TDD / Step 4 ROI 计数 TDD — Priority: P0 — Status: Done — Output: `src/analytics/roi_counter.py`, `tests/test_roi_counter.py` — Commit: TBD
- [x] Step 5 event rules TDD / Step 5 事件规则 TDD — Priority: P0 — Status: Done — Output: `src/analytics/event_rules.py`, `tests/test_event_rules.py` — Commit: TBD
- [x] Step 6 track writer / Step 6 轨迹写出器 — Priority: P0 — Status: Done — Output: `src/tracking/track_writer.py`, `tests/test_track_writer.py` — Commit: TBD
- [x] Step 6 Video Analysis Center skeleton / Step 6 分析结果中心骨架 — Priority: P0 — Status: Done — Output: `src/services/video_analysis_center.py`, `tests/test_video_analysis_center.py` — Commit: TBD
- [x] Step 7 docs and tag / Step 7 文档与标签 — Priority: P0 — Status: Ready for tag — Output: `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md`, tag `v0.8.0-video-analytics-mvp` — Commit: TBD

Deferred beyond v0.8.0:

- [ ] Real `track_video.py` integration / 真实 `track_video.py` 接入 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] Real ByteTrack/DeepSORT adapter integration / 真实 ByteTrack/DeepSORT adapter 接入 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] Streamlit video analysis pages / Streamlit 视频分析页面 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] FastAPI video jobs / FastAPI 异步视频任务接口 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] FastAPI video result query endpoints / FastAPI 视频结果查询接口 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] React frontend / React 前端 — Target: v0.9.0+ — Status: Pending
- [ ] Real video benchmark / 真实视频基准测试 — Target: v0.9.0+ — Status: Pending

## v0.8.1-video-analysis-synthetic-pipeline / 视频分析合成流水线

- [x] Step 1 synthetic pipeline / Step 1 合成端到端流水线 — Priority: P0 — Status: Completed — Output: `src/services/synthetic_video_analysis_pipeline.py`, `tests/test_synthetic_video_analysis_pipeline.py`, `docs/project_task_board.md` — Commit: `4596872`

Pending after v0.8.1 Step 1:

- [ ] Real `track_video.py` integration / 真实 `track_video.py` 接入 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] Real ByteTrack/DeepSORT adapter integration / 真实 ByteTrack/DeepSORT adapter 接入 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] Streamlit video analysis pages / Streamlit 视频分析页面 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] FastAPI video jobs / FastAPI 异步视频任务接口 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] FastAPI video result query endpoints / FastAPI 视频结果查询接口 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v0.8.1/v0.9.0 — Status: Pending
- [ ] React frontend / React 前端 — Target: v0.9.0+ — Status: Pending
- [ ] Database integration / 数据库集成 — Target: v0.9.0+ — Status: Pending
- [ ] Real video benchmark / 真实视频基准测试 — Target: v0.9.0+ — Status: Pending

## v0.8.2-track-video-skeleton / track_video 骨架

- [x] Step 1 `track_video.py` skeleton + CLI contract / Step 1 `track_video.py` 骨架与 CLI 契约 — Priority: P0 — Status: Completed — Output: `src/track_video.py`, `tests/test_track_video.py`, `docs/project_task_board.md` — Commit: `5403fe2`

Current scope:

- synthetic detections-to-tracks conversion only
- reads `detections.csv`
- writes `tracks.csv`
- no real video reading
- no YOLO frame inference
- no ByteTrack/DeepSORT adapter

Pending after v0.8.2 Step 1:

- [ ] Real video reading / 真实视频读取 — Target: v0.8.2/v0.9.0 — Status: Pending
- [ ] YOLO frame inference / YOLO 帧级推理 — Target: v0.8.2/v0.9.0 — Status: Pending
- [ ] ByteTrack/DeepSORT adapter integration / ByteTrack/DeepSORT adapter 接入 — Target: v0.8.2/v0.9.0 — Status: Pending
- [ ] Real tracked video rendering / 真实跟踪视频渲染 — Target: v0.9.0 — Status: Pending
- [ ] Streamlit video analysis pages / Streamlit 视频分析页面 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务接口 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video result query endpoints / FastAPI 视频结果查询接口 — Target: v0.9.0 — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v0.9.0 — Status: Pending

## v0.8.3-real-video-reading-skeleton / 真实视频读取骨架

- [x] Step 1 real video reading skeleton / Step 1 真实视频读取骨架 — Priority: P0 — Status: Completed — Output: `src/video_reader.py`, `tests/test_video_reader.py`, `docs/project_task_board.md` — Commit: `71b0f71`

Current scope:

- validates video paths
- reads video metadata only
- builds frame index rows only
- writes `frame_index.csv`
- writes `video_metadata.json`
- no YOLO frame inference
- no ByteTrack/DeepSORT adapter
- no real `track_video.py` runtime
- no tracked video rendering

Pending after v0.8.3 Step 1:

- [x] Connect `video_reader.py` to `track_video.py` skeleton / 将 `video_reader.py` 接入 `track_video.py` 骨架 — Target: v0.8.4/v0.9.0 — Status: Completed in v0.8.4 Step 1
- [ ] YOLO frame inference / YOLO 帧级推理 — Target: v0.8.4/v0.9.0 — Status: Pending
- [ ] ByteTrack/DeepSORT adapter integration / ByteTrack/DeepSORT adapter 接入 — Target: v0.8.4/v0.9.0 — Status: Pending
- [ ] Real `track_video.py` runtime / 真实 `track_video.py` 运行时 — Target: v0.9.0 — Status: Pending
- [ ] Real tracked video rendering / 真实跟踪视频渲染 — Target: v0.9.0 — Status: Pending
- [ ] Streamlit video analysis pages / Streamlit 视频分析页面 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务接口 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video result query endpoints / FastAPI 视频结果查询接口 — Target: v0.9.0 — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v0.9.0 — Status: Pending

## v0.8.4-video-reader-track-video-integration / video_reader 与 track_video 骨架集成

- [x] Step 1 connect `video_reader.py` to `track_video.py` metadata-only mode / Step 1 将 `video_reader.py` 接入 `track_video.py` 元数据模式 — Priority: P0 — Status: Completed — Output: `src/track_video.py`, `tests/test_track_video.py`, `docs/project_task_board.md` — Commit: `be26a40`

Current scope:

- `track_video.py` supports synthetic `detections.csv` to `tracks.csv` conversion
- `track_video.py` supports `--video-source --metadata-only` mode
- metadata-only mode writes `video_metadata.json`
- metadata-only mode writes `frame_index.csv`
- tests use pytest `tmp_path`
- no YOLO frame inference
- no ByteTrack/DeepSORT adapter
- no real tracking runtime
- no tracked video rendering

Pending after v0.8.4 Step 1:

- [ ] YOLO frame inference / YOLO 帧级推理 — Target: v0.8.4/v0.9.0 — Status: Pending
- [ ] ByteTrack/DeepSORT adapter integration / ByteTrack/DeepSORT adapter 接入 — Target: v0.8.4/v0.9.0 — Status: Pending
- [ ] Real tracking runtime / 真实跟踪运行时 — Target: v0.9.0 — Status: Pending
- [ ] Real tracked video rendering / 真实跟踪视频渲染 — Target: v0.9.0 — Status: Pending
- [ ] Streamlit video analysis pages / Streamlit 视频分析页面 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务接口 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video result query endpoints / FastAPI 视频结果查询接口 — Target: v0.9.0 — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v0.9.0 — Status: Pending

## v0.8.5-cli-smoke-docs / CLI 冒烟命令文档

- [x] Step 1 track_video CLI smoke docs / Step 1 `track_video.py` CLI 冒烟命令文档 — Priority: P0 — Status: Completed — Output: `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD

Current scope:

- documents synthetic `detections.csv` to `tracks.csv` smoke command
- documents metadata-only video smoke command
- smoke outputs use `/tmp`
- no new runtime code
- no YOLO frame inference
- no ByteTrack/DeepSORT adapter
- no real tracking runtime
- no tracked video rendering

Pending after v0.8.5 Step 1:

- [ ] Real YOLO frame inference / 真实 YOLO 帧级推理 — Target: v0.9.0 — Status: Pending
- [ ] ByteTrack/DeepSORT adapter integration / ByteTrack/DeepSORT adapter 接入 — Target: v0.9.0 — Status: Pending
- [ ] Real tracking runtime / 真实跟踪运行时 — Target: v0.9.0 — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v0.9.0 — Status: Pending
- [ ] Streamlit video analysis pages / Streamlit 视频分析页面 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务接口 — Target: v0.9.0 — Status: Pending
- [ ] FastAPI video result query endpoints / FastAPI 视频结果查询接口 — Target: v0.9.0 — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v0.9.0 — Status: Pending

## v0.9.0-real-video-detection-tracking-foundation / 真实视频检测与跟踪基础

- [x] Step 1 YOLO video `detections.csv` skeleton / Step 1 YOLO 视频 `detections.csv` 骨架 — Priority: P0 — Status: Completed — Output: `src/predict_video.py`, `tests/test_predict_video.py`, `docs/project_task_board.md` — Commit: `fcbd20e`
- [x] Step 2 ByteTrack/DeepSORT adapter interface skeleton / Step 2 ByteTrack/DeepSORT adapter 接口骨架 — Priority: P0 — Status: Completed — Output: `src/tracking/adapters.py`, `tests/test_tracking_adapters.py`, `docs/project_task_board.md` — Commit: `c6c4646`

Current scope:

- `predict_video.py` supports CSV-first video detection export
- writes `detections.csv`
- `detections.csv` fields are fixed as `video_id`, `frame_index`, `timestamp_sec`, `detection_id`, `class_id`, `class_name`, `confidence`, `xmin`, `ymin`, `xmax`, `ymax`
- YOLO is lazy-loaded and tested with monkeypatch/mock YOLO
- tracking adapter interface is defined
- `SyntheticTrackerAdapter` validates `detections.csv` to `tracks.csv` contract conversion
- `ByteTrackAdapter` and `DeepSORTAdapter` are placeholders only
- placeholder `update(...)` methods raise `NotImplementedError`
- tests use monkeypatch/mock YOLO, fake detections, and pytest `tmp_path`
- no tracker integration
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no real smoke demo

Pending after v0.9.0 Step 2:

- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v0.9.0+ — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v0.9.0+ — Status: Pending
- [ ] Real `tracks.csv` runtime / 真实 `tracks.csv` 运行时 — Target: v0.9.0+ — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v0.9.0+ — Status: Pending
- [ ] `track_video.py` full real runtime / `track_video.py` 完整真实运行时 — Target: v0.9.0+ — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v0.9.0+ — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v0.9.0+ — Status: Pending
- [ ] FastAPI video result query endpoints / FastAPI 视频结果查询接口 — Target: v0.9.0+ — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v0.9.0+ — Status: Pending

## v0.9.1-predict-to-track-synthetic-runtime / 预测到跟踪的 synthetic 运行路径

- [x] Step 1 `track_video.py` uses tracking adapter factory / Step 1 `track_video.py` 使用 tracking adapter factory — Priority: P0 — Status: Completed — Output: `src/track_video.py`, `tests/test_track_video.py`, `docs/project_task_board.md` — Commit: `bb23a28`

Current scope:

- `track_video.py` keeps synthetic `detections.csv` to `tracks.csv` CLI behavior
- detections-to-tracks mode now uses `create_tracker_adapter(tracker_name)`
- current successful runtime tracker is `synthetic`
- `bytetrack` and `deepsort` create placeholder adapters and raise `NotImplementedError` on `update(...)`
- metadata-only video mode does not call the tracker adapter factory
- tests use fake detections and pytest `tmp_path`
- no real ByteTrack/DeepSORT dependency integration
- no full real video tracking runtime
- no tracked video rendering

Pending after v0.9.1 Step 1:

- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Full real video tracking runtime / 完整真实视频跟踪运行时 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Video Analysis Center integration for real video jobs / 真实视频任务接入 Video Analysis Center — Target: v0.9.1+ — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.2-two-command-video-analysis-smoke-flow / 两命令视频分析冒烟链路

- [x] Step 1 two-command predict-to-track smoke flow / Step 1 两命令 predict-to-track 冒烟链路 — Priority: P0 — Status: Completed — Output: `tests/test_predict_to_track_smoke_flow.py`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md` — Commit: `9fe464a`

Current scope:

- documents `predict_video.py` to `track_video.py` two-command flow
- tests `predict_video.py` fake YOLO output to `detections.csv`
- tests `track_video.py` synthetic tracker output to `tracks.csv`
- tests use pytest `tmp_path` and monkeypatch/mock YOLO
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no repository output directories are created

Pending after v0.9.2 Step 1:

- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Video Analysis Center integration for real video jobs / 真实视频任务接入 Video Analysis Center — Target: v0.9.2+ — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.3-video-analysis-center-real-job-skeleton / Video Analysis Center 真实任务骨架

- [x] Step 1 Video Analysis Center real-job skeleton / Step 1 Video Analysis Center 真实任务骨架 — Priority: P0 — Status: Completed — Output: `src/services/video_analysis_job.py`, `tests/test_video_analysis_job.py`, `docs/project_task_board.md` — Commit: `6e4ede9`

Current scope:

- organizes existing `detections.csv` and `tracks.csv` artifacts into a `VideoAnalysisCenter` run directory
- writes `metadata.json`
- copies `detections.csv`
- copies `tracks.csv`
- writes `video_analysis_summary.json`
- counts detection rows, track rows, and unique track IDs
- tests use pytest `tmp_path` only
- does not run YOLO
- does not run tracker
- does not integrate real ByteTrack/DeepSORT dependencies
- does not render tracked video

Pending after v0.9.3 Step 1:

- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Full real `track_video.py` runtime / 完整真实 `track_video.py` 运行时 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Analytics execution on real tracks / 对真实 tracks 执行 analytics — Target: v0.9.3+ — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.4-three-step-video-analysis-job-flow / 三步视频分析任务链路

- [x] Step 1 three-step video analysis job flow / Step 1 三步视频分析任务链路 — Priority: P0 — Status: Completed — Output: `tests/test_three_step_video_analysis_job_flow.py`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md` — Commit: `6c1add9`

Current scope:

- tests `predict_video.py` fake YOLO output to `detections.csv`
- tests `track_video.py` synthetic tracker output to `tracks.csv`
- tests `video_analysis_job.py` output to `VideoAnalysisCenter` run directory
- verifies copied `detections.csv` and `tracks.csv`
- verifies `metadata.json` and `video_analysis_summary.json`
- tests use pytest `tmp_path` and monkeypatch/mock YOLO
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no repository output directories are created

Pending after v0.9.4 Step 1:

- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Analytics execution on real tracks / 对真实 tracks 执行 analytics — Target: v0.9.4+ — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.5-analytics-on-tracks-job / 基于 tracks 的分析任务执行

- [x] Step 1 analytics execution on tracks job / Step 1 基于 tracks 的分析任务执行 — Priority: P0 — Status: Completed — Output: `src/services/video_analysis_job.py`, `tests/test_video_analysis_job.py`, `docs/project_task_board.md` — Commit: `0bd4e31`

Current scope:

- optionally runs analytics from existing `tracks.csv` when `run_analytics=True`
- executes line counter and writes `count_events.csv`
- executes ROI counter and writes `roi_frame_counts.csv`
- executes event rules and writes `events.jsonl`
- updates `video_analysis_summary.json` with count, ROI, and event summaries
- keeps default `run_analytics=False` behavior compatible with v0.9.3
- tests use pytest `tmp_path` and fake CSV files only
- does not run YOLO
- does not run a tracker
- does not integrate real ByteTrack/DeepSORT dependencies
- does not render tracked video
- does not create repository output directories

Pending after v0.9.5 Step 1:

- [ ] Documented four-step local flow / 文档化四步本地链路 — Target: v0.9.5+ — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Full real `track_video.py` runtime / 完整真实 `track_video.py` 运行时 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.6-four-step-local-flow / 四步本地视频分析链路

- [x] Step 1 four-step local video analysis flow / Step 1 四步本地视频分析链路 — Priority: P0 — Status: Completed in working tree — Output: `tests/test_four_step_video_analysis_flow.py`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD

Current scope:

- tests `predict_video.py` fake YOLO output to `detections.csv`
- tests `track_video.py --tracker synthetic` output to `tracks.csv`
- tests `video_analysis_job.py` run creation under `VideoAnalysisCenter`
- tests `run_analytics=True` output to `count_events.csv`, `roi_frame_counts.csv`, and `events.jsonl`
- verifies updated `video_analysis_summary.json`
- tests use pytest `tmp_path` and monkeypatch/mock YOLO
- documents the four-step local smoke flow
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no Streamlit/FastAPI video workflow
- no repository output directories are created

Pending after v0.9.6 Step 1:

- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.7-four-step-smoke-runner / 四步本地冒烟 runner

- [x] Step 1 four-step local smoke runner / Step 1 四步本地冒烟 runner — Priority: P0 — Status: Completed in working tree — Output: `src/run_video_analysis_smoke.py`, `tests/test_run_video_analysis_smoke.py`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD

Current scope:

- wraps the current four-step local flow in `src/run_video_analysis_smoke.py`
- requires explicit `--output-dir`
- calls `predict_video.py` to export `detections.csv`
- calls `track_video.py` with the synthetic tracker to export `tracks.csv`
- calls `video_analysis_job.py` with `run_analytics=True`
- writes Video Analysis Center and analytics artifacts under the provided output directory
- tests use pytest `tmp_path` and monkeypatch/mock YOLO
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no Streamlit/FastAPI video workflow
- no repository output directories are created

Pending after v0.9.7 Step 1:

- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.8-real-local-smoke-preflight / 真实本地冒烟预检

- [x] Step 1 real local smoke preflight checker / Step 1 真实本地冒烟预检器 — Priority: P0 — Status: Completed in working tree — Output: `src/smoke_preflight.py`, `tests/test_smoke_preflight.py`, `docs/project_task_board.md`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md` — Commit: TBD

Current scope:

- checks model path exists and is a file
- checks video path exists and is a file
- checks output directory path without creating it
- checks optional `ultralytics` and `cv2` availability without importing them
- prints command previews for detector CSV export, synthetic tracking, and unified smoke runner
- does not run YOLO
- does not run tracking
- does not create output files or directories
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no Streamlit/FastAPI video workflow

Pending after v0.9.8 Step 1:

- [ ] Actual real local smoke run / 实际真实本地冒烟运行 — Target: v0.9.8+ — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Real DeepSORT dependency integration / 真实 DeepSORT 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending
- [ ] Real video smoke demo / 真实视频冒烟演示 — Target: v1.0 candidate — Status: Pending

## v0.9.9-real-local-smoke-result / 真实本地冒烟结果记录

- [x] Step 1 document real local smoke run result / Step 1 文档化真实本地冒烟运行结果 — Priority: P0 — Status: Completed in working tree — Output: `docs/real_local_smoke_run_result.md`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD

Recorded result:

- preflight `ok=true`
- local YOLOv8s `best.pt` on local `pexels_crosswalk_traffic_demo.mp4`
- `21988` detections
- `21988` synthetic track rows
- `34` synthetic tracks
- Video Analysis Center artifacts produced
- default smoke analytics config did not trigger line, ROI, or event outputs beyond headers
- output stayed under `/tmp/yolov8_real_smoke` and was not committed
- tracker remains synthetic, not ByteTrack/DeepSORT
- no tracked video rendering
- no Streamlit/FastAPI video workflow

Pending after v0.9.9 Step 1:

- [ ] CLI/module invocation ergonomics / CLI 与模块调用易用性修复 — Target: v0.9.10 — Status: Pending
- [ ] Tune analytics config for real smoke video / 为真实 smoke 视频调优 analytics 配置 — Target: v0.9.10+ — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending

## v0.10.0-cli-module-invocation-ergonomics / CLI 与模块调用易用性

- [x] Step 1 module invocation documented and tested / Step 1 文档化并测试模块调用 — Priority: P0 — Status: Completed in working tree — Output: `tests/test_cli_module_invocation.py`, `docs/track_video_cli_usage.md`, `docs/real_local_smoke_run_result.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD

Current scope:

- verifies `.venv/bin/python -m src.smoke_preflight --help`
- verifies `.venv/bin/python -m src.run_video_analysis_smoke --help`
- verifies module-style smoke preflight execution does not create outputs
- keeps `PYTHONPATH=. .venv/bin/python src/run_video_analysis_smoke.py ...` as fallback documentation
- no source code changes required
- no real YOLO run in tests
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no Streamlit/FastAPI video workflow

Pending after v0.10.0 Step 1:

- [ ] Tune analytics config for real smoke video / 为真实 smoke 视频调优 analytics 配置 — Target: v0.10.1+ — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending

## v0.10.1-real-smoke-analytics-config-tuning / 真实 smoke analytics 配置调优辅助

- [x] Step 1 analytics config suggester / Step 1 analytics 配置建议器 — Priority: P0 — Status: Completed in working tree — Output: `src/analytics_config_suggester.py`, `tests/test_analytics_config_suggester.py`, `docs/analytics_config_tuning.md`, `docs/real_local_smoke_run_result.md`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD

Current scope:

- reads existing `tracks.csv`
- summarizes bbox, center, and bottom-center coordinate distributions
- suggests line, ROI, and event-rule config
- uses synthetic CSV unit tests
- does not rerun YOLO
- does not regenerate detections or tracks
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no Streamlit/FastAPI video workflow

Pending after v0.10.1 Step 1:

- [x] Apply suggested config to analytics-only rerun / 将建议配置用于仅 analytics 重跑 — Target: v0.10.2+ — Status: Completed in working tree
- [ ] Visualization overlay for suggested line/ROI / 建议 line/ROI 可视化叠加 — Target: v0.10.2+ — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending

## v0.10.2-analytics-only-rerun-with-suggested-config / 建议配置 analytics-only 重跑

- [x] Step 1 analytics-only rerun tool / Step 1 仅 analytics 重跑工具 — Priority: P0 — Status: Completed in working tree — Output: `src/analytics_only_rerun.py`, `tests/test_analytics_only_rerun.py`, `docs/analytics_config_tuning.md`, `docs/real_local_smoke_run_result.md`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD
- [x] Real smoke analytics rerun performed locally / 本地执行真实 smoke analytics 重跑 — Priority: P0 — Status: Completed locally — Output: `/tmp/yolov8_real_smoke_analytics_rerun` — Commit: Not committed

Current scope:

- reads existing `detections.csv`
- reads existing `tracks.csv`
- reads direct analytics config JSON or v0.10.1 `suggested_config` JSON
- creates a fresh Video Analysis Center run
- writes analytics-only `count_events.csv`, `roi_frame_counts.csv`, `events.jsonl`, and `video_analysis_summary.json`
- does not rerun YOLO
- does not rerun tracker
- does not regenerate detections or tracks
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no Streamlit/FastAPI video workflow

Local rerun result:

- `count_events.csv`: `62` lines including header
- `roi_frame_counts.csv`: `1347` lines including header
- `events.jsonl`: `14` lines
- `count_summary.total_count`: `61`
- `roi_summary.frames_observed`: `1283`
- `event_summary.total_events`: `14`

Pending after v0.10.2 Step 1:

- [x] Suggested analytics overlay plan / 建议 analytics overlay plan — Target: v0.10.3+ — Status: Completed in working tree
- [ ] Static frame overlay renderer / 静态帧 overlay 渲染器 — Target: v0.10.4+ — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending

## v0.10.3-suggested-analytics-overlay-plan / 建议 analytics overlay plan

- [x] Step 1 overlay plan and geometry validation / Step 1 overlay plan 与几何校验 — Priority: P0 — Status: Completed in working tree — Output: `src/analytics_overlay_plan.py`, `tests/test_analytics_overlay_plan.py`, `docs/analytics_config_tuning.md`, `docs/real_local_smoke_run_result.md`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md` — Commit: TBD
- [x] Real smoke overlay plan generated locally / 本地生成真实 smoke overlay plan — Priority: P0 — Status: Completed locally — Output: `/tmp/yolov8_real_smoke/analytics_overlay_plan.json` — Commit: Not committed

Current scope:

- reads existing `tracks.csv`
- reads direct analytics config JSON or v0.10.1 `suggested_config` JSON
- summarizes bbox, center, and bottom-center coordinate ranges
- computes `inferred_frame_bounds` from bbox max coordinates
- validates suggested line geometry
- validates suggested ROI geometry
- writes optional JSON plan only when `--output-json` is provided
- does not run YOLO
- does not run tracker
- does not read or render video frames
- no real ByteTrack/DeepSORT dependency integration
- no tracked video rendering
- no Streamlit/FastAPI video workflow

Local overlay plan result:

- `row_count`: `21988`
- `track_count`: `34`
- `class_counts`: `Bus=588`, `Motorcycle=4`, `Person=21396`
- `inferred_frame_bounds`: `width_hint=1280`, `height_hint=720`
- line `line_main`: `recommendation=ok`
- ROI `roi_main`: `recommendation=ok`

Pending after v0.10.3 Step 1:

- [x] Tracked video renderer / 跟踪视频渲染器 — Target: v0.10.4+ — Status: Completed in working tree
- [ ] Full-length tracked video validation / 全长跟踪视频验证 — Target: v0.10.5+ — Status: Pending
- [ ] Tracked video rendering / 跟踪视频渲染 — Target: v1.0 candidate — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video pages / Streamlit 视频页面 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending

## v0.10.4-tracked-video-rendering / 跟踪视频渲染

- [x] Step 1 tracked video renderer / Step 1 跟踪视频渲染器 — Priority: P0 — Status: Completed in working tree — Output: `src/render_tracked_video.py`, `tests/test_render_tracked_video.py`, `docs/tracked_video_rendering.md`, `docs/track_video_cli_usage.md`, `docs/video_analytics_mvp.md`, `docs/project_task_board.md`, `README.md`, `docs/final_project_report.md`, `docs/real_local_smoke_run_result.md` — Commit: TBD
- [x] Local 300-frame tracked preview rendered / 本地 300 帧跟踪预览已渲染 — Priority: P0 — Status: Completed locally — Output: `/tmp/yolov8_real_smoke/tracked_preview_300.mp4` — Commit: Not committed

Current scope:

- reads existing source video
- reads existing `tracks.csv`
- draws bbox rectangles
- draws `track_id` and `class_name`
- optionally draws line and ROI overlays
- writes output video only to user-provided `--output-video`
- does not run YOLO
- does not run tracker
- does not regenerate detections or tracks
- no real ByteTrack/DeepSORT dependency integration
- no Streamlit/FastAPI video playback

Local preview result:

- `frames_written`: `300`
- `track_rows_loaded`: `21988`
- `unique_tracks`: `34`
- `frames_with_tracks`: `1678`
- `line_overlay_count`: `1`
- `roi_overlay_count`: `1`
- output size: `16M` (`16440663` bytes)

Pending after v0.10.4 Step 1:

- [ ] Full-length tracked video validation / 全长跟踪视频验证 — Target: v0.10.5+ — Status: Pending
- [ ] Real ByteTrack dependency integration / 真实 ByteTrack 依赖集成 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit video playback / Streamlit 视频播放 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video artifact endpoint / FastAPI 视频 artifact 端点 — Target: v1.0 candidate — Status: Pending

## v0.11.0-bytetrack-discovery-spike / ByteTrack 发现性 spike

- [x] Step 1 ByteTrack discovery helper and plan / Step 1 ByteTrack 发现性 helper 与计划 — Priority: P0 — Status: Completed in working tree — Output: `src/tracking/bytetrack_discovery.py`, `tests/test_bytetrack_discovery.py`, `docs/bytetrack_integration_plan.md`, `docs/project_task_board.md`, `docs/video_analytics_mvp.md`, `README.md`, `docs/final_project_report.md`, `docs/track_video_cli_usage.md` — Commit: TBD

Current scope:

- pure-Python discovery helper only
- optional module checks use `importlib.util.find_spec`
- no real ByteTrack runtime
- no real DeepSORT runtime
- no YOLO run
- no local model or video read
- no generated CSV, JSON, JSONL, or video outputs
- validates how fake Ultralytics `model.track` output maps into the existing `tracks.csv` contract
- keeps synthetic tracker fallback

Recommended path:

- first short local Ultralytics `model.track(..., tracker="bytetrack.yaml")` spike after explicit approval
- export real ByteTrack-like `tracks.csv` under `/tmp`
- render a short tracked preview from real ByteTrack tracks
- compare synthetic vs ByteTrack track summaries before claiming tracking quality

Pending after v0.11.0 Step 1:

- [ ] Ultralytics ByteTrack short local spike / Ultralytics ByteTrack 短视频本地 spike — Target: v0.11.1 — Status: Pending
- [ ] Export real ByteTrack `tracks.csv` / 导出真实 ByteTrack `tracks.csv` — Target: v0.11.1+ — Status: Pending
- [ ] Render tracked video from real ByteTrack tracks / 基于真实 ByteTrack tracks 渲染跟踪视频 — Target: v0.11.2+ — Status: Pending
- [ ] Compare synthetic vs ByteTrack tracks / 对比 synthetic 与 ByteTrack 轨迹 — Target: v0.11.2+ — Status: Pending
- [ ] Streamlit video playback / Streamlit 视频播放 — Target: v1.0 candidate — Status: Pending
- [ ] FastAPI video jobs / FastAPI 视频任务 — Target: v1.0 candidate — Status: Pending

## v0.11.1-ultralytics-bytetrack-short-video-spike / Ultralytics ByteTrack 短视频 spike

- [x] Step 1 short-video ByteTrack spike tool / Step 1 短视频 ByteTrack spike 工具 — Priority: P0 — Status: Completed in working tree — Output: `src/track_video_bytetrack_spike.py`, `tests/test_track_video_bytetrack_spike.py`, docs updates — Commit: TBD
- [x] Local short ByteTrack spike attempted / 本地短视频 ByteTrack spike 已尝试 — Priority: P0 — Status: Blocked locally — Output: `/tmp/yolov8_bytetrack_spike` empty dir only — Commit: Not committed

Current scope:

- lazy-loads Ultralytics
- runs `model.track(..., tracker="bytetrack.yaml")` only when explicitly executed
- limits iteration with `--max-frames`
- writes intended output to `/tmp/yolov8_bytetrack_spike/bytetrack_tracks.csv`
- can call existing tracked video renderer for preview output
- tests use fake model/results only
- no Streamlit/FastAPI integration
- not full production integration

Local attempt result:

- blocked by missing dependency: `No module named 'lap'`
- no `bytetrack_tracks.csv` produced
- no tracked preview MP4 produced
- no generated output committed

Pending after v0.11.1 Step 1:

- [ ] Approve/install missing Ultralytics ByteTrack dependency such as `lap` / 批准并安装缺失的 Ultralytics ByteTrack 依赖如 `lap` — Target: v0.11.2 — Status: Pending
- [ ] Rerun short ByteTrack spike / 重新运行短视频 ByteTrack spike — Target: v0.11.2 — Status: Pending
- [ ] Export real ByteTrack `tracks.csv` / 导出真实 ByteTrack `tracks.csv` — Target: v0.11.2 — Status: Pending
- [ ] Render tracked video from real ByteTrack tracks / 基于真实 ByteTrack tracks 渲染跟踪视频 — Target: v0.11.2+ — Status: Pending
- [ ] Compare synthetic vs ByteTrack tracks / 对比 synthetic 与 ByteTrack 轨迹 — Target: v0.11.2+ — Status: Pending
- [ ] Promote spike into `track_video.py` runtime / 将 spike 提升为 `track_video.py` runtime — Target: v1.0 candidate — Status: Pending
- [ ] Analytics rerun on ByteTrack tracks / 基于 ByteTrack tracks 重跑 analytics — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit/FastAPI integration / Streamlit/FastAPI 集成 — Target: v1.0 candidate — Status: Pending

## v0.11.2-lap-dependency-and-bytetrack-rerun / lap 依赖与 ByteTrack 重新运行

- [x] lap install verified locally / 本地已验证 lap 安装 — Priority: P0 — Status: Completed locally — Output: `.venv` local install `lap==0.5.13` — Commit: Not committed
- [x] 300-frame ByteTrack spike succeeded / 300 帧 ByteTrack spike 成功 — Priority: P0 — Status: Completed locally — Output: `/tmp/yolov8_bytetrack_spike` — Commit: Not committed
- [x] Real ByteTrack tracks.csv exported locally / 本地导出真实 ByteTrack `tracks.csv` — Priority: P0 — Status: Completed locally — Output: `/tmp/yolov8_bytetrack_spike/bytetrack_tracks.csv` — Commit: Not committed
- [x] Real ByteTrack tracked preview rendered locally / 本地渲染真实 ByteTrack 跟踪预览 — Priority: P0 — Status: Completed locally — Output: `/tmp/yolov8_bytetrack_spike/bytetrack_tracked_preview_300.mp4` — Commit: Not committed

Local result summary:

- `frames_seen=300`
- `track_rows=746`
- `unique_tracks=25`
- `frames_with_tracks=261`
- `class_counts`: `Person=720`, `Bus=26`
- preview readable by cv2: `frame_count=300`, `fps=29.97`, `width=1280`, `height=720`
- requirements files unchanged; `lap` dependency pin decision pending
- generated outputs are local-only and not committed

Pending after v0.11.2 local verification:

- [ ] Add lap to requirements decision / 是否将 lap 加入 requirements — Target: v0.11.3+ — Status: Pending
- [ ] Promote spike into `track_video.py` runtime / 将 spike 提升为 `track_video.py` runtime — Target: v1.0 candidate — Status: Pending
- [ ] Analytics rerun on ByteTrack tracks / 基于 ByteTrack tracks 重跑 analytics — Target: v1.0 candidate — Status: Pending
- [ ] Synthetic vs ByteTrack comparison / synthetic 与 ByteTrack 对比 — Target: v1.0 candidate — Status: Pending
- [ ] Full-length ByteTrack preview / 全长 ByteTrack 预览 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit/FastAPI integration / Streamlit/FastAPI 集成 — Target: v1.0 candidate — Status: Pending

## v0.11.3-bytetrack-runtime-integration-plan / ByteTrack runtime 接入计划

- [x] Runtime plan doc / runtime 计划文档 — Priority: P0 — Status: Completed in working tree — Output: `docs/bytetrack_runtime_integration_plan.md` — Commit: TBD
- [x] Contract helper / 契约 helper — Priority: P0 — Status: Completed in working tree — Output: `src/tracking/bytetrack_runtime_contract.py` — Commit: TBD
- [x] Contract helper tests / 契约 helper 测试 — Priority: P0 — Status: Completed in working tree — Output: `tests/test_bytetrack_runtime_contract.py` — Commit: TBD

Scope:

- pure-Python planning and contract helper only
- no real YOLO rerun
- no real ByteTrack rerun
- no tracked video rendering
- no `/tmp` output copied into the repository
- no `track_video.py` runtime change yet
- no requirements change yet

Pending after v0.11.3 Step 1:

- [ ] Add lap dependency decision / 是否固化 lap 依赖 — Target: v0.11.4+ — Status: Pending
- [ ] Implement `track_video.py --tracker bytetrack` / 实现 `track_video.py --tracker bytetrack` — Target: v0.11.4 — Status: Pending
- [ ] Analytics rerun on ByteTrack tracks / 基于 ByteTrack tracks 重跑 analytics — Target: v0.11.5+ — Status: Pending
- [ ] Synthetic vs ByteTrack comparison / synthetic 与 ByteTrack 对比 — Target: v0.11.5+ — Status: Pending
- [ ] Full-length validation / 全长验证 — Target: v1.0 candidate — Status: Pending
- [ ] Streamlit/FastAPI integration / Streamlit/FastAPI 集成 — Target: v1.0 candidate — Status: Pending

## v0.11.4-track-video-bytetrack-runtime / 标准 track_video ByteTrack runtime

- [x] Standard CLI path / 标准 CLI 路径 — Priority: P0 — Status: Completed in working tree — Output: `src/track_video.py` — Commit: TBD
- [x] Fake tests / fake 单元测试 — Priority: P0 — Status: Completed in working tree — Output: `tests/test_track_video.py` — Commit: TBD
- [x] Local 300-frame validation / 本地 300 帧验证 — Priority: P0 — Status: Completed locally — Output: `/tmp/yolov8_track_video_bytetrack/tracks.csv` — Commit: Not committed

Scope:

- `python -m src.track_video --video-source ... --model ... --tracker bytetrack`
- writes standard `tracks.csv` under the requested output directory
- default safe short run: `max_frames=300`
- synthetic tracker and metadata-only behavior unchanged
- no tracked video rendering by default
- no analytics rerun in this step

Local result summary:

- `track_rows=746`
- `unique_tracks=25`
- `frames_with_rows=261`
- `class_counts`: `Person=720`, `Bus=26`
- generated output stayed under `/tmp` and was not committed

Pending after v0.11.4 Step 1:

- [ ] Add lap dependency decision / 是否固化 lap 依赖 — Target: v0.11.5+ — Status: Pending
- [ ] Analytics rerun on ByteTrack tracks / 基于 ByteTrack tracks 重跑 analytics — Target: v0.11.5+ — Status: Pending
- [ ] ByteTrack tracked video rendering through standard pipeline / 通过标准流程渲染 ByteTrack 跟踪视频 — Target: v0.11.5+ — Status: Pending
- [ ] Synthetic vs ByteTrack comparison / synthetic 与 ByteTrack 对比 — Target: v0.11.5+ — Status: Pending
- [ ] Streamlit/FastAPI integration / Streamlit/FastAPI 集成 — Target: v1.0 candidate — Status: Pending

## P3 — Optional Future Experiments / 可选未来实验

- [x] Run YOLOv8s official test split validation if weight is available / 在权重可用时运行 YOLOv8s 官方测试集验证 — Priority: P3 — Status: Done — Output: `docs/experiments/yolov8s_640_50epochs_retrain/`, `docs/evaluation/yolov8s_640_50epochs_official/` — Result: P `0.865`, R `0.838`, mAP50 `0.876`, mAP50-95 `0.601` — Commit: `e4d5adb`
- [x] Update strict YOLOv8n vs YOLOv8s same-split comparison / 更新 YOLOv8n 与 YOLOv8s 同测试集严格对比 — Priority: P3 — Status: Done — Output: `docs/strict_model_comparison.md`, `docs/strict_model_comparison.csv`, `docs/experiment_comparison.md`, `docs/experiment_comparison.csv` — Result: Precision `+0.024`, Recall `+0.022`, mAP50 `+0.017`, mAP50-95 `+0.019` — Commit: `6c19def`
- [x] Image size ablation / 输入尺寸消融实验 — Priority: P3 — Status: Done — Output: `docs/image_size_ablation.md`, `docs/image_size_ablation.csv`, `docs/image_size_ablation_raw.json` — Result: validation-only, no training; 416 P `0.834`, R `0.792`, mAP50 `0.855`, mAP50-95 `0.576`; 512 P `0.825`, R `0.830`, mAP50 `0.863`, mAP50-95 `0.582`; 640 P `0.841`, R `0.816`, mAP50 `0.859`, mAP50-95 `0.582`; 512 slightly leads on mAP50/mAP50-95, 640 has highest precision; no full runs committed — Commit: `055d955`
- [x] YOLOv8m experiment / YOLOv8m 实验 — Priority: P3 — Status: Done — Output: `docs/experiments/yolov8m_640_50epochs/`, `docs/evaluation/yolov8m_640_50epochs_official/` — Plan output: `docs/yolov8m_experiment_plan.md` — Result: training validation P `0.837`, R `0.817`, mAP50 `0.870`, mAP50-95 `0.594`; official test P `0.852`, R `0.820`, mAP50 `0.872`, mAP50-95 `0.594`; YOLOv8m did not outperform YOLOv8s on official test mAP50-95 — Commit: `fd61a55`
- [x] YOLOv8 model family comparison / YOLOv8 模型家族对比 — Priority: P3 — Status: Done — Output: `docs/model_family_comparison.md`, `docs/model_family_comparison.csv` — Result: YOLOv8s remains recommended default and best current accuracy/latency trade-off; YOLOv8n remains fastest measured model; YOLOv8m is not recommended as default based on current results — Commit: `1fcb872`
- [ ] Optional YOLOv8m PyTorch speed benchmark / 可选 YOLOv8m PyTorch 推理速度基准测试 — Priority: P3 — Status: Optional — Output: TBD — Commit: TBD
- [ ] Optional YOLOv8m ONNX Runtime benchmark / 可选 YOLOv8m ONNX Runtime 基准测试 — Priority: P3 — Status: Optional — Output: TBD — Commit: TBD
- [x] ONNX export guide without committing ONNX file / 创建 ONNX 导出指南且不提交 ONNX 文件 — Priority: P3 — Status: Done — Output: `docs/onnx_export.md` — Commit: `24ec863`
- [x] ONNX Runtime benchmark/check / ONNX Runtime 基准测试与可运行性检查 — Priority: P3 — Status: Done — Output: `docs/onnx_runtime_benchmark.md`, `docs/onnx_runtime_benchmark.csv`, `docs/onnx_runtime_benchmark_raw.json` — Result: Provider `CUDAExecutionProvider,CPUExecutionProvider`; YOLOv8n 10.994 ms/image, 90.96 FPS; YOLOv8s 13.657 ms/image, 73.22 FPS; output shape `[[1, 10, 8400]]`, finite `True`, non-empty `True`; no ONNX files committed — Commit: `3b4e663`
- [x] Inference speed benchmark / 推理速度基准测试 — Priority: P3 — Status: Done — Output: `docs/inference_speed_benchmark.md`, `docs/inference_speed_benchmark.csv`, `docs/inference_speed_benchmark_raw.json` — Result: Colab Tesla T4, `cuda:0`, 100 measured images, 10 warmup images, imgsz 640; YOLOv8n 11.562 ms/image, 86.49 FPS; YOLOv8s 15.985 ms/image, 62.56 FPS; YOLOv8s latency ratio 1.383x — Commit: `b1a07d9`

## Do Not Track in Git

- `local_weights/`
- `*.pt`
- `*.pth`
- `*.onnx`
- `dataset/train/`
- `dataset/valid/`
- `dataset/test/`
- `runs/`
- `local_videos/source/`
- `*.mp4`
- `*.avi`
- `*.mov`
- `*.mkv`

## Next Recommended Task

1. v0.10.4 Step 2 commit docs/tests and tag tracked video rendering / v0.10.4 Step 2 提交测试文档并打 tag
2. v0.10.5 full-length tracked preview validation / v0.10.5 全长跟踪预览验证
3. v1.0 candidate real ByteTrack dependency integration planning / v1.0 候选真实 ByteTrack 依赖集成规划
