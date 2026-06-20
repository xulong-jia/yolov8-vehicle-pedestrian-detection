import type { ApiClientConfig, ApiResult, JsonValue } from "./types";

const defaultBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function getDefaultApiBaseUrl(): string {
  return defaultBaseUrl;
}

export function generateRequestId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `frontend-${Date.now()}`;
}

export async function apiRequest<T>(
  config: ApiClientConfig,
  path: string,
  options: RequestInit = {}
): Promise<ApiResult<T>> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (config.apiKey.trim()) {
    headers.set("X-API-Key", config.apiKey.trim());
  }
  if (config.requestId.trim()) {
    headers.set("X-Request-ID", config.requestId.trim());
  }

  const response = await fetch(`${config.apiBaseUrl.replace(/\/$/, "")}${path}`, {
    ...options,
    headers
  });
  const requestId = response.headers.get("X-Request-ID") || "";
  const text = await response.text();
  const data = text ? (JSON.parse(text) as T) : ({} as T);

  if (!response.ok) {
    const detail = (data as { detail?: JsonValue }).detail;
    throw new Error(
      typeof detail === "string" ? detail : `Request failed with status ${response.status}`
    );
  }

  return {
    data,
    requestId,
    status: response.status
  };
}

export function artifactDownloadUrl(
  apiBaseUrl: string,
  jobId: string,
  artifactName: string
): string {
  const base = apiBaseUrl.replace(/\/$/, "");
  return `${base}/api/videos/jobs/${encodeURIComponent(jobId)}/artifacts/${encodeURIComponent(
    artifactName
  )}/download`;
}
