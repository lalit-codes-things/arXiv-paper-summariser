import { useState, useEffect } from 'react';
import { useSearch, Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { Loader2 } from 'lucide-react';

const CATEGORIES = [
  { id: 'cs.AI', label: 'Artificial Intelligence' },
  { id: 'cs.CL', label: 'Computation & Language' },
  { id: 'cs.LG', label: 'Machine Learning' },
  { id: 'cs.CV', label: 'Computer Vision' },
  { id: 'stat.ML', label: 'Stats ML' },
  { id: 'cs.RO', label: 'Robotics' },
  { id: 'cs.IR', label: 'Information Retrieval' },
  { id: 'eess.AS', label: 'Audio & Speech' },
];

function PaperRow({ paper }: { paper: ArxivPaper }) {
  const year = paper.published ? new Date(paper.published).getFullYear() : null;
  const month = paper.published
    ? new Date(paper.published).toLocaleDateString('en-US', { month: 'short' })
    : null;

  return (
    <Link href={`/paper/${encodeURIComponent(paper.id)}`}>
      <div className="bg-white border border-[#191A23]/12 rounded-xl p-5 hover:border-[#191A23] hover:shadow-[3px_3px_0px_#191A23] transition-all cursor-pointer">
        <div className="flex items-start gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap gap-1.5 mb-2">
              {paper.categories.slice(0, 3).map((c) => (
                <span key={c} className="p-tag-gray text-[10px]">{c}</span>
              ))}
            </div>
            <h2 className="font-semibold text-[#191A23] leading-snug line-clamp-2 text-sm mb-2">
              {paper.title}
            </h2>
            <p className="text-xs text-[#898989] line-clamp-2 leading-relaxed mb-2">{paper.abstract}</p>
            <p className="text-xs text-[#898989]">
              {paper.authors.slice(0, 2).join(', ')}{paper.authors.length > 2 ? ' et al.' : ''}
              {year && month && <> · {month} {year}</>}
            </p>
          </div>
          <div className="text-xs text-[#191A23] font-medium shrink-0 bg-[#B9FF66] rounded-lg px-2.5 py-1 whitespace-nowrap">
            Read →
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function PapersPage() {
  const searchStr = useSearch();
  const params = new URLSearchParams(searchStr);
  const [category, setCategory] = useState(params.get('cat') ?? 'cs.AI');

  useEffect(() => {
    const cat = params.get('cat');
    if (cat) setCategory(cat);
  }, [searchStr]);

  const { data = [], isFetching, error } = useQuery({
    queryKey: ['papers', category],
    queryFn: () => arxiv.category(category, 30),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const catLabel = CATEGORIES.find((c) => c.id === category)?.label ?? category;

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-[#191A23] mb-1">Browse Papers</h1>
        <p className="text-[#898989] text-sm">Latest preprints from arXiv, updated continuously. Click any paper to read its summary.</p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        {CATEGORIES.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setCategory(id)}
            className={`rounded-full px-3.5 py-1.5 text-xs font-medium border transition-all ${
              category === id
                ? 'bg-[#191A23] text-white border-[#191A23]'
                : 'bg-white text-[#191A23] border-[#191A23]/20 hover:border-[#191A23]'
            }`}
          >
            {id} <span className="opacity-60">· {label}</span>
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-[#898989]">
          {!isFetching && data.length > 0
            ? <><span className="font-medium text-[#191A23]">{data.length}</span> latest {catLabel} papers</>
            : `Latest ${catLabel} papers`}
        </p>
        {isFetching && (
          <div className="flex items-center gap-2 text-xs text-[#898989]">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Fetching from arXiv…
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-red-700 text-sm">
          Could not reach arXiv. Please try again.
        </div>
      )}

      {isFetching && data.length === 0 && (
        <div className="flex items-center justify-center py-20 text-[#898989]">
          <Loader2 className="h-5 w-5 animate-spin mr-3" /> Loading from arXiv…
        </div>
      )}

      <div className="space-y-2.5">
        {data.map((paper) => <PaperRow key={paper.id} paper={paper} />)}
      </div>
    </AppShell>
  );
}
