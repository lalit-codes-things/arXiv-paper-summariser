import Link from 'next/link';
import { BookOpen, FileText, GitGraph, LayoutDashboard, Rss, Search, TrendingUp, Users } from 'lucide-react';
import { CommandPalette } from './command-palette';

const nav = [
  ['Dashboard', '/dashboard', LayoutDashboard],
  ['Feed', '/feed', Rss],
  ['Papers', '/papers', FileText],
  ['Search', '/search', Search],
  ['Trending', '/trending', TrendingUp],
  ['Graph', '/graph', GitGraph],
  ['Workspace', '/workspace', Users],
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen grid-bg">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-white/10 bg-black/30 p-5 backdrop-blur-xl md:block">
        <div className="mb-10 flex items-center gap-2 font-semibold"><BookOpen className="h-5 w-5" /> Arxiv Copilot</div>
        <nav className="space-y-2">{nav.map(([label, href, Icon]) => <Link key={href} href={href} className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-zinc-300 hover:bg-white/10 hover:text-white"><Icon className="h-4 w-4" />{label}</Link>)}</nav>
        <div className="absolute bottom-5 left-5 right-5 rounded-xl border border-emerald-400/20 bg-emerald-400/10 p-3 text-xs text-emerald-100">Press ⌘K to search papers</div>
      </aside>
      <section className="md:pl-64"><div className="mx-auto max-w-7xl p-6 md:p-10">{children}</div></section>
      <CommandPalette />
    </main>
  );
}
