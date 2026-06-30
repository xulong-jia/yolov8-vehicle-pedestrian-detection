import { FormEvent, useEffect, useState } from "react";
import { apiRequest } from "../api";
import type { ApiClientConfig, PredictResponse } from "../types";
import { Panel, StatusBadge, TextField } from "./DashboardUi";

interface ImageDetectPanelProps {
  config: ApiClientConfig;
  onRequestId: (requestId: string) => void;
  onResult: (result: PredictResponse | null) => void;
}

export default function ImageDetectPanel({ config, onRequestId, onResult }: ImageDetectPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [modelPath, setModelPath] = useState("");
  const [conf, setConf] = useState("0.25");
  const [imgsz, setImgsz] = useState("640");
  const [device, setDevice] = useState("cpu");
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  function selectFile(nextFile: File | null) {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setFile(nextFile);
    setResult(null);
    onResult(null);
    setPreviewUrl(nextFile ? URL.createObjectURL(nextFile) : "");
  }

  async function submitImage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("请先选择一张图片。");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const body = new FormData();
      body.append("file", file);
      const params = new URLSearchParams({
        conf,
        imgsz,
        device
      });
      if (modelPath.trim()) {
        params.set("model_path", modelPath.trim());
      }
      const response = await apiRequest<PredictResponse>(config, `/predict?${params}`, {
        method: "POST",
        body
      });
      setResult(response.data);
      onResult(response.data);
      onRequestId(response.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "图片检测失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Panel
      title="图片检测"
      eyebrow="单张图片"
      actions={<StatusBadge status={result ? "已完成" : file ? "已上传" : "等待中"} />}
      wide
    >
      <form className="image-detect-grid" onSubmit={submitImage}>
        <label className="dropzone">
          <span>上传图片</span>
          <strong>{file ? file.name : "选择 jpg / png / webp 图片"}</strong>
          <small>用于单张图片检测，结果只在页面中展示。</small>
          <input
            type="file"
            aria-label="上传待检测图片"
            accept="image/png,image/jpeg,image/webp,image/bmp"
            onChange={(event) => selectFile(event.target.files?.[0] || null)}
          />
        </label>
        <div className="image-result-card">
          <div className="image-preview">
            {previewUrl ? <img src={previewUrl} alt="待检测图片预览" /> : <span>图片预览区域</span>}
          </div>
          <div className="summary-grid compact-summary">
            <span>文件</span>
            <strong>{file?.name || "未选择"}</strong>
            <span>检测框</span>
            <strong>{result ? result.num_detections : "待检测"}</strong>
            <span>设备</span>
            <strong>{result?.device || device}</strong>
          </div>
        </div>
        <div className="form-grid compact-grid image-params">
          <TextField label="模型路径" value={modelPath} onChange={setModelPath} placeholder="可选，留空使用后端默认模型" />
          <TextField label="置信度阈值" value={conf} onChange={setConf} type="number" step="0.01" />
          <TextField label="推理尺寸" value={imgsz} onChange={setImgsz} type="number" />
          <TextField label="运行设备" value={device} onChange={setDevice} />
          <div className="form-actions">
            <button type="submit" disabled={loading}>
              {loading ? "检测中" : "开始图片检测"}
            </button>
          </div>
        </div>
      </form>

      {error ? <p className="error-text">{error}</p> : null}
      {result ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>类别</th>
                <th>置信度</th>
                <th>检测框 bbox</th>
              </tr>
            </thead>
            <tbody>
              {result.detections.map((detection, index) => (
                <tr key={`${detection.class_id}-${index}`}>
                  <td>{detection.class_name}</td>
                  <td><StatusBadge status={detection.confidence.toFixed(4)} /></td>
                  <td>
                    {detection.bbox.xmin.toFixed(1)}, {detection.bbox.ymin.toFixed(1)},{" "}
                    {detection.bbox.xmax.toFixed(1)}, {detection.bbox.ymax.toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!result.detections.length ? <p className="muted">当前阈值下没有检测框。</p> : null}
        </div>
      ) : (
        <p className="muted">选择图片后可查看类别、置信度和 bbox。</p>
      )}
    </Panel>
  );
}
