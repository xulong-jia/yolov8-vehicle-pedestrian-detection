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
          <p className="eyebrow">YOLOv8 本地分析工具</p>
          <h1>YOLOv8 车辆与行人视频分析工具</h1>
        </div>
        <div className="status-pill">v1.8.3 普通用户中文界面</div>
      </header>

      <section className="control-strip" aria-label="后端连接设置">
        <label>
          后端服务地址 <span className="field-key">API base URL</span>
          <input value={apiBaseUrl} onChange={(event) => setApiBaseUrl(event.target.value)} />
        </label>
        <label>
          访问密钥（可选） <span className="field-key">API key</span>
          <input
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            type="password"
            placeholder="如果后端没有开启鉴权，可以留空"
          />
        </label>
        <label>
          请求编号（自动生成） <span className="field-key">X-Request-ID</span>
          <input value={requestId} onChange={(event) => setRequestId(event.target.value)} />
        </label>
        <button type="button" onClick={() => setRequestId(generateRequestId())}>
          生成新编号
        </button>
      </section>

      {lastResponseRequestId ? (
        <div className="request-banner">最近一次响应请求编号：{lastResponseRequestId}</div>
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
