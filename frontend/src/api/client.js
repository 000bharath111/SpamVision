// src/api/client.js
const BASE = import.meta.env.VITE_API_BASE || (process.env.REACT_APP_API_BASE || "http://localhost:8000");

async function request(path, opts = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, opts);
  const text = await res.text();
  try {
    const json = JSON.parse(text || "{}");
    if (!res.ok) throw new Error(json.detail || json.error || JSON.stringify(json));
    return json;
  } catch (e) {
    if (!res.ok) throw new Error(text || e.message);
    return {};
  }
}

export async function predict(text, threshold = null) {
  const body = { text };
  if (threshold !== null) body.threshold = threshold;
  return request("/predict/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function getModels() {
  return request("/admin/models");
}

export async function uploadModel(file, version, threshold = null) {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("version", version);
  if (threshold !== null) fd.append("threshold", threshold);
  return request("/admin/upload", { method: "POST", body: fd });
}

export async function activateModel(version) {
  return request(`/admin/activate/${encodeURIComponent(version)}`, { method: "POST" });
}

export async function getReviewQueue(limit = 25) {
  return request(`/review/queue?limit=${limit}`);
}

export async function submitReview(item) {
  return request("/review/submit", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(item) });
}

export async function getMetrics() {
  return request("/admin/metrics");
}
