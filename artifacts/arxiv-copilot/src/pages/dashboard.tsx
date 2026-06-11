import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { AppShell } from '@/components/research/shell';
import { Card, CardContent } from '@/components/ui/card';
import { v5 } from '@/lib/api';
import { useSession } from '@/store/session';

export default function DashboardPage() {
  const token = useSession((s) => s.token);
  const { data } = useQuery({ queryKey: ['dashboard', token], queryFn: () => v5.dashboard(token) });
  const stats = data?.reading_stats ?? { read: 0, bookmarked: 0, discussed: 0 };
  return (
    <AppShell>
      <div className="mb-8">
        <p className="text-sm text-indigo-200">Research dashboard</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight">Your AI literature command center</h1>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {Object.entries(stats).map(([label, value]) => (
          <motion.div key={label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardContent className="p-5">
                <p className="text-sm capitalize text-zinc-400">{label}</p>
                <p className="mt-3 text-4xl font-semibold">{value}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card>
          <CardContent className="p-5">
            <h2 className="font-medium">Trending topics</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {(data?.trends ?? ['agentic retrieval', 'graph RAG', 'multimodal reasoning']).map((trend) => (
                <span key={trend} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm">
                  {trend}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <h2 className="font-medium">Recommended papers</h2>
            <div className="mt-4 space-y-3">
              {data?.recommended?.map((paper) => (
                <div key={paper.id} className="rounded-xl bg-black/20 p-3">
                  <p className="font-medium">{paper.title}</p>
                  <p className="text-sm text-zinc-400">{paper.summary}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
