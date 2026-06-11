import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { arxiv } from '@/lib/api';
import { useBookmarks } from '@/store/bookmarks';
import { BookmarkCheck, FileText, Search, TrendingUp, ExternalLink, Loader2 } from 'lucide-react';
import { Link } from 'wouter';

export default function DashboardPage() {
  const { bookmarks } = useBookmarks();

  const { data: recent = [], isLoading } = useQuery({
    queryKey: ['dashboard-recent'],
    queryFn: () => arxiv.recent('cs.AI,cs.CL', 6),
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

  const { data: cvPapers = [] } = useQuery({
    queryKey: ['dashboard-cv'],
    queryFn: () => arxiv.category('cs.CV', 5),
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

  const stats = [
    { label: 'Bookmarked', value: bookmarks.length, Icon: BookmarkCheck, color: '#B9FF66' },
    { label: 'Categories', value: '200+', Icon: FileText, color: '#191A23' },
    { label: 'Daily Preprints', value: '~1,500', Icon: TrendingUp, color: '#191A23' },
    { label: 'Search Index', value: '2M+', Icon: Search, color: '#191A23' },
  ];

  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">Overview</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Dashboard</h1>
        <p className="text-[#898989]">Your research command center.</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, Icon, color }) => (
          <div key={label} className="p-card p-5">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center mb-3"
              style={{ backgroundColor: color }}
            >
              <Icon className="h-4 w-4" style={{ color: color === '#B9FF66' ? '#191A23' : '#fff' }} />
            </div>
            <div className="text-2xl font-bold text-[#191A23]">{value}</div>
            <div className="text-xs text-[#898989] mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent AI papers */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-[#191A23] text-lg">Latest cs.AI</h2>
            <Link href="/papers?cat=cs.AI">
              <button className="p-btn-outline text-xs px-3 py-1.5">View all →</button>
            </Link>
          </div>
          {isLoading ? (
            <div className="flex justify-center py-8 text-[#898989]">
              <Loader2 className="h-5 w-5 animate-spin" />
            </div>
          ) : (
            <div className="space-y-3">
              {recent.slice(0, 5).map((paper) => (
                <div key={paper.id} className="p-card p-4 hover:shadow-[3px_3px_0px_#191A23] transition-shadow">
                  <h3 className="text-sm font-medium text-[#191A23] line-clamp-2 mb-1">{paper.title}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[#898989]">
                      {paper.authors[0]}{paper.authors.length > 1 ? ' et al.' : ''}
                      {paper.published && ` · ${new Date(paper.published).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`}
                    </span>
                    <a href={paper.abs_url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-3.5 w-3.5 text-[#898989] hover:text-[#191A23]" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right col */}
        <div className="space-y-6">
          {/* Bookmarks */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-[#191A23] text-lg">Saved Papers</h2>
              <span className="p-tag-gray text-xs">{bookmarks.length} saved</span>
            </div>
            {bookmarks.length === 0 ? (
              <div className="p-card p-6 text-center text-[#898989] text-sm">
                <BookmarkCheck className="h-8 w-8 text-[#B9FF66] mx-auto mb-2" />
                No bookmarks yet. Save papers from the Browse page.
              </div>
            ) : (
              <div className="space-y-2">
                {bookmarks.slice(0, 5).map((id) => (
                  <div key={id} className="p-card p-3 text-sm text-[#191A23] flex items-center justify-between gap-2">
                    <span className="text-xs font-mono text-[#898989] truncate">{id}</span>
                    <a href={`https://arxiv.org/abs/${id}`} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-3.5 w-3.5 text-[#898989] hover:text-[#191A23] shrink-0" />
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Latest cs.CV */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-[#191A23] text-lg">Latest cs.CV</h2>
              <Link href="/papers?cat=cs.CV">
                <button className="p-btn-outline text-xs px-3 py-1.5">View all →</button>
              </Link>
            </div>
            <div className="space-y-2">
              {cvPapers.slice(0, 4).map((paper) => (
                <div key={paper.id} className="p-card p-4 hover:shadow-[3px_3px_0px_#191A23] transition-shadow">
                  <h3 className="text-sm font-medium text-[#191A23] line-clamp-1 mb-1">{paper.title}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[#898989]">
                      {paper.authors[0]}{paper.authors.length > 1 ? ' et al.' : ''}
                    </span>
                    <a href={paper.abs_url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-3.5 w-3.5 text-[#898989] hover:text-[#191A23]" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
