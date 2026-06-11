import { Link, useLocation } from 'wouter';
import {
  BookOpen, FileText, GitGraph, LayoutDashboard,
  Rss, Search, TrendingUp, Users, User, LogIn, LogOut,
} from 'lucide-react';
import { CommandPalette } from './command-palette';
import { useAuth } from '@workspace/replit-auth-web';

const nav = [
  { label: 'Search', href: '/search', Icon: Search },
  { label: 'Browse Papers', href: '/papers', Icon: FileText },
  { label: 'Feed', href: '/feed', Icon: Rss },
  { label: 'Trending', href: '/trending', Icon: TrendingUp },
  { label: 'Dashboard', href: '/dashboard', Icon: LayoutDashboard },
  { label: 'Knowledge Graph', href: '/graph', Icon: GitGraph },
  { label: 'Workspace', href: '/workspace', Icon: Users },
  { label: 'Profile', href: '/profile', Icon: User },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const { isAuthenticated, user, login, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col fixed inset-y-0 left-0 w-60 bg-[#191A23] z-30">
        {/* Logo — always goes home */}
        <Link href="/">
          <div className="flex items-center gap-2.5 px-5 py-5 border-b border-white/10 cursor-pointer hover:opacity-80 transition-opacity">
            <div className="w-7 h-7 bg-[#B9FF66] rounded-lg flex items-center justify-center shrink-0">
              <BookOpen className="h-3.5 w-3.5 text-[#191A23]" />
            </div>
            <span className="font-bold text-white text-sm leading-tight">ArXiv Paper<br />Summariser</span>
          </div>
        </Link>

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

        {/* Footer — auth */}
        <div className="px-3 pb-4 space-y-0.5 border-t border-white/10 pt-3">
          {isAuthenticated ? (
            <>
              <div className="flex items-center gap-2.5 px-3 py-2">
                <div className="w-6 h-6 rounded-full bg-[#B9FF66] flex items-center justify-center text-[#191A23] text-xs font-bold shrink-0">
                  {(user?.firstName?.[0] ?? user?.email?.[0] ?? '?').toUpperCase()}
                </div>
                <span className="text-xs text-white truncate flex-1">
                  {user?.firstName ?? user?.email ?? 'Account'}
                </span>
              </div>
              <button
                onClick={logout}
                className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-zinc-400 hover:text-white hover:bg-white/8 transition-all cursor-pointer"
              >
                <LogOut className="h-4 w-4 shrink-0" />
                Log out
              </button>
            </>
          ) : (
            <button
              onClick={login}
              className={`flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                location === '/login' ? 'bg-[#B9FF66] text-[#191A23]' : 'text-zinc-400 hover:text-white hover:bg-white/8'
              }`}
            >
              <LogIn className="h-4 w-4 shrink-0" />
              Log in
            </button>
          )}
          <div className="flex items-center gap-2 px-3 pt-2">
            <kbd className="bg-white/10 text-zinc-400 px-1.5 py-0.5 rounded text-[10px] font-mono">⌘K</kbd>
            <span className="text-xs text-zinc-500">Quick search</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 md:ml-60 min-h-screen bg-[#F3F3F3]">
        <div className="max-w-5xl mx-auto px-6 py-8">
          {children}
        </div>
      </main>

      <CommandPalette />
    </div>
  );
}
