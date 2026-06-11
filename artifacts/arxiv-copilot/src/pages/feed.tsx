import { useQuery } from '@tanstack/react-query';
import { Link } from 'wouter';
import { AppShell } from '@/components/research/shell';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { ExternalLink, Loader2, Rss } from 'lucide-react';

const FEED_CATS = 'cs.AI,cs.CL,cs.LG';

function FeedItem({ paper, index }: { paper: ArxivPaper; index: number }) {
  const date = paper.published ? new Date(paper.published) : null;
  const dateStr = date
    ? date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : null;

  return (
    <div className="p-card p-5 hover:shadow-[4px_4px_0px_#191A23] transition-shadow">
      <div className="flex gap-4">
        <div className="w-10 h-10 bg-[#B9FF66] rounded-xl flex items-center justify-center text-[#191A23] font-bold text-sm shrink-0">
          {index + 1}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap gap-1.5 mb-2">
            {paper.categories.slice(0, 3).map((c) => (
              <span key={c} className="p-tag-gray text-[10px]">{c}</span>
            ))}
          </div>
          <h2 className="font-semibold text-[#191A23] leading-snug mb-2 line-clamp-2">{paper.title}</h2>
          <p className="text-sm text-[#898989] line-clamp-2 leading-relaxed">{paper.abstract}</p>
          <div className="flex items-center justify-between mt-3">
            <div className="text-xs text-[#898989]">
              {paper.authors.slice(0, 2).join(', ')}{paper.authors.length > 2 ? ' et al.' : ''}
              {dateStr && <> · {dateStr}</>}
            </div>
            <a
              href={paper.abs_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-btn-dark text-xs px-3 py-1.5"
            >
              Read <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FeedPage() {
  const { data = [], isLoading, error } = useQuery({
    queryKey: ['feed', FEED_CATS],
    queryFn: () => arxiv.recent(FEED_CATS, 20),
    staleTime: 30_000,
    retry: 1,
  });

  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">cs.AI · cs.CL · cs.LG</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Research Feed</h1>
        <p className="text-[#898989]">Latest preprints from top AI and ML categories on arXiv.</p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-24 text-[#898989]">
          <Loader2 className="h-6 w-6 animate-spin mr-3" /> Loading feed from arXiv...
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700 text-sm">
          Could not reach arXiv. Please try again.
        </div>
      )}

      {!isLoading && data.length === 0 && !error && (
        <div className="p-card p-10 text-center">
          <Rss className="h-10 w-10 text-[#B9FF66] mx-auto mb-4" />
          <p className="text-[#898989]">No papers loaded yet.</p>
        </div>
      )}

      <div className="space-y-3">
        {data.map((paper, i) => <FeedItem key={paper.id} paper={paper} index={i} />)}
      </div>

      {data.length > 0 && (
        <div className="mt-8 text-center">
          <Link href="/papers">
            <button className="p-btn-outline px-6 py-2.5">Browse more by category →</button>
          </Link>
        </div>
      )}
    </AppShell>
  );
}
