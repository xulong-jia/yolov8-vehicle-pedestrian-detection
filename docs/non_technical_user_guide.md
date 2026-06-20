# 普通用户启动指南

这份说明给不熟悉代码的普通用户使用。维护者提前准备好项目文件夹、Python 环境和模型权重后，用户只需要双击启动脚本，然后在浏览器里操作。

## 这个工具能做什么

- 打开本地网页。
- 上传图片做车辆与行人检测。
- 提交视频分析任务。
- 查询视频任务状态和结果文件。
- 查看 Bad Case 元数据和示例说明。

这个工具不会自动下载模型，也不会把结果提交到 Git。所有本地运行结果默认放在 `local_outputs/`。

## 第一次使用前确认

请让维护者先确认这三件事：

1. 项目文件夹完整。
2. `.venv` 已经创建好。
3. 模型权重存在：`local_weights/best.pt`。

如果 `local_weights/best.pt` 不存在，图片检测和视频分析不能正常运行。

## macOS 怎么启动

1. 打开项目文件夹。
2. 找到 `scripts/start_app_macos.command`。
3. 双击它。
4. 如果 macOS 提示没有执行权限，请让维护者在终端运行：

```bash
chmod +x scripts/start_app_macos.command
```

启动后会打开：

- Streamlit 页面：`http://localhost:8501`
- FastAPI 服务：`http://localhost:8000`
- React 页面：`http://localhost:5173`，仅在 `frontend/node_modules` 已存在时启动

## Windows 怎么启动

1. 打开项目文件夹。
2. 找到 `scripts/start_app_windows.bat`。
3. 双击它。
4. 保持弹出的 FastAPI 和 Streamlit 窗口不要关闭。

启动后会打开：

- Streamlit 页面：`http://localhost:8501`
- FastAPI 健康检查：`http://localhost:8000/health`

React 前端在 Windows 上是可选项。如果维护者已经安装 Node 环境，可以进入 `frontend` 后运行 `npm run dev`，再打开 `http://localhost:5173`。

## 图片检测怎么用

1. 打开 `http://localhost:8501`。
2. 选择图片检测或上传图片的位置。
3. 上传一张本地图片。
4. 等待检测结果显示。

如果使用 React 页面，也可以先检查 Health / Model Status，再使用后端提供的接口能力。

## 视频分析怎么用

1. 把视频放到 `local_videos/source/`，或者准备一个完整视频路径。
2. 在 Streamlit 或 React 的视频任务入口中填写：
   - `video_id`
   - `run_name`
   - 视频路径
   - 模型路径：`local_weights/best.pt`
3. 提交任务。
4. 查询任务状态。

视频分析会写结果到 `local_outputs/`。这些结果是本地文件，不需要提交。

## 结果文件在哪里

常见位置：

- 视频任务：`local_outputs/api_video_jobs/`
- Bad Case 元数据：`local_outputs/bad_cases/`
- 启动日志：`local_outputs/launcher_logs/`

不要手动移动 `local_weights/best.pt`。如果需要清理结果，请先询问维护者。

## 常见问题

### 打不开网页

先等待 10 到 30 秒。如果仍然打不开，检查启动窗口里是否有错误提示。

### 提示模型不存在

说明 `local_weights/best.pt` 不存在。请让维护者把模型权重放到这个位置。

### 端口被占用

如果提示 `localhost:8501` 或 `localhost:8000` 被占用，请先关闭之前打开的 FastAPI、Streamlit 或 React 窗口，然后重新双击启动脚本。

### 如何停止

- macOS：在启动脚本打开的 Terminal 窗口按 Control-C。
- Windows：关闭 FastAPI 和 Streamlit 命令窗口。

### 视频路径怎么填

推荐把视频放在 `local_videos/source/`，然后填写该视频的完整路径。也可以直接填写系统中的完整文件路径。

### 不要删除哪些文件

不要删除：

- `.venv`
- `local_weights/best.pt`
- `configs/`
- `src/`
- `app.py`
- `frontend/`

如果只想清理旧结果，请先询问维护者如何处理 `local_outputs/`。
