import { useState, useEffect } from 'react';
import { useSearch } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { ExternalLink, FileText, Loader2, BookmarkPlus, BookmarkCheck } from 'lucide-react';
import { useBookmarks } from '@/store/bookmarks';

const CATEGORIES = [
  { id: 'cs.AI', label: 'AI' },
  { id: 'cs.CL', label: 'Computation & Language' },
  { id: 'cs.LG', label: 'Machine Learning' },
  { id: 'cs.CV', label: 'Computer Vision' },
  { id: 'stat.ML', label: 'Stats ML' },
  { id: 'cs.RO', label: 'Robotics' },
  { id: 'cs.IR', label: 'Information Retrieval' },
  { id: 'eess.AS', label: 'Audio & Speech' },
];

function PaperCard({ paper }: { paper: ArxivPaper }) {
  const { toggle, has } = useBookmarks();
  const saved = has(paper.id);
  const year = paper.published ? new Date(paper.published).getFullYear() : null;

  return (
    <div className="p-card p-6 flex flex-col gap-3 hover:shadow-[4px_4px_0px_#191A23] transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap gap-1.5">
          {paper.categories.slice(0, 2).map((c) => (
            <span key={c} className="p-tag-gray text-[10px]">{c}</span>
          ))}
        </div>
        <button
          onClick={() => toggle(paper.id)}
          className="shrink-0 text-[#898989] hover:text-[#191A23] transition-colors"
          title={saved ? 'Remove bookmark' : 'Bookmark'}
        >
          {saved ? <BookmarkCheck className="h-4 w-4 text-[#B9FF66]" /> : <BookmarkPlus className="h-4 w-4" />}
        </button>
      </div>
      <h2 className="font-semibold text-[#191A23] leading-snug line-clamp-2 text-sm">{paper.title}</h2>
      <p className="text-xs text-[#898989] leading-relaxed line-clamp-3">{paper.abstract}</p>
      <div className="text-xs text-[#898989] mt-auto">
        {paper.authors.slice(0, 2).join(', ')}{paper.authors.length > 2 ? ' et al.' : ''}
        {year ? ` · ${year}` : ''}
      </div>
      <div className="flex gap-2 pt-1">
        <a href={paper.abs_url} target="_blank" rel="noopener noreferrer" className="p-btn-dark text-xs px-3 py-1.5 flex-1 justify-center">
          Abstract <ExternalLink className="h-3 w-3" />
        </a>
        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="p-btn-outline text-xs px-3 py-1.5 flex-1 justify-center">
          PDF <FileText className="h-3 w-3" />
        </a>
      </div>
    </div>
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
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">Live from arXiv</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Browse Papers</h1>
        <p className="text-[#898989]">Latest preprints by category, updated continuously.</p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        {CATEGORIES.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setCategory(id)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium border transition-all ${
              category === id
                ? 'bg-[#191A23] text-white border-[#191A23]'
                : 'bg-white text-[#191A23] border-[#191A23]/20 hover:border-[#191A23]'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Results header */}
      <div className="flex items-center justify-between mb-5">
        <div className="text-sm text-[#898989]">
          Showing latest <span className="font-medium text-[#191A23]">{catLabel}</span> papers
          {!isFetching && data.length > 0 && <> · {data.length} results</>}
        </div>
        {isFetching && (
          <div className="flex items-center gap-2 text-xs text-[#898989]">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Loading...
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700 text-sm">
          Could not reach arXiv. Please try again in a moment.
        </div>
      )}

      {isFetching && data.length === 0 && (
        <div className="flex items-center justify-center py-24 text-[#898989]">
          <Loader2 className="h-6 w-6 animate-spin mr-3" /> Fetching from arXiv...
        </div>
      )}

      {!isFetching && data.length === 0 && !error && (
        <div className="p-card p-10 text-center text-[#898989]">No papers found for this category.</div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.map((paper) => <PaperCard key={paper.id} paper={paper} />)}
      </div>
    </AppShell>
  );
}
