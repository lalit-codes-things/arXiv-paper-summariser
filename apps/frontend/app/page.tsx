import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function Home() {
  return <main className="min-h-screen grid-bg p-8"><section className="mx-auto flex min-h-[85vh] max-w-5xl flex-col items-center justify-center text-center"><div className="mb-4 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-zinc-300">V5 production research SaaS</div><h1 className="max-w-4xl text-5xl font-semibold tracking-tight md:text-7xl">Research papers, teams, graphs, and AI chat in one fast workspace.</h1><p className="mt-6 max-w-2xl text-lg text-zinc-400">A Linear-fast, Notion-clear, Perplexity-inspired copilot for arXiv discovery and collaborative reading.</p><div className="mt-8 flex gap-3"><Link href="/dashboard"><Button>Open dashboard</Button></Link><Link href="/login"><Button className="bg-white/10 text-white hover:bg-white/20">Sign in</Button></Link></div></section></main>;
}
