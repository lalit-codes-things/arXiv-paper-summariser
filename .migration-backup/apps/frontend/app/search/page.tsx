'use client';
import { Suspense, useState, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { v3 } from '@/lib/api';

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState(searchParams.get('q') ?? '');
  const [submitted, setSubmitted] = useState(searchParams.get('q') ?? '');

  const { data, isFetching } = useQuery({
    queryKey: ['search', submitted],
    queryFn: () => v3.search(submitted, 15),
    enabled: submitted.length > 0,
  });

  const handleSearch = useCallback(() => {
    setSubmitted(query);
    router.replace(`/search?q=${encodeURIComponent(query)}`);
  }, [query, router]);

  return (
    <AppShell>
      <h1 className="text-4xl font-semibold">Semantic search</h1>
      <p className="mt-2 text-zinc-400">Hybrid vector + keyword search across all indexed papers.</p>
      <div className="mt-6 flex gap-3">
        <input
          className="flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-2.5 text-sm outline-none focus:border-indigo-400"
          placeholder="e.g. attention mechanisms for long sequences..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button onClick={handleSearch} disabled={isFetching}>{isFetching ? 'Searching…' : 'Search'}</Button>
      </div>
      {data && <div className="mt-2 text-xs text-zinc-500">{data.results.length} results for &quot;{data.query}&quot;</div>}
      <div className="mt-6 space-y-4">
        {data?.results.map((result) => (
          <Card key={result.paper.id}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-indigo-400/10 px-2 py-0.5 text-xs text-indigo-300">{result.match_type}</span>
                  {result.paper.topics.slice(0, 2).map((t) => <span key={t} className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-zinc-400">{t}</span>)}
                </div>
                <h2 className="mt-2 text-lg font-medium leading-snug">{result.paper.title}</h2>
                <p className="mt-1 text-sm text-zinc-400 line-clamp-2">{result.matched_chunk ?? result.paper.abstract}</p>
                <p className="mt-2 text-xs text-zinc-500">{result.paper.authors.slice(0, 3).join(', ')}{result.paper.authors.length > 3 ? ' et al.' : ''}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <span className="text-sm font-medium text-emerald-300">{Math.round(result.score * 100)}%</span>
                <a href={`https://arxiv.org/abs/${result.paper.arxiv_id}`} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-400 hover:underline">arXiv ↗</a>
              </div>
            </div>
          </Card>
        ))}
      </div>
      {data && !isFetching && data.results.length === 0 && <p className="mt-8 text-center text-zinc-500">No results found.</p>}
    </AppShell>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<AppShell><div className="mt-20 text-center text-zinc-500">Loading search…</div></AppShell>}>
      <SearchContent />
    </Suspense>
  );
}
