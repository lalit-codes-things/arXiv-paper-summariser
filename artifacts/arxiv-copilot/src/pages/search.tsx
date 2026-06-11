import { useState, useCallback } from 'react';
import { useSearch, useLocation } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { Search, ExternalLink, FileText, Loader2 } from 'lucide-react';

function PaperRow({ paper }: { paper: ArxivPaper }) {
  const year = paper.published ? new Date(paper.published).getFullYear() : null;
  return (
    <div className="p-card p-5 hover:shadow-[4px_4px_0px_#191A23] transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap gap-1.5 mb-2">
            {paper.categories.slice(0, 3).map((c) => (
              <span key={c} className="p-tag-gray text-[10px]">{c}</span>
            ))}
          </div>
          <h2 className="font-semibold text-[#191A23] leading-snug mb-2 line-clamp-2">{paper.title}</h2>
          <p className="text-sm text-[#898989] line-clamp-2 leading-relaxed">{paper.abstract}</p>
          <div className="flex items-center gap-3 mt-3 text-xs text-[#898989]">
            <span>{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ' et al.' : ''}</span>
            {year && <span>· {year}</span>}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          <a
            href={paper.abs_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-btn-dark text-xs px-3 py-1.5"
          >
            Abstract <ExternalLink className="h-3 w-3" />
          </a>
          <a
            href={paper.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-btn-outline text-xs px-3 py-1.5"
          >
            PDF <FileText className="h-3 w-3" />
          </a>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  const searchStr = useSearch();
  const params = new URLSearchParams(searchStr);
  const [, navigate] = useLocation();
  const [input, setInput] = useState(params.get('q') ?? '');
  const [submitted, setSubmitted] = useState(params.get('q') ?? '');

  const { data, isFetching, error } = useQuery({
    queryKey: ['search', submitted],
    queryFn: () => arxiv.search(submitted, 20),
    enabled: submitted.length > 1,
    retry: 1,
  });

  const handleSearch = useCallback(() => {
    const q = input.trim();
    if (!q) return;
    setSubmitted(q);
    navigate(`/search?q=${encodeURIComponent(q)}`);
  }, [input, navigate]);

  return (
    <AppShell>
      {/* Header */}
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">arXiv · 2M+ papers</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Semantic Search</h1>
        <p className="text-[#898989]">Search across all arXiv preprints in real time.</p>
      </div>

      {/* Search bar */}
      <div className="flex gap-3 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#898989]" />
          <input
            className="p-input pl-10"
            placeholder="e.g. transformer attention mechanisms, diffusion models for robotics..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={isFetching || !input.trim()}
          className="p-btn-dark px-5"
        >
          {isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
        </button>
      </div>

      {/* Results */}
      {isFetching && (
        <div className="flex items-center gap-3 text-[#898989] py-12 justify-center">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Searching arXiv...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700 text-sm">
          Could not reach arXiv. Please try again.
        </div>
      )}

      {data && !isFetching && (
        <>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-[#898989]">
              {data.length} result{data.length !== 1 ? 's' : ''} for <span className="font-medium text-[#191A23]">"{submitted}"</span>
            </span>
          </div>
          {data.length === 0 ? (
            <div className="p-card p-10 text-center text-[#898989]">
              No results found. Try broader terms.
            </div>
          ) : (
            <div className="space-y-3">
              {data.map((paper) => <PaperRow key={paper.id} paper={paper} />)}
            </div>
          )}
        </>
      )}

      {!submitted && !isFetching && (
        <div className="p-card p-10 text-center">
          <Search className="h-10 w-10 text-[#B9FF66] mx-auto mb-4" />
          <p className="text-[#191A23] font-medium mb-1">Start searching</p>
          <p className="text-sm text-[#898989]">Enter any topic, author name, or paper title above.</p>
        </div>
      )}
    </AppShell>
  );
}
