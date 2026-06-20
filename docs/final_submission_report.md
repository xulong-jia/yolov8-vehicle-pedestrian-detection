# YOLOv8 车辆与行人检测系统最终项目报告

## 1. 项目背景与目标

本项目面向道路、园区、停车场、校区道路和出入口等常见视频场景，目标是将车辆与行人检测从单一脚本扩展为一套可运行、可复查、可评测、可部署的工程化系统。实际场景中，视频数据不仅需要识别画面中有哪些目标，还需要回答目标是否经过某条线、某个区域内目标数量如何变化、是否出现停留过久或人群聚集等问题。

因此，本项目的目标不止是调用 YOLOv8 画检测框，而是围绕检测、视频推理、多目标跟踪、车流/人流统计、ROI 区域统计、轻量事件检测、Bad Case 复查、FastAPI 服务化、Streamlit/React 可视化和 Docker 部署形成完整链路。项目最终冻结版本为 `v1.8.5-final-freeze-identity-cleanup`，对应提交 `bed6639`，GitHub 仓库为 <https://github.com/xulong-jia/yolov8-vehicle-pedestrian-detection>。

## 2. 系统总体设计

系统整体采用分层架构：

- 感知层：使用 YOLOv8 完成图片和视频帧中的车辆、行人相关目标检测。
- 时序层：通过跟踪模块生成跨帧 `track_id`，其中 ByteTrack runtime 已接入标准 `track_video.py` 路径，DeepSORT 保留为可选未来扩展。
- 分析层：基于 `tracks.csv` 执行 line counter、ROI counter 和 event rules，生成统计与事件结果。
- 结果管理层：通过 VideoAnalysisCenter 统一组织一次视频分析产生的检测、轨迹、统计、ROI、事件和摘要文件。
- 服务与展示层：通过 Streamlit 提供本地演示，通过 FastAPI 提供 JSON API，通过 React 提供最小可选前端，通过 Docker 提供容器化运行方式。

核心链路可以概括为：

```text
image / video
  -> YOLOv8 detection
  -> detections.csv
  -> tracker / ByteTrack
  -> tracks.csv
  -> line counter / ROI counter / event rules
  -> VideoAnalysisCenter
  -> Streamlit / FastAPI / React / reports
```

该设计体现了模块边界：YOLOv8 只负责目标检测，跟踪模块负责目标身份关联，统计和事件模块负责可解释规则，VideoAnalysisCenter 负责结果索引和复查入口，API 和 UI 负责对外使用。

## 3. 数据集与类别设计

项目使用 Roboflow YOLOv8 格式数据集，数据集配置文件为 `dataset/data.yaml`。目标类别固定为 6 类：

- `Bus`
- `Car`
- `Motorcycle`
- `Person`
- `Truck`
- `mini-truck`

项目完成了标签检查和清理，文档中记录了无效类别 ID 检查、polygon-like 标签修复等数据质量处理。完整数据集 split 文件夹不进入 Git，`dataset/train/`、`dataset/valid/`、`dataset/test/` 均按本地资产处理。模型权重、完整数据集、大视频、批量输出和运行结果也通过 `.gitignore`、`.dockerignore` 和 `make danger-check` 进行隔离。

## 4. 模型训练与评估

项目记录了 YOLOv8n、YOLOv8s 和 YOLOv8m 的训练与评估结果，并基于官方测试集和同 split 对比选择 YOLOv8s 作为最终推荐模型。

主要已记录结果包括：

| 实验 | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| YOLOv8n 640x640 50 epochs baseline | 0.81981 | 0.82768 | 0.86422 | 0.59102 |
| YOLOv8n official test | 0.841 | 0.816 | 0.859 | 0.582 |
| YOLOv8s retrain validation | 0.83909 | 0.84059 | 0.87705 | 0.60405 |
| YOLOv8s official test | 0.865 | 0.838 | 0.876 | 0.601 |
| YOLOv8m official test | 0.852 | 0.820 | 0.872 | 0.594 |

在严格同测试集对比中，YOLOv8s 相比 YOLOv8n 的变化为 Precision +0.024、Recall +0.022、mAP50 +0.017、mAP50-95 +0.019。YOLOv8m 没有在官方测试集 mAP50-95 上超过 YOLOv8s，因此被定位为模型规模实验，而不是默认部署模型。

