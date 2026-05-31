'use client';
import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { v3 } from '@/lib/api';
import { useBookmarks } from '@/store/bookmarks';

type Message = { role: 'user' | 'assistant'; content: string };

export default function PaperPage({ params }: { params: { id: string } }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const { toggle, has } = useBookmarks();

  const { data: paper } = useQuery({ queryKey: ['paper', params.id], queryFn: () => v3.paper(params.id) });
  const { data: related } = useQuery({ queryKey: ['related', params.id], queryFn: () => v3.related(params.id, 5), enabled: !!paper });

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const message = input;
    const userMsg: Message = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await v3.chat(params.id, message, history);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.answer }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Error getting response. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  if (!paper) {
    return <AppShell><div className="text-center text-zinc-500 mt-20">Loading paper…</div></AppShell>;
  }

  return (
    <AppShell>
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <div>
          <div className="flex flex-wrap gap-2 mb-3">{paper.topics.map((t) => <span key={t} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-zinc-400">{t}</span>)}</div>
          <h1 className="text-3xl font-semibold leading-tight">{paper.title}</h1>
          <p className="mt-2 text-sm text-zinc-500">{paper.authors.join(', ')}{paper.published_at && <> &middot; {new Date(paper.published_at).getFullYear()}</>}</p>
          <Card className="mt-6"><h2 className="font-medium mb-3">Abstract</h2><p className="text-zinc-300 text-sm leading-relaxed">{paper.abstract}</p></Card>
          {paper.summary && <Card className="mt-4"><h2 className="font-medium mb-3">AI Summary</h2><p className="text-zinc-300 text-sm leading-relaxed">{paper.summary}</p></Card>}
          <div className="mt-4 flex flex-wrap gap-3">
            <button onClick={() => toggle(paper.id)} className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10">{has(paper.id) ? '★ Saved' : '☆ Save'}</button>
            <a href={`https://arxiv.org/abs/${paper.arxiv_id}`} target="_blank" rel="noopener noreferrer" className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10">View on arXiv ↗</a>
            <a href={`https://arxiv.org/pdf/${paper.arxiv_id}`} target="_blank" rel="noopener noreferrer" className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10">Download PDF ↗</a>
          </div>
        </div>
        <div className="flex flex-col gap-4">
          <Card className="flex flex-col h-[520px]"><h2 className="font-medium mb-3 shrink-0">Ask about this paper</h2><div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {messages.length === 0 && <div className="text-sm text-zinc-500 mt-4 text-center">Ask anything about methodology, findings, or limitations.</div>}
            {messages.map((m, i) => <div key={i} className={`rounded-xl px-3 py-2 text-sm ${m.role === 'user' ? 'ml-4 bg-indigo-500/20 text-white' : 'mr-4 bg-white/5 text-zinc-200'}`}>{m.content}</div>)}
            {loading && <div className="mr-4 rounded-xl bg-white/5 px-3 py-2 text-sm text-zinc-400 animate-pulse">Thinking…</div>}
            <div ref={bottomRef} />
          </div><div className="mt-3 flex gap-2 shrink-0"><input className="flex-1 rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm outline-none focus:border-indigo-400" placeholder="What is the main contribution?" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()} /><Button onClick={send} disabled={loading} className="shrink-0">Send</Button></div></Card>
          {related && related.results.length > 0 && <Card><h2 className="font-medium mb-3">Related papers</h2><div className="space-y-3">{related.results.slice(0, 4).map((r) => <a key={r.paper.id} href={`/papers/${r.paper.id}`} className="block rounded-xl bg-black/20 p-3 hover:bg-black/30 transition-colors"><p className="text-sm font-medium line-clamp-2">{r.paper.title}</p><p className="mt-1 text-xs text-zinc-500">{Math.round(r.score * 100)}% similar</p></a>)}</div></Card>}
        </div>
      </div>
    </AppShell>
  );
}
