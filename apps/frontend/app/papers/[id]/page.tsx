'use client';
import { useState } from 'react';
import { AppShell } from '@/components/research/shell';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { api } from '@/lib/api';
import { useSession } from '@/store/session';

export default function PaperChatPage({ params }: { params: { id: string } }) {
  const token = useSession((s) => s.token);
  const [message, setMessage] = useState('Compare this paper methodology against recent graph RAG work.');
  const [answer, setAnswer] = useState('');
  async function ask() { const response = await api.chat(params.id, message, token); setAnswer(response.answer); }
  return <AppShell><h1 className="text-4xl font-semibold">AI paper chat</h1><p className="mt-2 text-zinc-400">Ask about methodology, findings, limitations, and adjacent work.</p><Card className="mt-8"><textarea className="min-h-28 w-full rounded-xl border border-white/10 bg-black/30 p-3" value={message} onChange={(event) => setMessage(event.target.value)} /><Button onClick={ask} className="mt-4">Ask copilot</Button>{answer && <div className="mt-6 rounded-xl bg-white/5 p-4 text-zinc-200">{answer}</div>}</Card></AppShell>;
}