评估体系覆盖 Precision、Recall、mAP50、mAP50-95、混淆矩阵、per-class failure analysis、confidence threshold analysis 和 qualitative error case review。项目也记录了速度与 ONNX Runtime 检查，但未把 ONNX 文件提交到仓库。

## 5. 图片检测与视频检测

图片检测支持多种入口：

- Streamlit 上传图片并显示检测结果。
- `src/predict_image.py` 执行本地图片推理。
- `src/batch_predict.py` 执行批量图片预测并导出 CSV。
- FastAPI `/predict` 接收 multipart 图片上传并返回 JSON 检测结果。

FastAPI 图片接口返回字段包括图片名、图片尺寸、模型路径、置信度阈值、请求尺寸、设备、检测数量和 detections 列表。模型通过 `MODEL_PATH` 或默认配置路径 lazy-load，不在 API import 时加载。

视频检测采用 CSV-first 设计，`src/predict_video.py` 将视频帧检测结果导出为 `detections.csv`。后续跟踪、统计、事件和结果管理均基于稳定文件契约展开。这种设计让视频检测、跟踪、分析和 UI/API 展示可以分阶段测试，也避免把生成的大视频或运行结果提交到仓库。

## 6. 多目标跟踪与视频分析

跟踪模块以 `tracks.csv` 为稳定输出契约，字段可被后续统计、ROI 和事件模块复用。项目经历了 synthetic tracker、ByteTrack discovery、短视频 ByteTrack spike、ByteTrack runtime 集成和 ByteTrack 后处理验证等阶段，最终 ByteTrack runtime 已被接入标准 `src/track_video.py` 路径。

视频分析模块包括：

- tracked video rendering：读取已有 source video 和 `tracks.csv`，生成带 bbox、track_id、line、ROI overlay 的预览视频。
- line counter：基于轨迹穿线判断输出 `count_events.csv`。
- ROI counter：基于 polygon ROI 判断每帧区域内目标数量，输出 `roi_frame_counts.csv`。
- event rules：基于 tracks、ROI counts、line counts 等生成 `events.jsonl`，用于 crowd、density、long stay、wrong direction 等轻量事件。

DeepSORT 当前不是最终冻结交付阻断项。它在文档中明确为 optional future，适用于后续遮挡较多或身份保持要求更高的场景。

## 7. VideoAnalysisCenter 与结果管理

VideoAnalysisCenter 是本项目从脚本型检测升级为工程化系统的重要组件。它不负责模型推理，也不直接判断事件，而是负责组织和索引一次视频分析的完整输出，使 Streamlit、FastAPI、React 和报告文档可以通过统一路径读取结果。

典型一次视频分析结果包括：

- `metadata.json`
- `detections.csv`
- `tracks.csv`
- `count_events.csv`
- `roi_frame_counts.csv`
- `events.jsonl`
- `video_analysis_summary.json`

FastAPI 视频任务使用 SQLite-backed metadata index 保存任务状态、路径、时间戳、错误信息和 artifact path metadata。SQLite 文件默认位于 `local_outputs/api_video_jobs/video_jobs.sqlite3`，只保存元数据，不保存 CSV、JSON、JSONL、图片、视频或模型权重内容。

项目还实现了 registered artifact download endpoints，例如：

```text
GET /api/videos/jobs/{job_id}/artifacts/{artifact_name}/download
```

下载接口只允许访问 job metadata 中已注册的 artifact key，不支持任意路径下载，并拒绝 path traversal 风格的 artifact name。

## 8. 系统服务化与用户界面

系统提供多种使用入口。

Streamlit 是本地演示主入口，支持图片检测、样例图片、检测表格、CSV 下载、视频 artifact 浏览、视频任务提交和结果查看。它适合课程展示、答辩演示和本地复查。

FastAPI 提供服务化接口，当前已交付的主要 endpoint 包括：

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
- `POST /api/bad-cases`
- `GET /api/bad-cases`

API key authentication 默认关闭，开启后通过 `API_KEY_AUTH_ENABLED=true API_KEY=...` 要求受保护接口携带 `X-API-Key`。公共接口包括 `/health`、`/config`、`/model-status`、`/docs` 和 `/openapi.json`。每个响应都会返回 `X-Request-ID`，调用方也可以传入该 header 方便排查。结构化日志包含 request id、path、status code、duration，以及 job/artifact/bad-case 等业务标识。

