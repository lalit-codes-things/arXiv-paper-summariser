import { useRoute } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { useState, useRef, useCallback } from 'react';
import { AppShell } from '@/components/research/shell';
import { ByokPanel } from '@/components/byok-panel';
import { useApiKey } from '@/hooks/use-api-key';
import { arxiv, type ArxivPaper } from '@/lib/api';
import { useBookmarks } from '@/store/bookmarks';
import {
  ExternalLink, FileText, BookmarkCheck, BookmarkPlus,
  ArrowLeft, Loader2, AlertCircle, Sparkles, RefreshCw,
} from 'lucide-react';
import { Link } from 'wouter';

const SUMMARY_PROMPT = (title: string, abstract: string, authors: string[], categories: string[]) => `
You are a research assistant. Write a detailed, structured summary of the following arXiv paper for an academic audience.

Title: ${title}
Authors: ${authors.slice(0, 5).join(', ')}${authors.length > 5 ? ' et al.' : ''}
Categories: ${categories.join(', ')}
Abstract: ${abstract}

Write the summary with these exact sections (use the bold headers):

**Background & Motivation**
What problem does this paper address? Why does it matter? What gap in prior work does it fill?

**Methods & Approach**
What techniques, architectures, algorithms, or frameworks did the authors use? Be specific about the technical approach.

**Key Results & Findings**
What did the paper achieve? Include specific numbers, benchmarks, or comparisons where possible.

**Limitations**
What are the acknowledged shortcomings, assumptions, or failure cases?

**Significance & Impact**
Why is this paper important? Who benefits from this work and how might it influence future research?

Be thorough and precise. Use full paragraphs, not bullet points.
`.trim();

function StreamingSummary({ paper }: { paper: ArxivPaper }) {
  const { key, hasKey } = useApiKey();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const generate = useCallback(async () => {
    if (!hasKey) return;
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    setText('');
    setError('');
    setDone(false);
    setLoading(true);

    try {
      const res = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        signal: ctrl.signal,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          stream: true,
          messages: [
            {
              role: 'user',
              content: SUMMARY_PROMPT(paper.title, paper.abstract, paper.authors, paper.categories),
            },
          ],
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as any)?.error?.message ?? `OpenAI returned ${res.status}`);
      }

      const reader = res.body!.getReader();
      const dec = new TextDecoder();
      let buf = '';

      while (true) {
        const { value, done: streamDone } = await reader.read();
        if (streamDone) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() ?? '';
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const data = line.slice(6).trim();
          if (data === '[DONE]') { setDone(true); continue; }
          try {
            const chunk = JSON.parse(data);
            const delta = chunk?.choices?.[0]?.delta?.content ?? '';
            if (delta) setText((t) => t + delta);
          } catch { /* skip bad chunk */ }
        }
      }
      setDone(true);
    } catch (e: any) {
      if (e?.name !== 'AbortError') setError(e?.message ?? 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, [key, hasKey, paper]);

  if (!hasKey) {
    return <ByokPanel compact onKeySet={() => {}} />;
  }

  return (
    <div>
      {!text && !loading && (
        <button onClick={generate} className="p-btn-dark text-sm">
          <Sparkles className="h-3.5 w-3.5" />
          Generate AI Summary
        </button>
      )}

      {loading && !text && (
        <div className="flex items-center gap-2 text-[#898989] text-sm py-4">
          <Loader2 className="h-4 w-4 animate-spin" />
          Generating summary…
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}

      {text && (
        <div className="space-y-5">
          <FormattedSummary text={text} />
          {done && (
            <button onClick={generate} className="p-btn-outline text-xs flex items-center gap-1.5">
              <RefreshCw className="h-3 w-3" /> Regenerate
            </button>
          )}
          {loading && (
            <span className="inline-block w-1.5 h-4 bg-[#191A23] animate-pulse rounded-sm" />
          )}
        </div>
      )}
    </div>
  );
}

function FormattedSummary({ text }: { text: string }) {
  // Split on **Section** headers and render as structured blocks
  const sections = text.split(/\n\n(?=\*\*)/);
  return (
    <div className="space-y-5">
      {sections.map((section, i) => {
        const headerMatch = section.match(/^\*\*(.+?)\*\*\n?([\s\S]*)/);
        if (headerMatch) {
          return (
            <div key={i}>
              <h3 className="font-bold text-[#191A23] text-base mb-2">{headerMatch[1]}</h3>
              <p className="text-[#191A23]/80 leading-relaxed text-[15px] whitespace-pre-line">
                {headerMatch[2].trim()}
              </p>
            </div>
          );
        }
        return (
          <p key={i} className="text-[#191A23]/80 leading-relaxed text-[15px] whitespace-pre-line">
            {section.replace(/\*\*/g, '').trim()}
          </p>
        );
      })}
    </div>
  );
}

function PaperView({ paper }: { paper: ArxivPaper }) {
  const { toggle, has } = useBookmarks();
  const saved = has(paper.id);
  const published = paper.published ? new Date(paper.published) : null;
  const dateStr = published
    ? published.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    : null;

  return (
    <div className="space-y-6 max-w-3xl">
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
      <div className="flex flex-wrap gap-2">
        <a href={paper.abs_url} target="_blank" rel="noopener noreferrer" className="p-btn-dark text-sm">
          View on arXiv <ExternalLink className="h-3.5 w-3.5" />
        </a>
        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="p-btn-green text-sm">
          PDF <FileText className="h-3.5 w-3.5" />
        </a>
        <button onClick={() => toggle(paper.id)} className="p-btn-outline text-sm">
          {saved
            ? <><BookmarkCheck className="h-3.5 w-3.5 text-[#B9FF66]" /> Saved</>
            : <><BookmarkPlus className="h-3.5 w-3.5" /> Save</>}
        </button>
      </div>

      <hr className="border-[#191A23]/10" />

      {/* Original Abstract */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <h2 className="font-bold text-[#191A23] text-lg">Abstract</h2>
        </div>
        <p className="text-[#191A23]/80 leading-relaxed text-[15px]">{paper.abstract}</p>
      </div>

      <hr className="border-[#191A23]/10" />

      {/* AI Deep Summary — BYOK */}
      <div className="p-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="h-4 w-4 text-[#191A23]" />
          <h2 className="font-bold text-[#191A23] text-lg">AI Deep Summary</h2>
          <span className="p-tag text-xs ml-auto">BYOK</span>
        </div>
        <p className="text-sm text-[#898989] mb-5">
          A structured breakdown covering background, methods, results, limitations, and significance —
          generated using your own OpenAI key, which never leaves your browser.
        </p>
        <StreamingSummary paper={paper} />
      </div>

      {/* Authors block */}
      {paper.authors.length > 0 && (
        <div className="p-card p-5">
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
          <p className="text-sm text-[#898989] mb-4">The arXiv API couldn't find this paper.</p>
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
