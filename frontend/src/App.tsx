import { useEffect, useState } from "react";
import { getDefaultApiBaseUrl, generateRequestId } from "./api";
import type { ApiClientConfig, BadCaseRecord, JsonValue, PredictResponse, VideoJobResponse } from "./types";
import BadCasePanel from "./components/BadCasePanel";
import { PageHeader, Panel, Sidebar, StatCard, StatusBadge, type NavItem } from "./components/DashboardUi";
import HealthPanel from "./components/HealthPanel";
import ImageDetectPanel from "./components/ImageDetectPanel";
import StatusPanel from "./components/StatusPanel";
import VideoJobPanel from "./components/VideoJobPanel";

type PageId = "overview" | "image-detection" | "video-detection" | "results" | "project-info";

const pageHashes: Record<PageId, string> = {
  overview: "#overview",
  "image-detection": "#image",
  "video-detection": "#video",
  results: "#results",
  "project-info": "#about"
};

const navItems: NavItem[] = [
  { id: "overview", label: "总览", description: "系统简介" },
  { id: "image-detection", label: "图片检测", description: "单图推理" },
  { id: "video-detection", label: "视频检测", description: "离线任务" },
  { id: "results", label: "结果查看", description: "产物与样例" },
  { id: "project-info", label: "项目说明", description: "边界与启动" }
];

const pageMeta: Record<PageId, { title: string; description: string }> = {
  overview: {
    title: "YOLOv8 车辆与行人检测系统",
    description: "上传本地图片或视频，运行 YOLOv8 检测，并查看可检查的检测结果。"
  },
  "image-detection": {
    title: "图片检测",
    description: "上传单张本地图片，调用现有 FastAPI 图片检测接口查看类别、置信度和 bbox。"
  },
  "video-detection": {
    title: "视频检测",
    description: "填写本地视频路径和推理参数，创建 YOLOv8 离线视频检测任务。"
  },
  results: {
    title: "结果查看",
    description: "集中查看最近任务状态、输出文件路径、检测摘要和问题样例。"
  },
  "project-info": {
    title: "项目说明",
    description: "查看技术栈、本地端口、启动方式、项目边界和报告截图建议。"
  }
};

