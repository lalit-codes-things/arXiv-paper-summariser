import { AppShell } from '@/components/research/shell';
import { Card, CardContent } from '@/components/ui/card';

const activity = [
  { author: 'Maya', action: 'annotated retrieval failure cases', paper: 'Graph Retrieval-Augmented Generation' },
  { author: 'Noah', action: 'resolved methodology comparison', paper: 'Attention Is All You Need' },
  { author: 'Lin', action: 'added a collaborative summary', paper: 'RAG for Knowledge-Intensive NLP' },
];

export default function WorkspacePage() {
  return (
    <AppShell>
      <h1 className="text-4xl font-semibold">Team workspace</h1>
      <p className="mt-2 text-zinc-400">
        Shared annotations, collaborative summaries, comments, and realtime presence for research teams.
      </p>
      <div className="mt-8 grid gap-4 lg:grid-cols-[1.3fr_.7fr]">
        <Card>
          <CardContent className="p-5">
            <h2 className="font-medium">Collaborative summary</h2>
            <p className="mt-4 text-zinc-300">
              Graph-aware retrieval improves multi-hop synthesis by grounding generation in citation neighborhoods,
              entity relationships, and benchmark-specific evidence. The open question is how to evaluate graph
              construction quality across domains.
            </p>
            <div className="mt-6 rounded-xl border border-white/10 bg-black/20 p-4 text-sm text-zinc-400">
              Comment thread: "Add ablation notes for chunk linking vs citation linking before Friday review."
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <h2 className="font-medium">Live activity</h2>
            <div className="mt-4 space-y-3">
              {activity.map((item) => (
                <div key={item.author} className="rounded-xl bg-white/5 p-3 text-sm">
                  <span className="text-white">{item.author}</span> {item.action}
                  <p className="text-zinc-500">{item.paper}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
