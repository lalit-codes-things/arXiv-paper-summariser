import { useState, useCallback } from 'react';

const STORAGE_KEY = 'arxiv_openai_key';

export function useApiKey() {
  const [key, setKeyState] = useState<string>(() => {
    try { return localStorage.getItem(STORAGE_KEY) ?? ''; } catch { return ''; }
  });

  const saveKey = useCallback((value: string) => {
    const trimmed = value.trim();
    try { localStorage.setItem(STORAGE_KEY, trimmed); } catch { /* noop */ }
    setKeyState(trimmed);
  }, []);

  const clearKey = useCallback(() => {
    try { localStorage.removeItem(STORAGE_KEY); } catch { /* noop */ }
    setKeyState('');
  }, []);

  return { key, saveKey, clearKey, hasKey: key.startsWith('sk-') };
}
