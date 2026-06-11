'use client';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { AppShell } from '@/components/research/shell';
import { Card } from '@/components/ui/card';
import { v3 } from '@/lib/api';

export default function TrendingPage() {
  const { data = [], isLoading } = useQuery({ queryKey: ['trending'], queryFn: () => v3.trending(15), staleTime: 60_000 });
  return (
    <AppShell>
      <h1 className="text-4xl font-semibold">Trending papers</h1>
      <p className="mt-2 text-zinc-400">Ranked by recent views and search activity across the platform.</p>
      {isLoading && <div className="mt-8 text-center text-zinc-500">Loading…</div>}
      <div className="mt-8 space-y-4">
        {data.map((item, i) => (
          <motion.div key={item.paper.id} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}>
            <Card>
              <div className="flex items-start gap-4">
                <span className="mt-1 text-3xl font-bold text-zinc-700">{String(i + 1).padStart(2, '0')}</span>
                <div className="flex-1">
                  <div className="flex flex-wrap gap-1">{item.paper.topics.slice(0, 3).map((t) => <span key={t} className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-zinc-400">{t}</span>)}</div>
                  <h2 className="mt-2 font-medium">{item.paper.title}</h2>
                  <p className="mt-1 text-sm text-zinc-400 line-clamp-2">{item.paper.abstract}</p>
                  <div className="mt-3 flex items-center gap-4 text-xs text-zinc-500"><span>{item.paper.authors.slice(0, 2).join(', ')}{item.paper.authors.length > 2 ? ' et al.' : ''}</span><span className="text-emerald-400">{item.reason}</span><span>Score: {item.score.toFixed(1)}</span></div>
                </div>
                <a href={`https://arxiv.org/abs/${item.paper.arxiv_id}`} target="_blank" rel="noopener noreferrer" className="shrink-0 text-xs text-indigo-400 hover:underline">arXiv ↗</a>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </AppShell>
  );
}
