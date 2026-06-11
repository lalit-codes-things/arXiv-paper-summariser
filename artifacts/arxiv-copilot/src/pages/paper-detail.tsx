import { useSearch } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { useBookmarks } from '@/store/bookmarks';
import { ExternalLink, FileText, BookmarkCheck, BookmarkPlus, ArrowLeft, Loader2 } from 'lucide-react';
import { Link } from 'wouter';

function PaperDetail({ paper }: { paper: ArxivPaper }) {
  const { toggle, has } = useBookmarks();
  const saved = has(paper.id);
  const published = paper.published ? new Date(paper.published) : null;

  return (
    <div className="space-y-6">
      {/* Back */}
      <Link href="/papers">
        <button className="p-btn-outline text-sm flex items-center gap-2">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to papers
        </button>
      </Link>

      {/* Header card */}
      <div className="p-card p-8">
        <div className="flex flex-wrap gap-2 mb-4">
          {paper.categories.map((c) => (
            <span key={c} className="p-tag-gray text-xs">{c}</span>
          ))}
        </div>
        <h1 className="text-2xl font-bold text-[#191A23] leading-snug mb-4">{paper.title}</h1>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-[#898989] mb-6">
          <span>{paper.authors.slice(0, 5).join(', ')}{paper.authors.length > 5 ? ' et al.' : ''}</span>
          {published && (
            <>
              <span>·</span>
              <span>{published.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
            </>
          )}
          <span>·</span>
          <span className="font-mono text-xs">{paper.arxiv_id}</span>
        </div>
        <div className="flex flex-wrap gap-3">
          <a href={paper.abs_url} target="_blank" rel="noopener noreferrer" className="p-btn-dark text-sm">
            View on arXiv <ExternalLink className="h-3.5 w-3.5" />
          </a>
          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="p-btn-green text-sm">
            Download PDF <FileText className="h-3.5 w-3.5" />
          </a>
          <button
            onClick={() => toggle(paper.id)}
            className="p-btn-outline text-sm"
          >
            {saved
              ? <><BookmarkCheck className="h-3.5 w-3.5 text-[#B9FF66]" /> Saved</>
              : <><BookmarkPlus className="h-3.5 w-3.5" /> Save</>
            }
          </button>
        </div>
      </div>

      {/* Abstract */}
      <div className="p-card p-8">
        <h2 className="font-bold text-[#191A23] text-lg mb-4">Abstract</h2>
        <p className="text-[#191A23]/80 leading-relaxed text-sm">{paper.abstract}</p>
      </div>

      {/* Authors */}
      {paper.authors.length > 0 && (
        <div className="p-card p-6">
          <h2 className="font-bold text-[#191A23] mb-3">Authors</h2>
          <div className="flex flex-wrap gap-2">
            {paper.authors.map((a) => (
              <span key={a} className="p-tag-gray text-sm">{a}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function PaperDetailPage() {
  const searchStr = useSearch();
  const params = new URLSearchParams(searchStr);
  const paperId = params.get('id') ?? '';

  const { data, isLoading, error } = useQuery({
    queryKey: ['paper-detail', paperId],
    queryFn: () => arxiv.search(paperId, 1),
    enabled: paperId.length > 3,
    retry: 1,
  });

  const paper = data?.[0];

  if (!paperId) {
    return (
      <AppShell>
        <div className="p-card p-12 text-center text-[#898989]">
          No paper ID specified. <Link href="/papers" className="text-[#191A23] font-medium underline">Browse papers →</Link>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      {isLoading && (
        <div className="flex items-center justify-center py-24 text-[#898989]">
          <Loader2 className="h-6 w-6 animate-spin mr-3" /> Loading paper...
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700 text-sm">
          Could not load paper details. <a href={`https://arxiv.org/abs/${paperId}`} target="_blank" rel="noopener noreferrer" className="underline">View directly on arXiv →</a>
        </div>
      )}
      {paper && <PaperDetail paper={paper} />}
    </AppShell>
  );
}
