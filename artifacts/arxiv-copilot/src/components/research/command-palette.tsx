import { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'wouter';
import { Search } from 'lucide-react';

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [, navigate] = useLocation();

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        setOpen((c) => !c);
      }
      if (event.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const submit = useCallback(() => {
    if (!query.trim()) return;
    navigate(`/search?q=${encodeURIComponent(query)}`);
    setOpen(false);
    setQuery('');
  }, [query, navigate]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/40 backdrop-blur-sm"
      onClick={() => setOpen(false)}
    >
      <div
        className="bg-white border border-[#191A23] rounded-2xl w-full max-w-xl shadow-[6px_6px_0px_#191A23] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-4 py-3 border-b border-[#191A23]/10">
          <Search className="h-4 w-4 text-[#898989] shrink-0" />
          <input
            autoFocus
            className="flex-1 bg-transparent text-[#191A23] text-base outline-none placeholder-[#898989]"
            placeholder="Search arXiv papers..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submit()}
          />
        </div>
        <div className="px-4 py-2.5 flex items-center gap-3 text-xs text-[#898989]">
          <span><kbd className="bg-[#F3F3F3] px-1.5 py-0.5 rounded text-[10px] font-mono">↵</kbd> search</span>
          <span><kbd className="bg-[#F3F3F3] px-1.5 py-0.5 rounded text-[10px] font-mono">Esc</kbd> close</span>
        </div>
      </div>
    </div>
  );
}
