import { useQuery } from '@tanstack/react-query';
import { Link } from 'wouter';
import { AppShell } from '@/components/research/shell';
import { arxiv } from '@/lib/api';
import { Loader2 } from 'lucide-react';

const CATS = 'cs.AI,cs.CL,cs.LG,cs.CV';

export default function TrendingPage() {
  const { data = [], isLoading, error } = useQuery({
    queryKey: ['trending', CATS],
    queryFn: () => arxiv.recent(CATS, 20),
    staleTime: 60_000,
    retry: 1,
  });

  return (
    <AppShell>
      <div className="mb-6">
        <span className="p-tag mb-3 inline-block">Updated continuously</span>
        <h1 className="text-3xl font-bold text-[#191A23] mb-1">Trending Papers</h1>
        <p className="text-[#898989] text-sm">
          Most recent preprints across cs.AI, cs.CL, cs.LG, and cs.CV. Click any paper to read its summary.
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-20 text-[#898989]">
          <Loader2 className="h-5 w-5 animate-spin mr-3" /> Loading from arXiv…
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-red-700 text-sm">
          Could not reach arXiv. Please try again.
        </div>
      )}

      <div className="space-y-2.5">
        {data.map((paper, i) => {
          const date = paper.published
            ? new Date(paper.published).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            : null;
          return (
            <Link key={paper.id} href={`/paper/${encodeURIComponent(paper.id)}`}>
              <div className="bg-white border border-[#191A23]/12 rounded-xl p-5 hover:border-[#191A23] hover:shadow-[3px_3px_0px_#191A23] transition-all cursor-pointer">
                <div className="flex items-start gap-4">
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 ${
                      i === 0 ? 'bg-[#B9FF66] text-[#191A23]' : 'bg-[#F3F3F3] text-[#898989]'
                    }`}
                  >
                    {String(i + 1).padStart(2, '0')}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap gap-1.5 mb-1.5">
                      {paper.categories.slice(0, 3).map((c) => (
                        <span key={c} className="p-tag-gray text-[10px]">{c}</span>
                      ))}
                    </div>
                    <h2 className="font-semibold text-[#191A23] leading-snug line-clamp-2 text-sm mb-1">
                      {paper.title}
                    </h2>
                    <p className="text-xs text-[#898989] line-clamp-1">{paper.abstract}</p>
                    <p className="text-xs text-[#898989] mt-1.5">
                      {paper.authors.slice(0, 2).join(', ')}{paper.authors.length > 2 ? ' et al.' : ''}
                      {date && <> · {date}</>}
                    </p>
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </AppShell>
  );
}
