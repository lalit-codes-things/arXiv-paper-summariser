import { useRoute, useLocation } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { useBookmarks } from '@/store/bookmarks';
import { ExternalLink, FileText, BookmarkCheck, BookmarkPlus, ArrowLeft, Loader2, AlertCircle } from 'lucide-react';
import { Link } from 'wouter';

function PaperView({ paper }: { paper: ArxivPaper }) {
  const { toggle, has } = useBookmarks();
  const saved = has(paper.id);
  const published = paper.published ? new Date(paper.published) : null;
  const dateStr = published
    ? published.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    : null;

  return (
    <div className="space-y-5 max-w-3xl">
      {/* Back */}
      <button onClick={() => history.back()} className="p-btn-outline text-sm flex items-center gap-2">
        <ArrowLeft className="h-3.5 w-3.5" /> Back
      </button>

      {/* Categories + ID */}
      <div className="flex flex-wrap items-center gap-2">
        {paper.categories.map((c) => (
          <span key={c} className="p-tag-gray text-xs">{c}</span>
        ))}
        <span className="text-xs font-mono text-[#898989] ml-1">{paper.arxiv_id}</span>
      </div>

      {/* Title */}
      <h1 className="text-2xl md:text-3xl font-bold text-[#191A23] leading-snug">{paper.title}</h1>

      {/* Authors + date */}
      <div className="text-sm text-[#898989] flex flex-wrap gap-x-3 gap-y-1 items-center">
        <span>{paper.authors.slice(0, 6).join(', ')}{paper.authors.length > 6 ? ' et al.' : ''}</span>
        {dateStr && <><span>·</span><span>{dateStr}</span></>}
      </div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-2 pt-1 pb-2">
        <a href={paper.abs_url} target="_blank" rel="noopener noreferrer" className="p-btn-dark text-sm">
          View on arXiv <ExternalLink className="h-3.5 w-3.5" />
        </a>
        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="p-btn-green text-sm">
          PDF <FileText className="h-3.5 w-3.5" />
        </a>
        <button onClick={() => toggle(paper.id)} className="p-btn-outline text-sm">
          {saved
            ? <><BookmarkCheck className="h-3.5 w-3.5" style={{ color: '#B9FF66' }} /> Saved</>
            : <><BookmarkPlus className="h-3.5 w-3.5" /> Save</>}
        </button>
      </div>

      <hr className="border-[#191A23]/10" />

      {/* Summary / Abstract */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <h2 className="font-bold text-[#191A23] text-lg">Summary</h2>
          <span className="p-tag text-xs">Abstract</span>
        </div>
        <p className="text-[#191A23]/80 leading-relaxed text-[15px] whitespace-pre-line">{paper.abstract}</p>
      </div>

      {/* Authors block */}
      {paper.authors.length > 0 && (
        <div className="bg-white border border-[#191A23]/12 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-[#191A23] mb-3">Authors</h3>
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
  const [match, params] = useRoute('/paper/:id');
  const [, navigate] = useLocation();
  const paperId = match ? decodeURIComponent(params!.id) : '';

  const { data: paper, isLoading, error } = useQuery({
    queryKey: ['paper', paperId],
    queryFn: () => arxiv.paper(paperId),
    enabled: paperId.length > 2,
    retry: 1,
  });

  if (!paperId) {
    return (
      <AppShell>
        <div className="p-card p-12 text-center text-[#898989]">
          No paper specified.{' '}
          <Link href="/papers" className="text-[#191A23] font-medium underline">Browse papers →</Link>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      {isLoading && (
        <div className="flex items-center gap-3 text-[#898989] py-20 justify-center">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading paper…</span>
        </div>
      )}

      {error && (
        <div className="p-card p-8 max-w-md">
          <div className="flex items-center gap-2 text-red-600 mb-3">
            <AlertCircle className="h-5 w-5" />
            <span className="font-semibold">Could not load paper</span>
          </div>
          <p className="text-sm text-[#898989] mb-4">The arXiv API couldn't find this paper. Try viewing it directly.</p>
          <div className="flex gap-2">
            <button onClick={() => history.back()} className="p-btn-outline text-sm">← Back</button>
            <a href={`https://arxiv.org/abs/${paperId}`} target="_blank" rel="noopener noreferrer" className="p-btn-dark text-sm">
              arXiv <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>
      )}

      {paper && !isLoading && <PaperView paper={paper} />}
    </AppShell>
  );
}