React 前端位于 `frontend/`，是 minimal optional frontend，不是生产 dashboard。它支持 health/model status、视频任务创建与查询、artifact download links、Bad Case 创建与列表、可选 `X-API-Key`、`X-Request-ID` 输入与展示。`v1.8.4-react-cors-support` 已完成本地 React/Streamlit 开发源的 CORS 支持，默认允许 `http://localhost:5173`、`http://127.0.0.1:5173` 以及常见 Streamlit 本地端口。

普通用户启动入口由 `v1.8.2-non-technical-user-launcher` 提供，包括：

- `scripts/start_app_macos.command`
- `scripts/start_app_windows.bat`
- `docs/non_technical_user_guide.md`

在维护者提前准备 `.venv` 和 `local_weights/best.pt` 后，普通用户可以通过双击脚本启动本地 FastAPI、Streamlit，并在前端依赖存在时启动 React。

## 9. Docker 部署与资产隔离

Docker 部署采用“镜像不包含权重和完整数据集，运行时挂载本地权重”的策略。典型运行方式是将 `local_weights/best.pt` 以只读 volume 挂载到容器内，并通过 `MODEL_PATH` 指定模型路径。

项目已完成 Docker build/run smoke、FastAPI container smoke、Streamlit container smoke 和 mounted-weight `/predict` smoke。`v1.4.1-docker-v1-api-smoke-refresh` 进一步验证了 v1.1-v1.4 API surface，包括 async video jobs、SQLite metadata、Bad Case metadata、GT scaffold 相关接口和 registered artifact download endpoints。该 Docker v1 API smoke 不覆盖 React runtime，也不运行 full video YOLO/ByteTrack 或 DeepSORT。

资产隔离策略明确要求以下内容不进入 Git：

- `local_weights/`
- `*.pt`
- `*.pth`
- `*.onnx`
- `*.sqlite3`
- `*.zip`
- `*.mp4`, `*.avi`, `*.mov`, `*.mkv`
- `dataset/train/`, `dataset/valid/`, `dataset/test/`
- `runs/`
- `local_outputs/`
- `local_videos/source/`
- `frontend/node_modules/`
- `frontend/dist/`
- `frontend/tsconfig.tsbuildinfo`

最终复核中的 risk `git ls-files` 扫描无输出，说明当前仓库没有跟踪权重、视频、local outputs、runs、sqlite、zip 或前端构建产物。

## 10. Bad Case 与评测体系

项目建立了 Bad Case schema、error taxonomy、hard examples、error case gallery 和 Bad Case report。Bad Case 覆盖 detector、tracker、counter、ROI、event、API、deployment、docs 和 dataset 等模块，用于记录 false positive、false negative、class confusion、id switch、count error、roi config error、rule error 等问题。

`v1.6.0-reviewed-bad-case-collection` 增加了 24 条 metadata-only reviewed sample，覆盖 detector、tracker、counter、ROI 和 event 模块。这些样例用于展示 taxonomy、schema、root cause 和 reviewer notes，不是大规模生产 Bad Case 数据集。

`v1.7.0-gt-quantitative-evaluation` 增加了 small reviewed GT quantitative evaluation sample pack，包含 counting、ROI、event 和 tracking 的 reviewed GT / prediction CSV 样例，并通过 `src.evaluation.video_eval_scaffold` 生成轻量 metrics。

当前 reviewed sample 指标包括：

| Metric group | Result |
| --- | --- |
| counting | `gt_count=9`, `pred_count=10`, `abs_error=1`, `MAE=1.0` |
| ROI | `compared_rows=4`, `frame_count_mae=1.0` |
| events | `gt_events=3`, `pred_events=4`, `matched_events=2`, `precision=0.5`, `recall=0.6666666666666666` |
| tracking | `track_count=5`, `avg_track_length=2.0`, `short_track_ratio=0.6`, `gt_required_for_idf1=true` |

该评测样例证明 GT rows、prediction rows 和 scaffold-generated metrics 的闭环可运行，但它不是生产级大规模 benchmark，也没有实现完整 MOT 指标如 IDF1/MOTA。

## 11. 测试与验收结果

项目最终冻结状态通过了多层测试和验收。

