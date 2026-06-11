import { AppShell } from '@/components/research/shell';
import { useBookmarks } from '@/store/bookmarks';
import { BookmarkCheck, ExternalLink } from 'lucide-react';

const interests = ['Transformers', 'RAG', 'Graph Neural Networks', 'LLM Alignment', 'Diffusion Models', 'Multimodal AI'];

const topicActivity: Record<string, number> = {
  'cs.AI': 14,
  'cs.CL': 11,
  'cs.LG': 9,
  'cs.CV': 6,
  'stat.ML': 4,
  'cs.RO': 2,
};

export default function ProfilePage() {
  const { bookmarks } = useBookmarks();

  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">You</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Research Profile</h1>
        <p className="text-[#898989]">Your interests and reading activity.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Interests */}
        <div className="p-card p-6">
          <h2 className="font-bold text-[#191A23] mb-4">Interests</h2>
          <div className="flex flex-wrap gap-2">
            {interests.map((interest) => (
              <span key={interest} className="p-tag">{interest}</span>
            ))}
          </div>
        </div>

        {/* Topic activity */}
        <div className="p-card p-6">
          <h2 className="font-bold text-[#191A23] mb-4">Category Activity</h2>
          <div className="space-y-3">
            {Object.entries(topicActivity)
              .sort(([, a], [, b]) => b - a)
              .map(([topic, count]) => {
                const max = Math.max(...Object.values(topicActivity));
                const pct = (count / max) * 100;
                return (
                  <div key={topic} className="flex items-center gap-3">
                    <span className="text-sm text-[#191A23] font-medium w-16 shrink-0">{topic}</span>
                    <div className="flex-1 bg-[#F3F3F3] rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full bg-[#B9FF66] rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-[#898989] w-6 text-right shrink-0">{count}</span>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Bookmarks */}
        <div className="p-card p-6 md:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <BookmarkCheck className="h-4 w-4 text-[#191A23]" />
            <h2 className="font-bold text-[#191A23]">Saved Papers</h2>
            <span className="p-tag-gray ml-auto">{bookmarks.length}</span>
          </div>
          {bookmarks.length === 0 ? (
            <div className="text-center py-8 text-[#898989] text-sm">
              No bookmarks yet. Save papers from the Browse page.
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 gap-3">
              {bookmarks.map((id) => (
                <div key={id} className="flex items-center justify-between bg-[#F3F3F3] border border-[#191A23]/10 rounded-xl px-4 py-3">
                  <span className="text-xs font-mono text-[#191A23] truncate">{id}</span>
                  <a
                    href={`https://arxiv.org/abs/${id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 shrink-0"
                  >
                    <ExternalLink className="h-3.5 w-3.5 text-[#898989] hover:text-[#191A23]" />
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
