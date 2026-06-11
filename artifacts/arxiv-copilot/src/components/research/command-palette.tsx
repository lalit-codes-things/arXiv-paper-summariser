import { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'wouter';

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [, navigate] = useLocation();

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        setOpen((current) => !current);
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
      className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/60 backdrop-blur-sm"
      onClick={() => setOpen(false)}
    >
      <div
        className="glass w-full max-w-xl rounded-2xl p-2"
        onClick={(event) => event.stopPropagation()}
      >
        <input
          autoFocus
          className="w-full bg-transparent px-4 py-3 text-lg outline-none placeholder-zinc-500"
          placeholder="Search papers... (Enter to search)"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => event.key === 'Enter' && submit()}
        />
        <div className="px-4 py-2 text-xs text-zinc-600">↵ to search · Esc to close · ⌘K to toggle</div>
      </div>
    </div>
  );
}
