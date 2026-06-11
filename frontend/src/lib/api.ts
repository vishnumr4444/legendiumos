"use client";
export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function token() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("legendium_token");
}
export function currentUser() {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("legendium_user");
  return raw ? JSON.parse(raw) : null;
}
export async function api(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
      ...(opts.headers || {}),
    },
  });
  if (res.status === 401 && typeof window !== "undefined") {
    localStorage.clear();
    window.location.href = "/login";
    throw new Error("Session expired");
  }
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  return res.json();
}
export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password });
  const res = await fetch(`${API}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Incorrect username or password");
  const data = await res.json();
  localStorage.setItem("legendium_token", data.access_token);
  localStorage.setItem("legendium_user", JSON.stringify(data.user));
  return data.user;
}
export function logout() {
  localStorage.clear();
  window.location.href = "/login";
}
