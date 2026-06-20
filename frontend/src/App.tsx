import { useState } from "react";
import { getDefaultApiBaseUrl, generateRequestId } from "./api";
import type { ApiClientConfig } from "./types";
import HealthPanel from "./components/HealthPanel";
import VideoJobPanel from "./components/VideoJobPanel";
import BadCasePanel from "./components/BadCasePanel";
import StatusPanel from "./components/StatusPanel";

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(getDefaultApiBaseUrl());
  const [apiKey, setApiKey] = useState("");
  const [requestId, setRequestId] = useState(generateRequestId());
  const [lastResponseRequestId, setLastResponseRequestId] = useState("");

  const config: ApiClientConfig = {
    apiBaseUrl,
    apiKey,
    requestId
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">YOLOv8 FastAPI Client</p>
          <h1>Video Job Frontend</h1>
        </div>
        <div className="status-pill">v1.8.0 minimal React frontend</div>
      </header>

      <section className="control-strip" aria-label="API client configuration">
        <label>
          API base URL
          <input value={apiBaseUrl} onChange={(event) => setApiBaseUrl(event.target.value)} />
        </label>
        <label>
          API key
          <input
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            type="password"
            placeholder="optional"
          />
        </label>
        <label>
          X-Request-ID
          <input value={requestId} onChange={(event) => setRequestId(event.target.value)} />
        </label>
        <button type="button" onClick={() => setRequestId(generateRequestId())}>
          New request ID
        </button>
      </section>

      {lastResponseRequestId ? (
        <div className="request-banner">Last response X-Request-ID: {lastResponseRequestId}</div>
      ) : null}

      <div className="dashboard-grid">
        <HealthPanel config={config} onRequestId={setLastResponseRequestId} />
        <VideoJobPanel config={config} onRequestId={setLastResponseRequestId} />
        <BadCasePanel config={config} onRequestId={setLastResponseRequestId} />
        <StatusPanel />
      </div>
    </main>
  );
}
