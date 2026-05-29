export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export type Paper = { id: string; title: string; authors: string[]; topic: string; score: number; summary: string };
export type Dashboard = { trends: string[]; reading_stats: { read: number; bookmarked: number; discussed: number }; recommended: Paper[] };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { ...init, headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) }, cache: 'no-store' });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) => request<{ access_token: string; token_type: string }>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  dashboard: (token?: string) => request<Dashboard>('/api/v1/dashboard', { headers: token ? { authorization: `Bearer ${token}` } : {} }),
  feed: () => request<Paper[]>('/api/v1/feed'),
  graph: () => request<{ nodes: Array<{ id: string; label: string; group: string }>; edges: Array<{ source: string; target: string; weight: number }> }>('/api/v1/graph'),
  chat: (paperId: string, message: string, token?: string) => request<{ answer: string; citations: string[] }>(`/api/v1/papers/${paperId}/chat`, { method: 'POST', body: JSON.stringify({ message }), headers: token ? { authorization: `Bearer ${token}` } : {} })
};
