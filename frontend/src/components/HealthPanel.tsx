import { useState } from "react";
import { apiRequest } from "../api";
import type { ApiClientConfig, JsonValue } from "../types";

interface HealthPanelProps {
  config: ApiClientConfig;
  onRequestId: (requestId: string) => void;
}

export default function HealthPanel({ config, onRequestId }: HealthPanelProps) {
  const [health, setHealth] = useState<JsonValue | null>(null);
  const [modelStatus, setModelStatus] = useState<JsonValue | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadStatus() {
    setLoading(true);
    setError("");
    try {
      const healthResult = await apiRequest<JsonValue>(config, "/health");
      const modelResult = await apiRequest<JsonValue>(config, "/model-status");
      setHealth(healthResult.data);
      setModelStatus(modelResult.data);
      onRequestId(modelResult.requestId || healthResult.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法刷新服务状态");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">服务检查</p>
          <h2>服务状态 / 模型状态</h2>
        </div>
        <button type="button" onClick={loadStatus} disabled={loading}>
          {loading ? "刷新中" : "刷新状态"}
        </button>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
      <div className="split-output">
        <JsonBlock title="服务是否在线 GET /health" value={health} />
        <JsonBlock title="模型是否可用 GET /model-status" value={modelStatus} />
      </div>
    </section>
  );
}

function JsonBlock({ title, value }: { title: string; value: JsonValue | null }) {
  return (
    <div className="json-block">
      <h3>{title}</h3>
      <pre>{value ? JSON.stringify(value, null, 2) : "暂无响应"}</pre>
    </div>
  );
}
