import { useState } from 'react';
import { KeyRound, Eye, EyeOff, Trash2, CheckCircle2 } from 'lucide-react';
import { useApiKey } from '@/hooks/use-api-key';

interface Props {
  /** When provided, shows an inline prompt instead of full settings card */
  compact?: boolean;
  onKeySet?: () => void;
}

export function ByokPanel({ compact, onKeySet }: Props) {
  const { key, hasKey, saveKey, clearKey } = useApiKey();
  const [draft, setDraft] = useState('');
  const [show, setShow] = useState(false);
  const [saved, setSaved] = useState(false);

  function handleSave() {
    if (!draft.trim().startsWith('sk-')) return;
    saveKey(draft.trim());
    setDraft('');
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    onKeySet?.();
  }

  if (compact && hasKey) return null;

  return (
    <div className={compact ? '' : 'p-card p-6'}>
      <div className="flex items-center gap-2 mb-4">
        <KeyRound className="h-4 w-4 text-[#191A23]" />
        <h2 className="font-bold text-[#191A23]">
          {compact ? 'Add your OpenAI API key to enable AI summaries' : 'OpenAI API Key'}
        </h2>
      </div>

      {/* Security notice */}
      <div className="bg-[#B9FF66]/20 border border-[#B9FF66] rounded-xl px-4 py-3 mb-4 text-sm text-[#191A23]">
        <strong>Your key stays on your device.</strong> It is saved only in your browser's
        localStorage and is sent directly to OpenAI — it never touches this website's server.
      </div>

      {hasKey ? (
        <div className="flex items-center gap-3">
          <div className="flex-1 p-input bg-[#F3F3F3] text-[#191A23]/50 font-mono text-xs flex items-center">
            sk-•••••••••••••••••{key.slice(-4)}
          </div>
          <button onClick={clearKey} className="p-btn-outline text-sm flex items-center gap-1.5 text-red-600 border-red-300 hover:bg-red-50">
            <Trash2 className="h-3.5 w-3.5" /> Remove
          </button>
        </div>
      ) : (
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type={show ? 'text' : 'password'}
              className="p-input pr-10 font-mono text-sm"
              placeholder="sk-..."
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSave()}
              autoComplete="off"
            />
            <button
              type="button"
              onClick={() => setShow((s) => !s)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#898989] hover:text-[#191A23]"
            >
              {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          <button
            onClick={handleSave}
            disabled={!draft.trim().startsWith('sk-')}
            className="p-btn-dark text-sm shrink-0"
          >
            {saved ? <><CheckCircle2 className="h-4 w-4" /> Saved</> : 'Save key'}
          </button>
        </div>
      )}

      {!compact && (
        <p className="text-xs text-[#898989] mt-3">
          Get a key at{' '}
          <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer"
            className="underline text-[#191A23]">platform.openai.com/api-keys</a>.
          Free-tier accounts get $5 of credit.
        </p>
      )}
    </div>
  );
}
