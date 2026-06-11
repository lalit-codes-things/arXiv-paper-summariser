import { useQuery } from '@tanstack/react-query';
import { Link } from 'wouter';
import { motion } from 'framer-motion';
import { AppShell } from '@/components/research/shell';
import { Card, CardContent } from '@/components/ui/card';
import { v3 } from '@/lib/api';
import { useSession } from '@/store/session';

export default function FeedPage() {
  const token = useSession((s) => s.token);
  const userId = token ? 'authenticated-user' : 'anonymous';
  const { data = [], isLoading } = useQuery({
    queryKey: ['feed', userId],
    queryFn: () => v3.feed(userId, 20),
    staleTime: 30_000,
  });
  return (
    <AppShell>
      <h1 className="text-4xl font-semibold">Research feed</h1>
      <p className="mt-2 text-zinc-400">Personalized papers ranked by relevance, freshness, and activity.</p>
      {isLoading && <div className="mt-8 text-center text-zinc-400">Loading your feed…</div>}
      <div className="mt-8 space-y-4">
        {data.map((paper, i) => (
          <motion.div
            key={paper.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Link href={`/papers/detail?id=${encodeURIComponent(paper.id)}`}>
              <Card className="hover:border-white/20 transition-colors cursor-pointer">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex flex-wrap gap-1 mb-2">
                        {paper.topics.slice(0, 3).map((t) => (
                          <span key={t} className="text-xs text-indigo-300 border border-indigo-400/20 bg-indigo-400/10 rounded-full px-2 py-0.5">
                            {t}
                          </span>
                        ))}
                      </div>
                      <h2 className="text-lg font-medium leading-snug line-clamp-2">{paper.title}</h2>
                      <p className="mt-2 text-sm text-zinc-400 line-clamp-2">{paper.abstract}</p>
                      <div className="mt-3 flex items-center gap-3 text-xs text-zinc-500">
                        <span>{paper.authors.slice(0, 2).join(', ')}</span>
                        {paper.published_at && <span>{new Date(paper.published_at).toLocaleDateString()}</span>}
                        <span className="text-indigo-400">{paper.reason}</span>
                      </div>
                    </div>
                    <span className="shrink-0 rounded-full bg-emerald-400/10 px-3 py-1 text-sm text-emerald-200">
                      {Math.round(paper.score * 100)}%
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </motion.div>
        ))}
      </div>
      {!isLoading && data.length === 0 && (
        <div className="mt-12 text-center text-zinc-500">
          No papers in the feed yet.{' '}
          <Link href="/papers" className="text-indigo-400 hover:underline">
            Browse and ingest papers
          </Link>{' '}
          to get started.
        </div>
      )}
    </AppShell>
  );
}
