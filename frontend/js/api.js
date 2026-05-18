const API = "http://localhost:8000/api";

// ── Token helpers ──────────────────────────────────────────────
export const getToken  = ()        => localStorage.getItem("ss_token");
export const setToken  = (t)       => localStorage.setItem("ss_token", t);
export const removeToken = ()      => localStorage.removeItem("ss_token");
export const getUser   = ()        => JSON.parse(localStorage.getItem("ss_user") || "null");
export const setUser   = (u)       => localStorage.setItem("ss_user", JSON.stringify(u));
export const isLoggedIn = ()       => !!getToken();

export function requireAuth() {
  if (!isLoggedIn()) { window.location.href = "/login.html"; }
}

// ── Base fetch wrapper ────────────────────────────────────────
async function req(method, path, body, isForm = false) {
  const headers = {};
  const tok = getToken();
  if (tok) headers["Authorization"] = `Bearer ${tok}`;
  if (!isForm) headers["Content-Type"] = "application/json";

  const res = await fetch(API + path, {
    method,
    headers,
    body: isForm ? body : (body ? JSON.stringify(body) : undefined),
  });

  if (res.status === 401) { removeToken(); window.location.href = "/login.html"; }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

// ── Auth ──────────────────────────────────────────────────────
export const register = (name, email, password) =>
  req("POST", "/auth/register", { name, email, password });

export const login = (email, password) =>
  req("POST", "/auth/login", { email, password });

export const getMe = () => req("GET", "/auth/me");

// ── Users ─────────────────────────────────────────────────────
export const getProfile   = ()     => req("GET",  "/users/profile");
export const updateProfile = (d)   => req("PUT",  "/users/profile", d);
export const updateAllergies = (d) => req("PUT",  "/users/allergies", d);

// ── Scans ─────────────────────────────────────────────────────
export const scanImage = (formData) => req("POST", "/scan/image", formData, true);
export const getHistory  = ()       => req("GET",  "/scan/history");
export const getScan     = (id)     => req("GET",  `/scan/${id}`);
export const deleteScan  = (id)     => req("DELETE", `/scan/${id}`);
export const toggleFav   = (id)     => req("POST", `/scan/${id}/favorite`);

// ── Dashboard ─────────────────────────────────────────────────
export const getDashboardStats = () => req("GET", "/dashboard/stats");

// ── Reviews ───────────────────────────────────────────────────
export const getReviews    = (name) => req("GET",  `/products/${encodeURIComponent(name)}/reviews`);
export const postReview    = (name, d) => req("POST", `/products/${encodeURIComponent(name)}/reviews`, d);
export const markHelpful   = (name, id) =>
  req("POST", `/products/${encodeURIComponent(name)}/reviews/${id}/helpful`);

// ── UI helpers ────────────────────────────────────────────────
export function verdictIcon(v) {
  return v === "safe" ? "✅" : v === "caution" ? "⚠️" : "❌";
}
export function verdictLabel(v) {
  return v === "safe" ? "Safe" : v === "caution" ? "Use with Caution" : "Not Safe";
}
export function scoreColor(s) {
  if (s >= 70) return "var(--safe)";
  if (s >= 40) return "var(--caution)";
  return "var(--unsafe)";
}

// ── Dark mode ─────────────────────────────────────────────────
export function initDarkMode() {
  const saved = localStorage.getItem("ss_theme");
  if (saved === "dark") document.documentElement.setAttribute("data-theme", "dark");
}
export function toggleDarkMode() {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  document.documentElement.setAttribute("data-theme", isDark ? "" : "dark");
  localStorage.setItem("ss_theme", isDark ? "light" : "dark");
}