import { AppShell } from '@/components/research/shell';
import { useBookmarks } from '@/store/bookmarks';
import { useAuth } from '@workspace/replit-auth-web';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { useQueries } from '@tanstack/react-query';
import { BookmarkCheck, ExternalLink, Lock, User } from 'lucide-react';
import { Link } from 'wouter';
import { ByokPanel } from '@/components/byok-panel';

function CategoryBar({ counts }: { counts: Record<string, number> }) {
  const entries = Object.entries(counts).sort(([, a], [, b]) => b - a).slice(0, 8);
  if (entries.length === 0) return null;
  const max = entries[0][1];
  return (
    <div className="space-y-3">
      {entries.map(([cat, count]) => (
        <div key={cat} className="flex items-center gap-3">
          <span className="text-sm text-[#191A23] font-medium w-16 shrink-0">{cat}</span>
          <div className="flex-1 bg-[#F3F3F3] rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-[#B9FF66] rounded-full transition-all duration-500"
              style={{ width: `${(count / max) * 100}%` }}
            />
          </div>
          <span className="text-xs text-[#898989] w-4 text-right shrink-0">{count}</span>
        </div>
      ))}
    </div>
  );
}

export default function ProfilePage() {
  const { isAuthenticated, isLoading: authLoading, user, login } = useAuth();
  const { bookmarks } = useBookmarks();

  const paperQueries = useQueries({
    queries: bookmarks.slice(0, 12).map((id) => ({
      queryKey: ['paper', id],
      queryFn: () => arxiv.paper(id),
      staleTime: 60 * 60 * 1000,
      retry: false,
    })),
  });

  if (authLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="w-6 h-6 rounded-full border-2 border-[#B9FF66] border-t-transparent animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (!isAuthenticated) {
    return (
      <AppShell>
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-[#191A23] mb-2">Profile</h1>
          <p className="text-[#898989]">Your research identity.</p>
        </div>
        <div className="p-card p-12 flex flex-col items-center text-center max-w-md mx-auto">
          <div className="w-12 h-12 bg-[#F3F3F3] border border-[#191A23]/10 rounded-2xl flex items-center justify-center mb-4">
            <Lock className="h-6 w-6 text-[#898989]" />
          </div>
          <h2 className="text-xl font-bold text-[#191A23] mb-2">Sign in to see your profile</h2>
          <p className="text-sm text-[#898989] mb-6">
            Your reading stats and bookmarks are tied to your account.
          </p>
          <button onClick={login} className="p-btn-dark">Log in</button>
        </div>
      </AppShell>
    );
  }

  const categoryCounts: Record<string, number> = {};
  for (const q of paperQueries) {
    if (q.data) {
      for (const cat of (q.data as ArxivPaper).categories) {
        categoryCounts[cat] = (categoryCounts[cat] ?? 0) + 1;
      }
    }
  }

  const fetchedPapers = paperQueries.filter((q) => q.data).map((q) => q.data as ArxivPaper);
  const fetchingCategories = paperQueries.some((q) => q.isLoading);
  const hasCategoryData = Object.keys(categoryCounts).length > 0;

  const displayName = [user?.firstName, user?.lastName].filter(Boolean).join(' ') || user?.email || 'Researcher';
  const initials = (user?.firstName?.[0] ?? user?.email?.[0] ?? '?').toUpperCase();

  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">You</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Research Profile</h1>
        <p className="text-[#898989]">Your reading history, saved papers, and settings.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Identity */}
        <div className="p-card p-6 flex items-center gap-4">
          {user?.profileImageUrl ? (
            <img
              src={user.profileImageUrl}
              alt={displayName}
              className="w-16 h-16 rounded-2xl object-cover border border-[#191A23]/10 shrink-0"
            />
          ) : (
            <div className="w-16 h-16 rounded-2xl bg-[#B9FF66] border border-[#191A23] flex items-center justify-center shrink-0">
              <span className="text-2xl font-bold text-[#191A23]">{initials}</span>
            </div>
          )}
          <div className="min-w-0">
            <p className="text-lg font-bold text-[#191A23] truncate">{displayName}</p>
            {user?.email && <p className="text-sm text-[#898989] truncate">{user.email}</p>}
            <p className="text-sm text-[#898989] mt-1">
              <span className="font-semibold text-[#191A23]">{bookmarks.length}</span>{' '}
              saved paper{bookmarks.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {/* Category activity */}
        <div className="p-card p-6">
          <h2 className="font-bold text-[#191A23] mb-4">Category Activity</h2>
          {bookmarks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-6 text-center">
              <User className="h-8 w-8 text-[#898989]/30 mb-2" />
              <p className="text-sm text-[#898989]">Save papers to see your category breakdown.</p>
              <Link href="/papers">
                <span className="text-xs text-[#191A23] font-medium underline underline-offset-2 mt-2 cursor-pointer">
                  Browse papers →
                </span>
              </Link>
            </div>
          ) : fetchingCategories && !hasCategoryData ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-16 h-3 bg-[#F3F3F3] rounded animate-pulse shrink-0" />
                  <div className="flex-1 h-2 bg-[#F3F3F3] rounded-full animate-pulse" />
                </div>
              ))}
            </div>
          ) : hasCategoryData ? (
            <CategoryBar counts={categoryCounts} />
          ) : (
            <p className="text-sm text-[#898989]">Could not load paper data.</p>
          )}
        </div>

        {/* BYOK API Settings */}
        <div className="md:col-span-2">
          <ByokPanel />
        </div>

        {/* Saved papers */}
        <div className="p-card p-6 md:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <BookmarkCheck className="h-4 w-4 text-[#191A23]" />
            <h2 className="font-bold text-[#191A23]">Saved Papers</h2>
            <span className="p-tag-gray ml-auto">{bookmarks.length}</span>
          </div>
          {bookmarks.length === 0 ? (
            <div className="text-center py-8 text-[#898989] text-sm">
              No bookmarks yet.{' '}
              <Link href="/papers">
                <span className="text-[#191A23] font-medium underline underline-offset-2 cursor-pointer">Browse papers</span>
              </Link>{' '}
              and save the ones you want to read.
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 gap-3">
              {bookmarks.map((id) => {
                const paper = fetchedPapers.find((p) => p.arxiv_id === id || p.id === id);
                return (
                  <div
                    key={id}
                    className="flex items-start justify-between bg-[#F3F3F3] border border-[#191A23]/10 rounded-xl px-4 py-3 gap-3"
                  >
                    <div className="min-w-0">
                      {paper ? (
                        <>
                          <p className="text-sm font-medium text-[#191A23] line-clamp-2 leading-snug">{paper.title}</p>
                          <p className="text-xs text-[#898989] mt-1 truncate">
                            {paper.authors[0]}{paper.authors.length > 1 ? ` +${paper.authors.length - 1}` : ''}
                            {' · '}{paper.published?.slice(0, 4)}
                          </p>
                        </>
                      ) : (
                        <span className="text-xs font-mono text-[#898989]">{id}</span>
                      )}
                    </div>
                    <a
                      href={`https://arxiv.org/abs/${id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 mt-0.5"
                    >
                      <ExternalLink className="h-3.5 w-3.5 text-[#898989] hover:text-[#191A23]" />
                    </a>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
