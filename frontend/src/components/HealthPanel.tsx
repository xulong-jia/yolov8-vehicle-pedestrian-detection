import { useState } from "react";
import { apiRequest } from "../api";
import type { ApiClientConfig, JsonValue } from "../types";
import { Panel, StatusBadge } from "./DashboardUi";

interface HealthPanelProps {
  config: ApiClientConfig;
  onRequestId: (requestId: string) => void;
  onStatusChange?: (health: JsonValue | null, modelStatus: JsonValue | null) => void;
}

export default function HealthPanel({ config, onRequestId, onStatusChange }: HealthPanelProps) {
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
      onStatusChange?.(healthResult.data, modelResult.data);
      onRequestId(modelResult.requestId || healthResult.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法刷新服务状态");
    } finally {
      setLoading(false);
    }
  }

  const serviceStatus = health ? "正常" : "等待中";

  return (
    <Panel
      title="运行状态"
      className="health-slim-panel"
      actions={
        <button type="button" className="secondary-button small-button" onClick={loadStatus} disabled={loading}>
          {loading ? "刷新中" : "刷新状态"}
        </button>
      }
    >
      {error ? <p className="error-text">{error}</p> : null}
      <div className="slim-status-row">
        <span>服务状态：</span>
        <StatusBadge status={serviceStatus} />
        <span>·</span>
        <span>FastAPI 8010</span>
        <span>·</span>
        <span>React 5178</span>
        <span>·</span>
        <span>Streamlit 8511</span>
      </div>
      <details className="json-details">
        <summary>查看原始响应</summary>
        <div className="split-output">
          <JsonBlock title="服务是否在线 GET /health" value={health} />
          <JsonBlock title="模型是否可用 GET /model-status" value={modelStatus} />
        </div>
      </details>
    </Panel>
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