Python 测试方面，最终复核记录中 `pytest -q` 结果为 `367 passed, 1 warning`。其中 warning 来自 Starlette/FastAPI TestClient 的 httpx deprecation warning，不是项目 runtime blocker。

项目检查包括：

- `make check`: passed
- `make api-check`: passed
- `make danger-check`: passed
- `git diff --check`: passed
- risk `git ls-files` scan: no output

前端方面，`cd frontend && npm run build` 通过。React build 使用 Vite 5.4.21，构建产物位于已忽略的 `frontend/dist/`。

Docker 方面：

- Docker build passed。
- FastAPI container smoke passed。
- Streamlit container smoke passed。
- Mounted-weight `/predict` passed。
- Docker v1 API smoke passed for async attach-mode jobs、SQLite metadata、artifact summary download 和 Bad Case metadata。

服务化验收方面，FastAPI import 不加载 YOLO，`/health`、`/config`、`/model-status` 不加载模型，`/predict` 首次有效请求时 lazy-load。API key auth、`X-Request-ID`、structured logging 和 CORS support 均已记录并测试。

前端依赖审计方面，`npm audit` 仍有 1 moderate 和 1 high finding，位于 Vite/esbuild development/build dependency chain。npm 建议修复需要 semver-major 升级到 Vite 8，因此最终冻结阶段没有执行 `npm audit fix --force`，而是将其保留为后续 dependency refresh 工作。

## 12. 项目亮点

1. 从单一检测脚本升级为完整视频分析工程链路。项目覆盖数据集、训练、评估、图片检测、视频检测、跟踪、统计、事件、服务化、可视化和部署。
2. 结果可复查。检测、轨迹、计数、ROI、事件和 summary 都以 CSV/JSON/JSONL 等稳定格式保存，并通过 VideoAnalysisCenter 统一组织。
3. 多入口交付。开发者可使用 CLI 和 FastAPI，普通用户可使用 Streamlit 和 launcher，前端展示可使用 minimal React frontend，部署可使用 Docker。
4. Bad Case 与 GT 评测闭环。项目不仅记录成功结果，也建立错误类型、root cause、reviewed sample 和 reviewed GT evaluation scaffold。
5. 普通用户一键启动。macOS/Windows launcher scripts 降低了演示和课程答辩时的启动门槛。
6. 资产边界清楚。模型权重、完整数据集、大视频、运行输出、前端依赖和构建产物均不进入 Git。

## 13. 局限性与未来工作

项目已达到课程/答辩和本地交付状态，但并不声称全部生产级完成。当前明确局限包括：

- DeepSORT production runtime 未完成，仍为 optional future。
- React 仍是 minimal optional frontend，不是生产级 dashboard，也不包含视频播放器、多用户权限或复杂路由。
- 大规模 GT benchmark 未完成；当前只有 small reviewed GT sample，不是 production benchmark。
- OAuth/JWT、多用户权限、API key rotation、Prometheus/Grafana 和外部监控未完成。
- 前端依赖 `npm audit` 仍有 Vite/esbuild development/build dependency findings，未执行 semver-major force upgrade。
- 生产部署 hardening、长期运行监控和更大规模真实视频验证仍属于后续工作。
- Full MOT IDF1/MOTA 等正式跟踪指标未在当前阶段实现，需要更大规模 reviewed tracking GT 和匹配协议。

这些局限不构成 `v1.8.5-final-freeze-identity-cleanup` 的冻结阻断项，因为它们在最终文档中已经被明确划入 future work 或 scope note。

## 14. 总结

本项目最终冻结版本为 `v1.8.5-final-freeze-identity-cleanup`。它已经从 YOLOv8 检测实验扩展为一个包含图片/视频推理、ByteTrack 跟踪、视频分析规则、VideoAnalysisCenter、Bad Case、GT 评测样例、FastAPI、Streamlit、React、Docker 和普通用户启动脚本的工程化系统。

项目的交付重点是本地可运行、结果可复查、接口可测试、资产边界清楚、文档验收完整。它没有夸大为完整生产平台，也没有把 DeepSORT、OAuth/JWT、大规模 GT benchmark 或生产级 React dashboard 误写为已完成。根据当前文档、测试、构建和资产扫描结果，本项目已经达到课程提交和答辩展示所需的最终交付状态。
