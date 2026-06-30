import { FormEvent, useState } from "react";
import { apiRequest, artifactDownloadUrl } from "../api";
import type { ApiClientConfig, VideoAnalyzePayload, VideoJobResponse } from "../types";
import { Panel, StatusBadge, TextField } from "./DashboardUi";

interface VideoJobPanelProps {
  config: ApiClientConfig;
  onRequestId: (requestId: string) => void;
  onJobChange?: (job: VideoJobResponse | null) => void;
}

const initialForm: VideoAnalyzePayload = {
  video_id: "演示视频",
  run_name: "演示任务",
  source: "",
  video_path: "",
  model_path: "",
  conf: 0.25,
  imgsz: 640,
  device: "cpu",
  run_dir: ""
};

export default function VideoJobPanel({ config, onRequestId, onJobChange }: VideoJobPanelProps) {
  const [form, setForm] = useState<VideoAnalyzePayload>(initialForm);
  const [jobIdQuery, setJobIdQuery] = useState("");
  const [job, setJob] = useState<VideoJobResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = cleanVideoPayload(form);
      const result = await apiRequest<VideoJobResponse>(config, "/api/videos/analyze", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setJob(result.data);
      onJobChange?.(result.data);
      setJobIdQuery(result.data.job_id);
      onRequestId(result.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法创建视频检测任务");
    } finally {
      setLoading(false);
    }
  }

  async function queryJob() {
    if (!jobIdQuery.trim()) {
      setError("请输入任务编号后再查询。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await apiRequest<VideoJobResponse>(
        config,
        `/api/videos/jobs/${encodeURIComponent(jobIdQuery.trim())}`
      );
      setJob(result.data);
      onJobChange?.(result.data);
      onRequestId(result.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法查询任务状态");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Panel title="视频分析任务" eyebrow="视频检测" wide>
      <p className="helper-text">
        当前后端支持本地视频路径任务。填写视频路径、模型路径和基础参数后创建任务，
        再用任务编号查询最近状态和输出路径。
      </p>
      <div className="form-section-title">
        <strong>视频输入与参数</strong>
        <span>不支持在线流或摄像头接入，只处理本地路径。</span>
      </div>
      <form className="form-grid" onSubmit={submitJob}>
        <TextField label="视频ID" value={form.video_id} onChange={(value) => setForm({ ...form, video_id: value })} />
        <TextField label="任务名称" value={form.run_name} onChange={(value) => setForm({ ...form, run_name: value })} />
        <TextField label="视频路径" value={form.source || ""} onChange={(value) => setForm({ ...form, source: value })} placeholder="填写本地视频文件路径" />
        <TextField label="视频路径（备用）" value={form.video_path || ""} onChange={(value) => setForm({ ...form, video_path: value })} placeholder="可选" />
        <TextField label="模型路径" value={form.model_path || ""} onChange={(value) => setForm({ ...form, model_path: value })} placeholder="可选，留空使用默认模型" />
        <TextField label="已有结果目录" value={form.run_dir || ""} onChange={(value) => setForm({ ...form, run_dir: value })} placeholder="高级选项，可不填" />
        <TextField label="置信度阈值" value={String(form.conf)} onChange={(value) => setForm({ ...form, conf: Number(value) })} type="number" step="0.01" />
        <TextField label="推理尺寸" value={String(form.imgsz)} onChange={(value) => setForm({ ...form, imgsz: Number(value) })} type="number" />
        <TextField label="运行设备" value={form.device} onChange={(value) => setForm({ ...form, device: value })} />
        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? "提交中" : "创建检测任务"}
          </button>
        </div>
      </form>
      <div className="form-section-title">
        <strong>最近视频任务</strong>
        <span>提交任务后会自动填入任务编号，也可以手动查询已有任务。</span>
      </div>
      <div className="query-row">
        <label>
          任务编号
          <input value={jobIdQuery} onChange={(event) => setJobIdQuery(event.target.value)} />
        </label>
        <button type="button" onClick={queryJob} disabled={loading}>
          查询任务状态
        </button>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
      {job ? <JobResult config={config} job={job} /> : <p className="muted">暂无任务结果</p>}
      <div className="task-note">
        <StatusBadge status={job?.status || "等待中"} />
        <span>任务可能需要一点时间完成；状态和输出文件以 FastAPI 返回为准。</span>
      </div>
    </Panel>
  );
}

function JobResult({ config, job }: { config: ApiClientConfig; job: VideoJobResponse }) {
  const artifacts = job.artifact_paths || {};
  return (
    <div className="result-stack">
      <div className="summary-grid">
        <span>任务编号</span>
        <strong>{job.job_id}</strong>
        <span>状态</span>
        <StatusBadge status={job.status} />
        <span>输出目录</span>
        <code>{job.output_dir || ""}</code>
        <span>运行目录</span>
        <code>{job.run_dir}</code>
        <span>摘要路径</span>
        <code>{job.summary_path || ""}</code>
      </div>
      <h3>结果文件</h3>
      {Object.keys(artifacts).length ? (
        <ul className="artifact-list">
          {Object.entries(artifacts).map(([name, path]) => (
            <li key={name}>
              <a href={artifactDownloadUrl(config.apiBaseUrl, job.job_id, name)} target="_blank" rel="noreferrer">
                {name}
              </a>
              <code>{path}</code>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">暂无已登记结果文件。</p>
      )}
    </div>
  );
}

function cleanVideoPayload(form: VideoAnalyzePayload): VideoAnalyzePayload {
  return Object.fromEntries(
    Object.entries(form).filter(([, value]) => value !== "" && value !== undefined)
  ) as VideoAnalyzePayload;
}
