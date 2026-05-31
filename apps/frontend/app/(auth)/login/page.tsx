'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { useSession } from '@/store/session';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function LoginPage() {
  const router = useRouter();
  const setToken = useSession((s) => s.setToken);
  const [email, setEmail] = useState('founder@arxivcopilot.ai');
  const [password, setPassword] = useState('research');
  const [error, setError] = useState('');
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError('');
    try { const session = await api.login(email, password); setToken(session.access_token); router.push('/dashboard'); }
    catch { setError('Unable to sign in with those credentials.'); }
  }
  return <main className="grid min-h-screen place-items-center grid-bg p-6"><motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}><Card className="w-full max-w-md"><h1 className="text-2xl font-semibold">Welcome back</h1><p className="mt-2 text-sm text-zinc-400">Sign in to your research workspace.</p><form onSubmit={submit} className="mt-6 space-y-4"><input className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2" value={email} onChange={(e) => setEmail(e.target.value)} /><input className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />{error && <p className="text-sm text-red-300">{error}</p>}<Button className="w-full">Sign in</Button></form></Card></motion.div></main>;
}
