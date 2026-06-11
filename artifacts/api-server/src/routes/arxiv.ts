import { Router, type IRouter } from "express";
import { XMLParser } from "fast-xml-parser";

const router: IRouter = Router();

const parser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  isArray: (name) => ["entry", "author", "category", "link"].includes(name),
});

type ArxivEntry = {
  id: string;
  title: string;
  summary: string;
  author: Array<{ name: string }>;
  published: string;
  updated: string;
  category: Array<{ "@_term": string }>;
  link: Array<{ "@_href": string; "@_type"?: string; "@_rel"?: string }>;
};

function parseArxivId(rawId: string): string {
  return rawId.replace("http://arxiv.org/abs/", "").replace("https://arxiv.org/abs/", "").split("v")[0];
}

function toJson(entry: ArxivEntry) {
  const arxivId = parseArxivId(entry.id);
  const pdfLink = entry.link?.find((l) => l["@_type"] === "application/pdf");
  const absLink = entry.link?.find((l) => l["@_rel"] === "alternate");
  return {
    id: arxivId,
    arxiv_id: arxivId,
    title: entry.title?.trim().replace(/\s+/g, " ") ?? "",
    abstract: entry.summary?.trim().replace(/\s+/g, " ") ?? "",
    authors: (entry.author ?? []).map((a) => a.name).filter(Boolean),
    categories: (entry.category ?? []).map((c) => c["@_term"]).filter(Boolean),
    published: entry.published ?? "",
    updated: entry.updated ?? "",
    pdf_url: pdfLink?.["@_href"] ?? `https://arxiv.org/pdf/${arxivId}`,
    abs_url: absLink?.["@_href"] ?? `https://arxiv.org/abs/${arxivId}`,
  };
}

async function queryArxiv(params: Record<string, string>): Promise<ReturnType<typeof toJson>[]> {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`http://export.arxiv.org/api/query?${qs}`, {
    headers: { "User-Agent": "ArxivCopilot/1.0 (replit.dev)" },
  });
  if (!res.ok) throw new Error(`arXiv API error ${res.status}`);
  const xml = await res.text();
  const parsed = parser.parse(xml);
  const entries: ArxivEntry[] = parsed?.feed?.entry ?? [];
  return entries.map(toJson);
}

router.get("/search", async (req, res) => {
  const q = (req.query.q as string) ?? "";
  const max = Math.min(Number(req.query.max) || 20, 50);
  if (!q) {
    res.status(400).json({ error: "q is required" });
    return;
  }
  const papers = await queryArxiv({
    search_query: `all:${q}`,
    max_results: String(max),
    sortBy: "relevance",
    sortOrder: "descending",
  });
  res.json(papers);
});

router.get("/category", async (req, res) => {
  const cat = (req.query.cat as string) ?? "cs.AI";
  const max = Math.min(Number(req.query.max) || 30, 50);
  const papers = await queryArxiv({
    search_query: `cat:${cat}`,
    max_results: String(max),
    sortBy: "submittedDate",
    sortOrder: "descending",
  });
  res.json(papers);
});

router.get("/paper", async (req, res) => {
  const id = (req.query.id as string) ?? "";
  if (!id) {
    res.status(400).json({ error: "id is required" });
    return;
  }
  const papers = await queryArxiv({ id_list: id, max_results: "1" });
  if (!papers[0]) {
    res.status(404).json({ error: "Paper not found" });
    return;
  }
  res.json(papers[0]);
});

router.get("/recent", async (req, res) => {
  const cats = (req.query.cats as string) ?? "cs.AI";
  const max = Math.min(Number(req.query.max) || 20, 50);
  const catList = cats.split(",").slice(0, 3);
  const query = catList.map((c) => `cat:${c.trim()}`).join(" OR ");
  const papers = await queryArxiv({
    search_query: query,
    max_results: String(max),
    sortBy: "submittedDate",
    sortOrder: "descending",
  });
  res.json(papers);
});

export default router;
