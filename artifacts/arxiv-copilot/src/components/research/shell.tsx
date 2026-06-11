import { Link, useLocation } from 'wouter';
import {
  BookOpen, FileText, GitGraph, LayoutDashboard,
  Rss, Search, TrendingUp, Users, User, LogIn, LogOut,
} from 'lucide-react';
import { useUser, useClerk } from '@clerk/react';

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

const basePath = import.meta.env.BASE_URL.replace(/\/$/, '');

export function AppShell({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const { user, isLoaded, isSignedIn } = useUser();
  const { signOut } = useClerk();

  const initials = (
    user?.firstName?.[0] ??
    user?.emailAddresses?.[0]?.emailAddress?.[0] ??
    '?'
  ).toUpperCase();

  const displayName =
    [user?.firstName, user?.lastName].filter(Boolean).join(' ') ||
    user?.emailAddresses?.[0]?.emailAddress ||
    'Account';

  return (
    <div className="flex min-h-screen bg-[#F3F3F3]">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col fixed inset-y-0 left-0 w-60 bg-white border-r border-[#191A23] z-30">

        {/* Logo */}
        <Link href="/">
          <div className="flex items-center gap-2.5 px-5 py-5 border-b border-[#191A23] cursor-pointer hover:bg-[#F3F3F3] transition-colors">
            <div className="w-7 h-7 bg-[#B9FF66] border border-[#191A23] rounded-lg flex items-center justify-center shrink-0">
              <BookOpen className="h-3.5 w-3.5 text-[#191A23]" />
            </div>
            <span className="font-bold text-[#191A23] text-sm leading-tight">ArXiv Paper<br />Summariser</span>
          </div>
        </Link>

        {/* Nav */}
        <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
          {nav.map(({ label, href, Icon }) => {
            const active = location === href || (href !== '/' && location.startsWith(href));
            return (
              <Link key={href} href={href}>
                <div className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                  active
                    ? 'bg-[#B9FF66] text-[#191A23] border border-[#191A23]'
                    : 'text-[#191A23] hover:bg-[#F3F3F3]'
                }`}>
                  <Icon className="h-4 w-4 shrink-0" />
                  {label}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-3 pb-4 pt-3 border-t border-[#191A23]">
          {isLoaded && isSignedIn ? (
            <div className="space-y-0.5">
              <div className="flex items-center gap-2.5 px-3 py-2">
                {user?.imageUrl ? (
                  <img src={user.imageUrl} alt={displayName} className="w-6 h-6 rounded-full border border-[#191A23] shrink-0 object-cover" />
                ) : (
                  <div className="w-6 h-6 rounded-full bg-[#B9FF66] border border-[#191A23] flex items-center justify-center text-[#191A23] text-xs font-bold shrink-0">
                    {initials}
                  </div>
                )}
                <span className="text-xs text-[#191A23] font-medium truncate flex-1">{displayName}</span>
              </div>
              <button
                onClick={() => signOut({ redirectUrl: basePath || '/' })}
                className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-[#191A23] hover:bg-[#F3F3F3] transition-colors cursor-pointer"
              >
                <LogOut className="h-4 w-4 shrink-0" />
                Log out
              </button>
            </div>
          ) : (
            <Link href="/sign-in">
              <div className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors cursor-pointer ${
                location === '/sign-in'
                  ? 'bg-[#B9FF66] text-[#191A23] border border-[#191A23]'
                  : 'text-[#191A23] hover:bg-[#F3F3F3]'
              }`}>
                <LogIn className="h-4 w-4 shrink-0" />
                Log in
              </div>
            </Link>
          )}
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 md:ml-60 min-h-screen bg-[#F3F3F3]">
        <div className="max-w-5xl mx-auto px-6 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
