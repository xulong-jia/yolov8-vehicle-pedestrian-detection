import { FormEvent, useState } from "react";
import { apiRequest, artifactDownloadUrl } from "../api";
import type { ApiClientConfig, VideoAnalyzePayload, VideoJobResponse } from "../types";

interface VideoJobPanelProps {
  config: ApiClientConfig;
  onRequestId: (requestId: string) => void;
}

const initialForm: VideoAnalyzePayload = {
  video_id: "demo",
  run_name: "demo_run",
  source: "",
  video_path: "",
  model_path: "",
  conf: 0.25,
  imgsz: 640,
  device: "cpu",
  run_dir: ""
};

export default function VideoJobPanel({ config, onRequestId }: VideoJobPanelProps) {
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
      setJobIdQuery(result.data.job_id);
      onRequestId(result.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create video job");
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
      onRequestId(result.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法查询任务状态");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-header">
        <div>
          <p className="eyebrow">视频</p>
          <h2>视频分析任务</h2>
        </div>
      </div>
      <p className="helper-text">
        普通使用：只需要填写“视频路径”和“模型路径”，然后点击“提交视频分析任务”。
        “已有结果目录”是高级选项，通常不用填写。
      </p>
      <form className="form-grid" onSubmit={submitJob}>
        <Field label="视频ID" fieldKey="video_id" value={form.video_id} onChange={(value) => setForm({ ...form, video_id: value })} />
        <Field label="任务名称" fieldKey="run_name" value={form.run_name} onChange={(value) => setForm({ ...form, run_name: value })} />
        <Field label="视频路径" fieldKey="source" value={form.source || ""} onChange={(value) => setForm({ ...form, source: value })} />
        <Field label="视频路径（备用）" fieldKey="video_path" value={form.video_path || ""} onChange={(value) => setForm({ ...form, video_path: value })} />
        <Field label="模型路径" fieldKey="model_path" value={form.model_path || ""} onChange={(value) => setForm({ ...form, model_path: value })} />
        <Field label="已有结果目录（高级选项，可不填）" fieldKey="run_dir attach-mode" value={form.run_dir || ""} onChange={(value) => setForm({ ...form, run_dir: value })} />
        <Field label="置信度阈值" fieldKey="conf" value={String(form.conf)} onChange={(value) => setForm({ ...form, conf: Number(value) })} type="number" step="0.01" />
        <Field label="推理尺寸" fieldKey="imgsz" value={String(form.imgsz)} onChange={(value) => setForm({ ...form, imgsz: Number(value) })} type="number" />
        <Field label="运行设备" fieldKey="device" value={form.device} onChange={(value) => setForm({ ...form, device: value })} />
        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? "提交中" : "提交视频分析任务"}
          </button>
        </div>
      </form>
      <div className="query-row">
        <label>
          任务编号 <span className="field-key">job_id</span>
          <input value={jobIdQuery} onChange={(event) => setJobIdQuery(event.target.value)} />
        </label>
        <button type="button" onClick={queryJob} disabled={loading}>
          查询任务状态
        </button>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
      {job ? <JobResult config={config} job={job} /> : <p className="muted">暂无任务结果</p>}
    </section>
  );
}

function JobResult({ config, job }: { config: ApiClientConfig; job: VideoJobResponse }) {
  const artifacts = job.artifact_paths || {};
  return (
    <div className="result-stack">
      <div className="summary-grid">
        <span>job_id</span>
        <strong>{job.job_id}</strong>
        <span>status</span>
        <strong>{job.status}</strong>
        <span>output_dir</span>
        <code>{job.output_dir || ""}</code>
        <span>run_dir</span>
        <code>{job.run_dir}</code>
        <span>summary_path</span>
        <code>{job.summary_path || ""}</code>
      </div>
      <h3>结果文件 <span className="field-key">artifact_paths</span></h3>
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

function Field({
  label,
  fieldKey,
  value,
  onChange,
  type = "text",
  step
}: {
  label: string;
  fieldKey: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  step?: string;
}) {
  return (
    <label>
      {label} <span className="field-key">{fieldKey}</span>
      <input type={type} step={step} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function cleanVideoPayload(form: VideoAnalyzePayload): VideoAnalyzePayload {
  return Object.fromEntries(
    Object.entries(form).filter(([, value]) => value !== "" && value !== undefined)
  ) as VideoAnalyzePayload;
}
