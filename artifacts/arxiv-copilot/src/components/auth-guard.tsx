// AuthGuard is replaced by the <Show> / Guarded pattern in App.tsx.
// This file is kept as a no-op re-export to avoid breaking any existing imports.
export function AuthGuard({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
