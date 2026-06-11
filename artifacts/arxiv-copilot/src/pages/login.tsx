import { useEffect } from 'react';
import { useLocation } from 'wouter';
import { BookOpen } from 'lucide-react';
import { useAuth } from '@workspace/replit-auth-web';

export default function LoginPage() {
  const { isAuthenticated, isLoading, login, user } = useAuth();
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (isAuthenticated) {
      setLocation('/dashboard');
    }
  }, [isAuthenticated, setLocation]);

  return (
    <div className="min-h-screen bg-[#F3F3F3] flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-[#B9FF66] rounded-2xl flex items-center justify-center mx-auto mb-4">
            <BookOpen className="h-6 w-6 text-[#191A23]" />
          </div>
          <h1 className="text-3xl font-bold text-[#191A23]">Sign in</h1>
          <p className="text-[#898989] mt-2 text-sm">
            Access bookmarks, reading history, and your workspace.
          </p>
        </div>

        <div className="bg-white border border-[#191A23] rounded-2xl p-8 space-y-4">
          {isLoading ? (
            <div className="p-btn-dark w-full justify-center opacity-60 cursor-not-allowed">
              Checking session…
            </div>
          ) : isAuthenticated ? (
            <p className="text-center text-sm text-[#898989]">
              Signed in as{' '}
              <span className="font-semibold text-[#191A23]">
                {user?.firstName ?? user?.email ?? 'you'}
              </span>. Redirecting…
            </p>
          ) : (
            <button onClick={login} className="p-btn-dark w-full justify-center">
              Log in
            </button>
          )}

          <p className="text-center text-xs text-[#898989]">
            Uses your existing account — no separate sign-up.
          </p>
        </div>
      </div>
    </div>
  );
}
