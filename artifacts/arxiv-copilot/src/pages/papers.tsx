import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'wouter';
import { AppShell } from '@/components/research/shell';
import { Card, CardContent } from '@/components/ui/card';
import { v3 } from '@/lib/api';
import { useBookmarks } from '@/store/bookmarks';

const TOPICS = ['cs.AI', 'cs.CL', 'cs.LG', 'cs.CV', 'stat.ML', 'cs.RO', 'cs.IR', 'eess.AS'];

export default function PapersPage() {
  const [topic, setTopic] = useState<string | undefined>();
  const [ingestCategory, setIngestCategory] = useState('cs.AI');
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState('');
  const { toggle, has } = useBookmarks();
  const { data = [], refetch } = useQuery({
    queryKey: ['papers', topic],
    queryFn: () => v3.papers(50, topic),
  });

  const handleIngest = async () => {
    setIngesting(true);
    setIngestMsg('');
    try {
      const result = await v3.ingestCategory(ingestCategory, 20);
      setIngestMsg(`Ingested ${result.ingested} papers from ${ingestCategory}`);
      void refetch();
    } catch {
      setIngestMsg('Ingestion failed. Check backend logs.');
    } finally {
      setIngesting(false);
    }
  };

  return (
    <AppShell>
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-4xl font-semibold">Papers</h1>
          <p className="mt-2 text-zinc-400">Browse and filter indexed research.</p>
        </div>
        <Card>
          <CardContent className="p-3 flex items-center gap-3">
            <select
              value={ingestCategory}
              onChange={(e) => setIngestCategory(e.target.value)}
              className="rounded-lg border border-white/10 bg-black/30 px-3 py-1.5 text-sm"
            >
              {TOPICS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <button
              onClick={handleIngest}
              disabled={ingesting}
              className="rounded-xl bg-white px-3 py-1.5 text-xs font-medium text-black transition hover:bg-zinc-200 disabled:opacity-50"
            >
              {ingesting ? 'Fetching…' : 'Ingest from arXiv'}
            </button>
          </CardContent>
        </Card>
      </div>
      {ingestMsg && <p className="mt-2 text-xs text-emerald-400">{ingestMsg}</p>}
      <div className="mt-6 flex flex-wrap gap-2">
        <button
          onClick={() => setTopic(undefined)}
          className={`rounded-full px-3 py-1 text-xs border ${
            !topic ? 'border-indigo-400 bg-indigo-400/20 text-indigo-200' : 'border-white/10 bg-white/5 text-zinc-400 hover:border-white/20'
          }`}
        >
          All
        </button>
        {TOPICS.map((t) => (
          <button
            key={t}
            onClick={() => setTopic(topic === t ? undefined : t)}
            className={`rounded-full px-3 py-1 text-xs border ${
              topic === t ? 'border-indigo-400 bg-indigo-400/20 text-indigo-200' : 'border-white/10 bg-white/5 text-zinc-400 hover:border-white/20'
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {data.map((paper) => (
          <Link key={paper.id} href={`/papers/detail?id=${encodeURIComponent(paper.id)}`}>
            <Card className="h-full hover:border-white/20 transition-colors cursor-pointer">
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex flex-wrap gap-1 mb-2">
                    {paper.topics.slice(0, 2).map((t) => (
                      <span key={t} className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-zinc-500">
                        {t}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={(event) => {
                      event.preventDefault();
                      toggle(paper.id);
                    }}
                    className="shrink-0 text-sm text-amber-300"
                  >
                    {has(paper.id) ? '★ Saved' : '☆ Save'}
                  </button>
                </div>
                <h2 className="font-medium line-clamp-2">{paper.title}</h2>
                <p className="mt-2 text-sm text-zinc-400 line-clamp-2">{paper.abstract}</p>
                <p className="mt-3 text-xs text-zinc-600">
                  {paper.authors.slice(0, 2).join(', ')}
                  {paper.authors.length > 2 ? ' et al.' : ''}
                  {paper.published_at && ` · ${new Date(paper.published_at).getFullYear()}`}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
      {data.length === 0 && (
        <div className="mt-12 text-center text-zinc-500">
          No papers indexed yet. Use the ingest button above to fetch from arXiv.
        </div>
      )}
    </AppShell>
  );
}
