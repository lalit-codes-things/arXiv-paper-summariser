import { useState, useCallback } from 'react';
import { useLocation, Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { Search, ArrowRight, BookOpen, Loader2 } from 'lucide-react';
import { arxiv } from '@/lib/api';
import { CommandPalette } from '@/components/research/command-palette';

const CATEGORIES = [
  { id: 'cs.AI', label: 'AI' },
  { id: 'cs.CL', label: 'NLP' },
  { id: 'cs.LG', label: 'ML' },
  { id: 'cs.CV', label: 'Vision' },
  { id: 'stat.ML', label: 'Stats ML' },
  { id: 'cs.RO', label: 'Robotics' },
];

export default function Home() {
  const [, navigate] = useLocation();
  const [query, setQuery] = useState('');

  const { data: trending = [], isLoading } = useQuery({
    queryKey: ['home-trending'],
    queryFn: () => arxiv.recent('cs.AI,cs.CL,cs.LG', 6),
    staleTime: 60_000,
  });

  const handleSearch = useCallback(() => {
    const q = query.trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
  }, [query, navigate]);

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Top nav */}
      <header className="flex items-center justify-between px-8 py-5 border-b border-[#191A23]/8 max-w-6xl mx-auto w-full">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-[#B9FF66] rounded-lg flex items-center justify-center">
            <BookOpen className="h-4 w-4 text-[#191A23]" />
          </div>
          <span className="font-bold text-[#191A23] text-base">ArXiv Paper Summariser</span>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/papers">
            <button className="p-btn-outline text-sm">Browse</button>
          </Link>
          <Link href="/trending">
            <button className="p-btn-dark text-sm">Trending <ArrowRight className="h-3.5 w-3.5" /></button>
          </Link>
        </div>
      </header>

      {/* Hero — search centric */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
        <span className="p-tag mb-6">Live arXiv data · No sign-up</span>
        <h1 className="text-5xl md:text-6xl font-bold text-[#191A23] leading-tight mb-4 max-w-2xl">
          Find and read any<br />
          <span className="bg-[#B9FF66] px-2 rounded-md">arXiv paper</span>
        </h1>
        <p className="text-lg text-[#898989] mb-10 max-w-md">
          Search across 2 million preprints. Browse by category. Read clean summaries.
        </p>

        {/* Search bar */}
        <div className="flex gap-2 w-full max-w-xl">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#898989]" />
            <input
              autoFocus
              className="p-input pl-10 h-12 text-base"
              placeholder="Search topic, author, or arXiv ID…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={!query.trim()}
            className="p-btn-dark h-12 px-5 text-sm shrink-0"
          >
            Search
          </button>
        </div>

        {/* Category pills */}
        <div className="flex flex-wrap gap-2 justify-center mt-6">
          {CATEGORIES.map(({ id, label }) => (
            <Link key={id} href={`/papers?cat=${id}`}>
              <div className="border border-[#191A23]/20 rounded-full px-4 py-1.5 text-sm text-[#191A23] font-medium hover:bg-[#191A23] hover:text-white transition-all cursor-pointer">
                {id} <span className="text-[#898989] font-normal">({label})</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Recent papers strip */}
      <section className="border-t border-[#191A23]/8 bg-[#F3F3F3] px-8 py-10">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-bold text-[#191A23] text-lg">Latest from arXiv</h2>
            <Link href="/trending">
              <button className="p-btn-outline text-xs px-3 py-1.5">See all trending →</button>
            </Link>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-8 text-[#898989]">
              <Loader2 className="h-5 w-5 animate-spin" />
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {trending.map((paper) => (
                <Link key={paper.id} href={`/paper/${encodeURIComponent(paper.id)}`}>
                  <div className="bg-white border border-[#191A23]/12 rounded-xl p-4 hover:border-[#191A23] hover:shadow-[3px_3px_0px_#191A23] transition-all cursor-pointer h-full">
                    <div className="flex gap-1.5 mb-2 flex-wrap">
                      {paper.categories.slice(0, 2).map((c) => (
                        <span key={c} className="p-tag-gray text-[10px]">{c}</span>
                      ))}
                    </div>
                    <h3 className="text-sm font-semibold text-[#191A23] line-clamp-2 leading-snug mb-2">{paper.title}</h3>
                    <p className="text-xs text-[#898989]">
                      {paper.authors[0]}{paper.authors.length > 1 ? ' et al.' : ''}
                      {paper.published && ` · ${new Date(paper.published).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <CommandPalette />
    </div>
  );
}
