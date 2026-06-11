export type ArxivPaper = {
  id: string;
  arxiv_id: string;
  title: string;
  abstract: string;
  authors: string[];
  categories: string[];
  published: string;
  updated: string;
  pdf_url: string;
  abs_url: string;
};

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const arxiv = {
  search: (q: string, max = 20) =>
    request<ArxivPaper[]>(`/api/arxiv/search?q=${encodeURIComponent(q)}&max=${max}`),

  category: (cat: string, max = 30) =>
    request<ArxivPaper[]>(`/api/arxiv/category?cat=${encodeURIComponent(cat)}&max=${max}`),

  recent: (cats = "cs.AI,cs.CL", max = 20) =>
    request<ArxivPaper[]>(`/api/arxiv/recent?cats=${encodeURIComponent(cats)}&max=${max}`),

  paper: (id: string) =>
    request<ArxivPaper>(`/api/arxiv/paper?id=${encodeURIComponent(id)}`),
};
