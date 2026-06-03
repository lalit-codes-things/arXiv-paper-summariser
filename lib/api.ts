const V5_URL = process.env.NEXT_PUBLIC_V5_API_URL ?? 'http://localhost:8001';
const V3_URL = process.env.NEXT_PUBLIC_V3_API_URL ?? 'http://localhost:8000';

export type Paper = {
  id: string;
  title: string;
  authors: string[];
  topic: string;
  score: number;
  summary: string;
};
export type V3Paper = {
  id: string;
  arxiv_id: string;
  title: string;
  abstract: string;
  authors: string[];
  topics: string[];
  summary: string | null;
  published_at: string | null;
  created_at: string;
};
export type Dashboard = {
  trends: string[];
  reading_stats: { read: number; bookmarked: number; discussed: number };
  recommended: Paper[];
};
export type SearchResult = {
  paper: V3Paper;
  score: number;
  matched_chunk: string | null;
  match_type: 'semantic' | 'keyword' | 'hybrid';
};
export type SearchResponse = { query: string; results: SearchResult[] };
export type TrendingPaper = { paper: V3Paper; score: number; reason: string };
export type FeedPaper = {
  id: string;
  arxiv_id: string;
  title: string;
  abstract: string;
  authors: string[];
  topics: string[];
  score: number;
  published_at: string | null;
  reason: string;
};

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) },
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export const v5 = {
  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>(`${V5_URL}/api/v1/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: (token: string) =>
    request<{ id: string; email: string; name: string; role: string }>(`${V5_URL}/api/v1/me`, {
      headers: { authorization: `Bearer ${token}` },
    }),
  dashboard: (token?: string) =>
    request<Dashboard>(`${V5_URL}/api/v1/dashboard`, {
      headers: token ? { authorization: `Bearer ${token}` } : {},
    }),
  graph: () =>
    request<{
      nodes: Array<{ id: string; label: string; group: string }>;
      edges: Array<{ source: string; target: string; weight: number }>;
    }>(`${V5_URL}/api/v1/graph`),
  annotations: (workspaceId: string, token: string) =>
    request<unknown[]>(`${V5_URL}/api/v1/workspaces/${workspaceId}/annotations`, {
      headers: { authorization: `Bearer ${token}` },
    }),
};

export const v3 = {
  papers: (limit = 20, topic?: string) =>
    request<V3Paper[]>(`${V3_URL}/api/v3/papers?limit=${limit}${topic ? `&topic=${topic}` : ''}`),
  paper: (id: string) => request<V3Paper>(`${V3_URL}/api/v3/paper/${id}`),
  search: (q: string, limit = 10) =>
    request<SearchResponse>(`${V3_URL}/api/v3/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  trending: (limit = 10) => request<TrendingPaper[]>(`${V3_URL}/api/v3/trending?limit=${limit}`),
  related: (paperId: string, limit = 10) =>
    request<{ paper_id: string; results: SearchResult[] }>(`${V3_URL}/api/v3/related/${paperId}?limit=${limit}`),
  feed: (userId = 'anonymous', limit = 20) =>
    request<FeedPaper[]>(`${V3_URL}/api/v3/feed/personalized?user_id=${userId}&limit=${limit}`),
  chat: (paperId: string, message: string, history: unknown[] = []) =>
    request<{ answer: string; citations: string[]; paper_id: string }>(`${V3_URL}/api/v3/chat/paper`, {
      method: 'POST',
      body: JSON.stringify({ paper_id: paperId, message, conversation_history: history }),
    }),
  ingestCategory: (category: string, maxResults = 20) =>
    request<{ ingested: number; paper_ids: string[] }>(`${V3_URL}/api/v3/ingest/category`, {
      method: 'POST',
      body: JSON.stringify({ category, max_results: maxResults }),
    }),
  ingestPaper: (arxivId: string) =>
    request<{ paper_id: string; arxiv_id: string }>(`${V3_URL}/api/v3/ingest/paper`, {
      method: 'POST',
      body: JSON.stringify({ arxiv_id: arxivId }),
    }),
  recordEvent: (userId: string, paperId: string, action = 'viewed') =>
    request<unknown>(`${V3_URL}/api/v3/memory/events`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, paper_id: paperId, action }),
    }),
  userProfile: (userId: string) =>
    request<{ id: string; interests: string[]; topic_clusters: Record<string, number> }>(
      `${V3_URL}/api/v3/memory/users/${userId}`,
    ),
};

export const api = v5;
