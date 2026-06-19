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

1. v0.8.1 synthetic end-to-end video analysis sample or `track_video.py` skeleton / v0.8.1 合成端到端视频分析样例或 `track_video.py` 骨架
2. v0.9.0 real ByteTrack/DeepSORT plus Streamlit/FastAPI video workflow / v0.9.0 真实跟踪器与视频分析 UI/API 工作流