export default function App() {
  const [activePage, setActivePage] = useState<PageId>(() => pageFromHash(window.location.hash));
  const [apiBaseUrl, setApiBaseUrl] = useState(getDefaultApiBaseUrl());
  const [apiKey, setApiKey] = useState("");
  const [requestId, setRequestId] = useState(generateRequestId());
  const [lastResponseRequestId, setLastResponseRequestId] = useState("");
  const [health, setHealth] = useState<JsonValue | null>(null);
  const [modelStatus, setModelStatus] = useState<JsonValue | null>(null);
  const [lastJob, setLastJob] = useState<VideoJobResponse | null>(null);
  const [badCases, setBadCases] = useState<BadCaseRecord[]>([]);
  const [imageResult, setImageResult] = useState<PredictResponse | null>(null);

  const config: ApiClientConfig = {
    apiBaseUrl,
    apiKey,
    requestId
  };
  const page = pageMeta[activePage];

  useEffect(() => {
    function handleHashChange() {
      setActivePage(pageFromHash(window.location.hash));
    }

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  function navigateTo(pageId: PageId) {
    setActivePage(pageId);
    if (window.location.hash !== pageHashes[pageId]) {
      window.history.replaceState(null, "", pageHashes[pageId]);
    }
  }

  return (
    <div className="dashboard-layout">
      <Sidebar items={navItems} activeId={activePage} onSelect={(id) => navigateTo(id as PageId)} />
      <main className="app-shell">
        <PageHeader title={page.title} description={page.description} />

        {activePage === "overview" ? (
          <OverviewPage
            config={config}
            onNavigate={navigateTo}
            onRequestId={setLastResponseRequestId}
            onStatusChange={(nextHealth, nextModelStatus) => {
              setHealth(nextHealth);
              setModelStatus(nextModelStatus);
            }}
          />
        ) : null}

        {activePage === "image-detection" ? (
          <ImageDetectPanel config={config} onRequestId={setLastResponseRequestId} onResult={setImageResult} />
        ) : null}

        {activePage === "video-detection" ? (
          <VideoJobPanel config={config} onRequestId={setLastResponseRequestId} onJobChange={setLastJob} />
        ) : null}

        {activePage === "results" ? (
          <ResultsPage
            config={config}
            lastJob={lastJob}
            imageResult={imageResult}
            badCaseCount={badCases.length}
            onRequestId={setLastResponseRequestId}
            onRecordsChange={setBadCases}
          />
        ) : null}

        {activePage === "project-info" ? (
          <ProjectInfoPage
            apiBaseUrl={apiBaseUrl}
            apiKey={apiKey}
            requestId={requestId}
            lastResponseRequestId={lastResponseRequestId}
            health={health}
            modelStatus={modelStatus}
            onApiBaseUrlChange={setApiBaseUrl}
            onApiKeyChange={setApiKey}
            onRequestIdChange={setRequestId}
          />
        ) : null}
      </main>
    </div>
  );
}

function pageFromHash(hash: string): PageId {
  switch (hash.replace(/^#\/?/, "")) {
    case "image":
    case "image-detection":
      return "image-detection";
    case "video":
    case "video-detection":
      return "video-detection";
    case "results":
      return "results";
    case "about":
    case "project-info":
      return "project-info";
    default:
      return "overview";
  }
}

function OverviewPage({
  config,
  onNavigate,
  onRequestId,
  onStatusChange
}: {
  config: ApiClientConfig;
  onNavigate: (page: PageId) => void;
  onRequestId: (requestId: string) => void;
  onStatusChange: (health: JsonValue | null, modelStatus: JsonValue | null) => void;
}) {
  return (
    <div className="overview-layout">
      <div className="overview-actions">
        <article className="home-action-card">
          <span>图片检测</span>
          <strong>单图推理</strong>
          <p>上传图片，查看类别、置信度和 bbox。</p>
          <button type="button" onClick={() => onNavigate("image-detection")}>开始图片检测</button>
        </article>
        <article className="home-action-card">
          <span>视频检测</span>
          <strong>离线任务</strong>
          <p>提交本地视频路径，查看任务状态和输出文件。</p>
          <button type="button" onClick={() => onNavigate("video-detection")}>创建视频任务</button>
        </article>
      </div>

      <Panel title="核心能力" className="overview-main">
        <div className="workflow-list">
          <article>
            <strong>图片检测</strong>
            <span>单张图片推理，输出类别、置信度和 bbox。</span>
          </article>
          <article>
            <strong>视频检测</strong>
            <span>本地视频离线分析，记录任务状态和输出路径。</span>
          </article>
          <article>
            <strong>结果查看</strong>
            <span>集中查看最近任务、输出文件和问题样例。</span>
          </article>
        </div>
        <div className="quick-actions">
          <button type="button" className="secondary-button" onClick={() => onNavigate("image-detection")}>图片检测</button>
          <button type="button" className="secondary-button" onClick={() => onNavigate("video-detection")}>视频检测</button>
          <button type="button" className="secondary-button" onClick={() => onNavigate("results")}>查看结果</button>
        </div>
      </Panel>

      <HealthPanel config={config} onRequestId={onRequestId} onStatusChange={onStatusChange} />
    </div>
  );
}

function ResultsPage({
  config,
  lastJob,
  imageResult,
  badCaseCount,
  onRequestId,
  onRecordsChange
}: {
  config: ApiClientConfig;
  lastJob: VideoJobResponse | null;
  imageResult: PredictResponse | null;
  badCaseCount: number;
  onRequestId: (requestId: string) => void;
  onRecordsChange: (records: BadCaseRecord[]) => void;
}) {
  const detections = imageResult?.detections || [];
  const artifacts = lastJob?.artifact_paths || {};

  return (
    <div className="results-layout">
      <Panel title="最近任务状态" eyebrow="任务状态">
        <div className="summary-grid compact-summary">
          <span>任务编号</span>
          <strong>{lastJob?.job_id || "暂无"}</strong>
          <span>状态</span>
          <StatusBadge status={lastJob?.status || "等待中"} />
          <span>运行目录</span>
          <code>{lastJob?.run_dir || "暂无"}</code>
          <span>摘要路径</span>
          <code>{lastJob?.summary_path || "暂无"}</code>
        </div>
      </Panel>

      <Panel title="检测结果摘要" eyebrow="检测摘要">
        <div className="summary-grid compact-summary">
          <span>图片名称</span>
          <strong>{imageResult?.image_name || "暂无"}</strong>
          <span>检测框</span>
          <strong>{detections.length}</strong>
          <span>类别数</span>
          <strong>{new Set(detections.map((item) => item.class_name)).size}</strong>
          <span>问题样例</span>
          <strong>{badCaseCount}</strong>
        </div>
      </Panel>

      <Panel title="输出产物" eyebrow="输出产物" wide>
        {Object.keys(artifacts).length ? (
          <ul className="artifact-list result-artifacts">
            {Object.entries(artifacts).map(([name, path]) => (
              <li key={name}>
                <div>
                  <StatusBadge status="已完成" />
                  <a href={`${config.apiBaseUrl.replace(/\/$/, "")}/api/videos/jobs/${lastJob?.job_id}/artifacts/${name}/download`} target="_blank" rel="noreferrer">
                    下载 {name}
                  </a>
                </div>
                <code>{path}</code>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">暂无输出文件。提交或查询视频任务后，CSV、JSON、TXT、视频或摘要路径会显示在这里。</p>
        )}
      </Panel>

      <Panel title="图片检测结果表" eyebrow="结果明细" wide>
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
              {detections.length ? (
                detections.map((detection, index) => (
                  <tr key={`${detection.class_name}-${index}`}>
                    <td>{detection.class_name}</td>
                    <td><StatusBadge status={detection.confidence.toFixed(4)} /></td>
                    <td>
                      {detection.bbox.xmin.toFixed(1)}, {detection.bbox.ymin.toFixed(1)},{" "}
                      {detection.bbox.xmax.toFixed(1)}, {detection.bbox.ymax.toFixed(1)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3}>暂无图片检测结果。可先到“图片检测”页面上传图片。</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <BadCasePanel config={config} onRequestId={onRequestId} onRecordsChange={onRecordsChange} />
    </div>
  );
}

function ProjectInfoPage({
  apiBaseUrl,
  apiKey,
  requestId,
  lastResponseRequestId,
  health,
  modelStatus,
  onApiBaseUrlChange,
  onApiKeyChange,
  onRequestIdChange
}: {
  apiBaseUrl: string;
  apiKey: string;
  requestId: string;
  lastResponseRequestId: string;
  health: JsonValue | null;
  modelStatus: JsonValue | null;
  onApiBaseUrlChange: (value: string) => void;
  onApiKeyChange: (value: string) => void;
  onRequestIdChange: (value: string) => void;
}) {
  return (
    <div className="project-info-layout">
      <Panel title="技术栈" eyebrow="技术栈">
        <div className="info-grid">
          <span>前端</span><strong>React + Vite</strong>
          <span>后端</span><strong>FastAPI + Python</strong>
          <span>演示入口</span><strong>Streamlit</strong>
          <span>检测模型</span><strong>YOLOv8 / Ultralytics</strong>
        </div>
      </Panel>

      <Panel title="本地端口" eyebrow="本地端口">
        <div className="port-grid">
          <StatCard label="FastAPI" value="8010" hint="后端接口" />
          <StatCard label="React" value="5178" hint="前端页面" tone="cyan" />
          <StatCard label="Streamlit" value="8511" hint="本地演示" tone="green" />
        </div>
      </Panel>

      <Panel title="启动方式" eyebrow="启动方式" wide>
        <p className="helper-text">
          双击或运行 <code>scripts/start_app_macos.command</code>。停止服务时，在启动窗口按 Control-C。
        </p>
      </Panel>

      <Panel title="报告截图建议" eyebrow="截图建议" wide>
        <div className="report-grid">
          <article><strong>总览</strong><span>系统简介、核心能力、运行检查。</span></article>
          <article><strong>图片检测</strong><span>上传区、检测摘要、结果表。</span></article>
          <article><strong>视频检测</strong><span>任务参数、任务编号、输出路径。</span></article>
          <article><strong>结果查看</strong><span>任务状态、产物路径、问题样例。</span></article>
          <article><strong>项目说明</strong><span>技术栈、端口、边界说明。</span></article>
        </div>
      </Panel>

      <StatusPanel />

      <Panel title="建议检查命令" eyebrow="检查命令" className="print-optional-panel">
        <ul className="status-list check-list">
          <li><StatusBadge status={health ? "正常" : "等待中"} /> FastAPI 健康检查（点击总览页“刷新状态”后更新）</li>
          <li><StatusBadge status={modelStatus ? "正常" : "等待中"} /> 模型路径检查（点击总览页“刷新状态”后更新）</li>
          <li><StatusBadge status="建议" /> <code>npm run build</code></li>
          <li><StatusBadge status="建议" /> <code>tsc --noEmit</code></li>
          <li><StatusBadge status="建议" /> <code>py_compile app.py</code></li>
          <li><StatusBadge status="建议" /> <code>git diff --check</code></li>
        </ul>
      </Panel>

      <Panel title="高级调试信息" eyebrow="调试信息" wide className="print-hidden-panel">
        <details className="advanced-settings">
          <summary>展开后端地址、访问密钥和请求编号</summary>
          <div className="control-strip compact-control" aria-label="高级后端连接设置">
            <label>
              后端服务地址 <span className="field-key">API base URL</span>
              <input value={apiBaseUrl} onChange={(event) => onApiBaseUrlChange(event.target.value)} />
            </label>
            <label>
              访问密钥（可选） <span className="field-key">API key</span>
              <input
                value={apiKey}
                onChange={(event) => onApiKeyChange(event.target.value)}
                type="password"
                placeholder="如果后端没有开启鉴权，可以留空"
              />
            </label>
            <label>
              请求编号 <span className="field-key">X-Request-ID</span>
              <input value={requestId} onChange={(event) => onRequestIdChange(event.target.value)} />
            </label>
            <button type="button" onClick={() => onRequestIdChange(generateRequestId())}>
              生成新编号
            </button>
          </div>
          {lastResponseRequestId ? (
            <div className="request-banner">最近一次响应请求编号：{lastResponseRequestId}</div>
          ) : null}
        </details>
      </Panel>
    </div>
  );
}
