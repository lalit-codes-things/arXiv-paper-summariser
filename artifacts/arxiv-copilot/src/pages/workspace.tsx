import { AppShell } from '@/components/research/shell';
import { FileText, Bookmark, Lock } from 'lucide-react';
import { useAuth } from '@workspace/replit-auth-web';
import { useBookmarks } from '@/store/bookmarks';
import { Link } from 'wouter';
import { useState, useEffect } from 'react';

const NOTES_KEY = 'arxiv_workspace_notes';

export default function WorkspacePage() {
  const { isAuthenticated, isLoading, user, login } = useAuth();
  const { bookmarks } = useBookmarks();
  const [notes, setNotes] = useState(() => {
    try { return localStorage.getItem(NOTES_KEY) ?? ''; } catch { return ''; }
  });

  useEffect(() => {
    try { localStorage.setItem(NOTES_KEY, notes); } catch { /* noop */ }
  }, [notes]);

  if (isLoading) {
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
          <h1 className="text-4xl font-bold text-[#191A23] mb-2">Workspace</h1>
          <p className="text-[#898989]">Your personal research notebook.</p>
        </div>
        <div className="p-card p-12 flex flex-col items-center text-center max-w-md mx-auto">
          <div className="w-12 h-12 bg-[#F3F3F3] border border-[#191A23]/10 rounded-2xl flex items-center justify-center mb-4">
            <Lock className="h-6 w-6 text-[#898989]" />
          </div>
          <h2 className="text-xl font-bold text-[#191A23] mb-2">Sign in to use the workspace</h2>
          <p className="text-sm text-[#898989] mb-6">
            Your notes and reading history are saved to your account so they follow you across devices.
          </p>
          <button onClick={login} className="p-btn-dark">
            Log in
          </button>
        </div>
      </AppShell>
    );
  }

  const name = user?.firstName ?? user?.email?.split('@')[0] ?? 'Researcher';

  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">Personal</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Workspace</h1>
        <p className="text-[#898989]">Welcome back, {name}.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        {/* Notes */}
        <div className="p-card p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="h-4 w-4 text-[#191A23]" />
            <h2 className="font-bold text-[#191A23]">Research Notes</h2>
            <span className="ml-auto text-xs text-[#898989]">Saved locally</span>
          </div>
          <textarea
            className="flex-1 min-h-[200px] w-full resize-none bg-[#F3F3F3] border border-[#191A23]/10 rounded-xl p-4 text-sm text-[#191A23] placeholder-[#898989] focus:outline-none focus:ring-2 focus:ring-[#B9FF66]"
            placeholder="Jot down paper summaries, open questions, or ideas…"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        {/* Bookmarks */}
        <div className="p-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Bookmark className="h-4 w-4 text-[#191A23]" />
            <h2 className="font-bold text-[#191A23]">Saved Papers</h2>
            <span className="p-tag ml-auto">{bookmarks.length}</span>
          </div>
          {bookmarks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <Bookmark className="h-8 w-8 text-[#898989]/40 mb-3" />
              <p className="text-sm text-[#898989]">No saved papers yet.</p>
              <Link href="/papers">
                <span className="text-xs text-[#191A23] font-medium underline underline-offset-2 mt-2 cursor-pointer">
                  Browse papers →
                </span>
              </Link>
            </div>
          ) : (
            <div className="space-y-2 max-h-72 overflow-y-auto">
              {bookmarks.map((id) => (
                <Link key={id} href={`/paper/${encodeURIComponent(id)}`}>
                  <div className="bg-[#F3F3F3] border border-[#191A23]/10 rounded-xl p-3 cursor-pointer hover:border-[#191A23]/30 transition-colors">
                    <p className="text-sm font-medium text-[#191A23] font-mono">{id}</p>
                    <p className="text-xs text-[#898989] mt-1">View paper →</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
