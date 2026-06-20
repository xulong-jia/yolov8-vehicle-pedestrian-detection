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
      setError(err instanceof Error ? err.message : "Unable to load status");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Service</p>
          <h2>Health / Model Status</h2>
        </div>
        <button type="button" onClick={loadStatus} disabled={loading}>
          {loading ? "Loading" : "Refresh"}
        </button>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
      <div className="split-output">
        <JsonBlock title="GET /health" value={health} />
        <JsonBlock title="GET /model-status" value={modelStatus} />
      </div>
    </section>
  );
}

function JsonBlock({ title, value }: { title: string; value: JsonValue | null }) {
  return (
    <div className="json-block">
      <h3>{title}</h3>
      <pre>{value ? JSON.stringify(value, null, 2) : "No response yet"}</pre>
    </div>
  );
}
