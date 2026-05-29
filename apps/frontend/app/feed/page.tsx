'use client';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { Card } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function FeedPage() {
  const { data = [] } = useQuery({ queryKey: ['feed'], queryFn: api.feed });
  return <AppShell><h1 className="text-4xl font-semibold">Research feed</h1><p className="mt-2 text-zinc-400">A social-style stream of high-signal AI papers and team activity.</p><div className="mt-8 space-y-4">{data.map((paper) => <Card key={paper.id}><div className="flex items-start justify-between gap-4"><div><p className="text-sm text-indigo-200">{paper.topic}</p><h2 className="mt-1 text-xl font-medium">{paper.title}</h2><p className="mt-2 text-zinc-400">{paper.summary}</p><p className="mt-3 text-sm text-zinc-500">{paper.authors.join(', ')}</p></div><span className="rounded-full bg-emerald-400/10 px-3 py-1 text-sm text-emerald-200">{Math.round(paper.score * 100)}%</span></div></Card>)}</div></AppShell>;
}
