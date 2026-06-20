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
      setError("Enter a job_id to query.");
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
      setError(err instanceof Error ? err.message : "Unable to query job");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Video</p>
          <h2>Video Job</h2>
        </div>
      </div>
      <form className="form-grid" onSubmit={submitJob}>
        <Field label="video_id" value={form.video_id} onChange={(value) => setForm({ ...form, video_id: value })} />
        <Field label="run_name" value={form.run_name} onChange={(value) => setForm({ ...form, run_name: value })} />
        <Field label="source" value={form.source || ""} onChange={(value) => setForm({ ...form, source: value })} />
        <Field label="video_path" value={form.video_path || ""} onChange={(value) => setForm({ ...form, video_path: value })} />
        <Field label="model_path" value={form.model_path || ""} onChange={(value) => setForm({ ...form, model_path: value })} />
        <Field label="run_dir attach-mode" value={form.run_dir || ""} onChange={(value) => setForm({ ...form, run_dir: value })} />
        <Field label="conf" value={String(form.conf)} onChange={(value) => setForm({ ...form, conf: Number(value) })} type="number" step="0.01" />
        <Field label="imgsz" value={String(form.imgsz)} onChange={(value) => setForm({ ...form, imgsz: Number(value) })} type="number" />
        <Field label="device" value={form.device} onChange={(value) => setForm({ ...form, device: value })} />
        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? "Submitting" : "Create job"}
          </button>
        </div>
      </form>
      <div className="query-row">
        <label>
          job_id
          <input value={jobIdQuery} onChange={(event) => setJobIdQuery(event.target.value)} />
        </label>
        <button type="button" onClick={queryJob} disabled={loading}>
          Query job
        </button>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
      {job ? <JobResult config={config} job={job} /> : <p className="muted">No job response yet.</p>}
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
      <h3>artifact_paths</h3>
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
        <p className="muted">No artifacts registered.</p>
      )}
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  step
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  step?: string;
}) {
  return (
    <label>
      {label}
      <input type={type} step={step} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function cleanVideoPayload(form: VideoAnalyzePayload): VideoAnalyzePayload {
  return Object.fromEntries(
    Object.entries(form).filter(([, value]) => value !== "" && value !== undefined)
  ) as VideoAnalyzePayload;
}
