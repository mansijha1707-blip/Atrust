const DEFAULT_DEV_API_ORIGIN = "http://127.0.0.1:8000";

function readViteEnvBaseUrl() {
  try {
    if (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL;
    }
  } catch (_err) {
    // Ignore non-module/legacy runtime issues and use fallback below.
  }
  return undefined;
}

function resolveApiBaseUrl() {
  const viteEnvUrl = readViteEnvBaseUrl();
  if (viteEnvUrl) {
    return viteEnvUrl.replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const fromWindow = window.__ATRUST_API_BASE_URL__;
    if (typeof fromWindow === "string" && fromWindow.trim()) {
      return fromWindow.trim().replace(/\/$/, "");
    }
    if (window.location?.port === "5173") {
      return "/api";
    }
  }

  return DEFAULT_DEV_API_ORIGIN;
}

export const API_BASE_URL = resolveApiBaseUrl();

function buildApiErrorMessage(response, url, bodyText) {
  const statusText = response.statusText || "Unknown";
  const bodySnippet = bodyText ? ` Details: ${bodyText.slice(0, 200)}` : "";
  return `API request failed (${response.status} ${statusText}) at ${url}.${bodySnippet}`;
}

export async function apiRequest(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const bodyText = await response.text();
      throw new Error(buildApiErrorMessage(response, url, bodyText));
    }
    return await response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        `Network error while calling ${url}. This usually means the backend is unreachable, blocked by CORS, or HTTP/HTTPS origins are mixed. Original error: ${error.message}`
      );
    }
    throw error;
  }
}

export function getConnectivityHint() {
  return `Backend base URL: ${API_BASE_URL}. Ensure FastAPI is running and /health is reachable.`;
}
