import { useState } from 'react';
import { useLocation, Link } from 'wouter';
import { BookOpen, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const [, navigate] = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  function submit(e: React.FormEvent) {
    e.preventDefault();
    navigate('/dashboard');
  }

  return (
    <div className="min-h-screen bg-[#F3F3F3] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-[#B9FF66] rounded-2xl flex items-center justify-center mx-auto mb-4">
            <BookOpen className="h-6 w-6 text-[#191A23]" />
          </div>
          <h1 className="text-3xl font-bold text-[#191A23]">Welcome back</h1>
          <p className="text-[#898989] mt-2">Sign in to your research workspace</p>
        </div>

        <div className="bg-white border border-[#191A23] rounded-2xl p-8">
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#191A23] mb-1.5">Email</label>
              <input
                type="email"
                className="p-input"
                placeholder="you@research.org"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#191A23] mb-1.5">Password</label>
              <input
                type="password"
                className="p-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="p-btn-dark w-full justify-center py-2.5 text-sm mt-2">
              Sign in <ArrowRight className="h-4 w-4" />
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-[#898989] mt-6">
          Don't need an account?{' '}
          <Link href="/search" className="text-[#191A23] font-medium hover:underline">
            Search papers directly →
          </Link>
        </p>
      </div>
    </div>
  );
}
