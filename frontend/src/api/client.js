const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

let isRefreshing = false;
let refreshPromise = null;

async function refreshTokens() {
  const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error("Refresh failed");
  }
  return response.json();
}

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });

  // If 401 and this isn't the refresh endpoint itself, try refreshing
  if (response.status === 401 && !endpoint.includes("/auth/refresh")) {
    // Deduplicate: if multiple requests fail at the same time,
    // only one refresh call is made; others wait for it
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = refreshTokens().finally(() => {
        isRefreshing = false;
        refreshPromise = null;
      });
    }

    try {
      await refreshPromise;
    } catch {
      // Refresh failed — don't retry, throw the original 401
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Session expired. Please log in again.");
    }

    // Retry the original request with the new access token cookie
    const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      ...options,
    });

    if (!retryResponse.ok) {
      const error = await retryResponse.json().catch(() => ({}));
      throw new Error(error.detail || `Request failed: ${retryResponse.status}`);
    }
    return retryResponse.json();
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    // Support structured error details (e.g., { code, message, email })
    if (error.detail && typeof error.detail === "object") {
      const err = new Error(error.detail.message || `Request failed: ${response.status}`);
      err.data = error.detail;
      err.status = response.status;
      throw err;
    }
    const err = new Error(error.detail || `Request failed: ${response.status}`);
    err.status = response.status;
    throw err;
  }

  return response.json();
}

export const api = {
  get: (endpoint) => request(endpoint),
  post: (endpoint, body) =>
    request(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
