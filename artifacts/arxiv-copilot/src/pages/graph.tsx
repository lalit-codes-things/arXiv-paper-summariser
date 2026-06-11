import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { GraphCanvas } from '@/components/research/graph-canvas';
import { v5 } from '@/lib/api';

export default function GraphPage() {
  const { data } = useQuery({ queryKey: ['graph'], queryFn: v5.graph });
  return (
    <AppShell>
      <h1 className="text-4xl font-semibold">Paper relationship graph</h1>
      <p className="mt-2 text-zinc-400">
        Explore methods, citations, benchmarks, and conceptual clusters interactively.
      </p>
      <div className="mt-8">{data && <GraphCanvas graph={data} />}</div>
    </AppShell>
  );
}
