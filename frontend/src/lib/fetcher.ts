export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";
export async function apiGet(path: string) {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json();
}
