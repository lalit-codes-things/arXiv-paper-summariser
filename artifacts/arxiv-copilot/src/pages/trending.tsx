import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { ExternalLink, Loader2, TrendingUp } from 'lucide-react';

const TRENDING_CATS = 'cs.AI,cs.CL,cs.LG,cs.CV';

function TrendingRow({ paper, rank }: { paper: ArxivPaper; rank: number }) {
  const date = paper.published ? new Date(paper.published) : null;
  const dateStr = date
    ? date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    : null;

  return (
    <div className="p-card p-5 hover:shadow-[4px_4px_0px_#191A23] transition-shadow">
      <div className="flex items-start gap-4">
        <div
          className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm shrink-0 ${
            rank === 1 ? 'bg-[#B9FF66] text-[#191A23]' :
            rank === 2 ? 'bg-[#191A23] text-white' :
            rank === 3 ? 'bg-[#191A23]/70 text-white' :
            'bg-[#F3F3F3] text-[#898989]'
          }`}
        >
          {String(rank).padStart(2, '0')}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap gap-1.5 mb-2">
            {paper.categories.slice(0, 3).map((c) => (
              <span key={c} className="p-tag-gray text-[10px]">{c}</span>
            ))}
          </div>
          <h2 className="font-semibold text-[#191A23] leading-snug mb-1 line-clamp-2">{paper.title}</h2>
          <p className="text-sm text-[#898989] line-clamp-2 mb-3">{paper.abstract}</p>
          <div className="flex items-center justify-between">
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
              arXiv <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TrendingPage() {
  const { data = [], isLoading, error } = useQuery({
    queryKey: ['trending', TRENDING_CATS],
    queryFn: () => arxiv.recent(TRENDING_CATS, 20),
    staleTime: 60_000,
    retry: 1,
  });

  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">Updated hourly</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Trending Papers</h1>
        <p className="text-[#898989]">Most recent preprints from cs.AI, cs.CL, cs.LG, and cs.CV.</p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-24 text-[#898989]">
          <Loader2 className="h-6 w-6 animate-spin mr-3" /> Loading from arXiv...
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700 text-sm">
          Could not reach arXiv. Please try again.
        </div>
      )}

      {!isLoading && data.length === 0 && !error && (
        <div className="p-card p-10 text-center">
          <TrendingUp className="h-10 w-10 text-[#B9FF66] mx-auto mb-4" />
          <p className="text-[#898989]">No papers loaded.</p>
        </div>
      )}

      <div className="space-y-3">
        {data.map((paper, i) => <TrendingRow key={paper.id} paper={paper} rank={i + 1} />)}
      </div>
    </AppShell>
  );
}
