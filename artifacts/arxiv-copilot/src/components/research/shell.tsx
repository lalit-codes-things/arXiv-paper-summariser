import { Link, useLocation } from 'wouter';
import {
  BookOpen, FileText, GitGraph, LayoutDashboard,
  Rss, Search, TrendingUp, Users, User
} from 'lucide-react';
import { CommandPalette } from './command-palette';

const nav = [
  { label: 'Search', href: '/search', Icon: Search },
  { label: 'Papers', href: '/papers', Icon: FileText },
  { label: 'Feed', href: '/feed', Icon: Rss },
  { label: 'Trending', href: '/trending', Icon: TrendingUp },
  { label: 'Dashboard', href: '/dashboard', Icon: LayoutDashboard },
  { label: 'Graph', href: '/graph', Icon: GitGraph },
  { label: 'Workspace', href: '/workspace', Icon: Users },
  { label: 'Profile', href: '/profile', Icon: User },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col fixed inset-y-0 left-0 w-64 bg-[#191A23] z-30">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-6 py-6 border-b border-white/10">
          <div className="w-8 h-8 bg-[#B9FF66] rounded-lg flex items-center justify-center">
            <BookOpen className="h-4 w-4 text-[#191A23]" />
          </div>
          <span className="font-bold text-white text-base tracking-tight">ArXiv Copilot</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {nav.map(({ label, href, Icon }) => {
            const active = location === href || (href !== '/' && location.startsWith(href));
            return (
              <Link key={href} href={href}>
                <div
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                    active
                      ? 'bg-[#B9FF66] text-[#191A23]'
                      : 'text-zinc-400 hover:text-white hover:bg-white/8'
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {label}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Footer hint */}
        <div className="px-5 py-4 border-t border-white/10">
          <div className="text-xs text-zinc-500 flex items-center gap-2">
            <kbd className="bg-white/10 text-zinc-400 px-1.5 py-0.5 rounded text-[10px] font-mono">⌘K</kbd>
            <span>Quick search</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 md:ml-64 min-h-screen bg-[#F3F3F3]">
        <div className="max-w-6xl mx-auto px-6 py-8">
          {children}
        </div>
      </main>

      <CommandPalette />
    </div>
  );
}
