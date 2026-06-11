import { AppShell } from '@/components/research/shell';
import { Users, MessageSquare, FileText } from 'lucide-react';

const activity = [
  { author: 'Maya', action: 'annotated retrieval failure cases', paper: 'Graph RAG', time: '2m ago' },
  { author: 'Noah', action: 'resolved methodology comparison', paper: 'Attention Is All You Need', time: '18m ago' },
  { author: 'Lin', action: 'added collaborative summary', paper: 'RAG for Knowledge-Intensive NLP', time: '1h ago' },
  { author: 'Priya', action: 'highlighted key findings', paper: 'Scaling Laws for Neural LMs', time: '2h ago' },
];

export default function WorkspacePage() {
  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">Collaborative</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Team Workspace</h1>
        <p className="text-[#898989]">Shared annotations, summaries, and discussion for your research team.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        {/* Collaborative summary */}
        <div className="p-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="h-4 w-4 text-[#191A23]" />
            <h2 className="font-bold text-[#191A23]">Collaborative Summary</h2>
            <span className="p-tag ml-auto">Graph RAG</span>
          </div>
          <p className="text-sm text-[#898989] leading-relaxed mb-4">
            Graph-aware retrieval improves multi-hop synthesis by grounding generation in citation
            neighborhoods, entity relationships, and benchmark-specific evidence. The open question
            is how to evaluate graph construction quality across domains.
          </p>
          <div className="bg-[#F3F3F3] border border-[#191A23]/10 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare className="h-3.5 w-3.5 text-[#898989]" />
              <span className="text-xs font-medium text-[#191A23]">Comment thread</span>
            </div>
            <p className="text-sm text-[#898989]">
              "Add ablation notes for chunk linking vs citation linking before Friday review."
            </p>
          </div>
        </div>

        {/* Activity feed */}
        <div className="p-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Users className="h-4 w-4 text-[#191A23]" />
            <h2 className="font-bold text-[#191A23]">Live Activity</h2>
            <div className="ml-auto w-2 h-2 rounded-full bg-[#B9FF66] animate-pulse" />
          </div>
          <div className="space-y-3">
            {activity.map((item) => (
              <div key={item.author} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[#191A23] flex items-center justify-center text-white text-xs font-bold shrink-0">
                  {item.author[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[#191A23]">
                    <span className="font-semibold">{item.author}</span> {item.action}
                  </p>
                  <p className="text-xs text-[#898989] truncate">{item.paper} · {item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Shared papers */}
      <div className="mt-6 p-card p-6">
        <h2 className="font-bold text-[#191A23] mb-4">Shared Reading List</h2>
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { title: 'Attention Is All You Need', cat: 'cs.CL', status: 'Read' },
            { title: 'Graph Retrieval-Augmented Generation', cat: 'cs.AI', status: 'In review' },
            { title: 'RAG for Knowledge-Intensive NLP', cat: 'cs.CL', status: 'Annotating' },
          ].map(({ title, cat, status }) => (
            <div key={title} className="bg-[#F3F3F3] border border-[#191A23]/10 rounded-xl p-4">
              <span className="p-tag-gray text-[10px] mb-2 inline-block">{cat}</span>
              <p className="text-sm font-medium text-[#191A23] line-clamp-2 mb-2">{title}</p>
              <div className="flex items-center justify-between">
                <span className={`text-xs font-medium ${
                  status === 'Read' ? 'text-green-600' :
                  status === 'In review' ? 'text-blue-600' : 'text-orange-600'
                }`}>{status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
