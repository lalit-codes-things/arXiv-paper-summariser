import { useEffect } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@workspace/replit-auth-web';
import { BookOpen, Search, Sparkles, TrendingUp, GitGraph, Users, KeyRound } from 'lucide-react';

const FEATURES = [
  { Icon: Search, label: 'Semantic search', desc: 'Find relevant papers instantly across 2 million arXiv preprints.' },
  { Icon: Sparkles, label: 'AI deep summaries', desc: 'Get structured breakdowns — background, methods, results — using your own API key.' },
  { Icon: TrendingUp, label: 'Trending & feed', desc: 'Stay current with daily trending papers ranked by topic relevance.' },
  { Icon: GitGraph, label: 'Knowledge graph', desc: 'Visualise connections between papers, authors, and topics.' },
  { Icon: Users, label: 'Team workspace', desc: 'Collaborative notes and shared reading lists for your research group.' },
  { Icon: KeyRound, label: 'Private by default', desc: 'Your API key stays in your browser — nothing sensitive ever hits our server.' },
];

export default function Home() {
  const { isAuthenticated, isLoading, login } = useAuth();
  const [, navigate] = useLocation();

  useEffect(() => {
    if (!isLoading && isAuthenticated) navigate('/search');
  }, [isAuthenticated, isLoading, navigate]);

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Top nav */}
      <header className="flex items-center justify-between px-8 py-5 border-b border-[#191A23]/8 max-w-6xl mx-auto w-full">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-[#B9FF66] border border-[#191A23] rounded-lg flex items-center justify-center">
            <BookOpen className="h-3.5 w-3.5 text-[#191A23]" />
          </div>
        </div>
        <button
          onClick={login}
          disabled={isLoading}
          className="p-btn-dark text-sm"
        >
          {isLoading ? 'Loading…' : 'Sign in'}
        </button>
      </header>

      {/* Hero */}
      <section className="flex flex-col items-center justify-center text-center px-6 pt-24 pb-16 max-w-3xl mx-auto w-full">
        <span className="p-tag mb-6">Research, accelerated</span>
        <h1 className="text-5xl md:text-6xl font-bold text-[#191A23] leading-tight mb-6">
          Read smarter.<br />
          <span className="bg-[#B9FF66] px-3 rounded-lg inline-block mt-1">Stay current.</span>
        </h1>
        <p className="text-lg text-[#898989] mb-10 max-w-lg leading-relaxed">
          An AI-powered platform for searching, reading, and discussing arXiv preprints — with personalised ranking, knowledge graphs, and team collaboration.
        </p>
        <button
          onClick={login}
          disabled={isLoading}
          className="p-btn-dark text-base px-8 py-3.5"
        >
          {isLoading ? 'Loading…' : 'Sign in to get started →'}
        </button>
        <p className="text-xs text-[#898989] mt-4">Sign in with your Replit account. Free to use.</p>
      </section>

      {/* Features grid */}
      <section className="border-t border-[#191A23]/8 bg-[#F3F3F3] px-8 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-[#191A23] mb-2 text-center">Everything you need for research</h2>
          <p className="text-[#898989] text-center mb-10">All features unlock after sign-in.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map(({ Icon, label, desc }) => (
              <div key={label} className="bg-white border border-[#191A23] rounded-2xl p-6 hover:shadow-[4px_4px_0_#191A23] transition-shadow">
                <div className="w-10 h-10 bg-[#B9FF66] border border-[#191A23] rounded-xl flex items-center justify-center mb-4">
                  <Icon className="h-5 w-5 text-[#191A23]" />
                </div>
                <h3 className="font-bold text-[#191A23] mb-1.5">{label}</h3>
                <p className="text-sm text-[#898989] leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="bg-[#191A23] px-8 py-16 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Ready to start researching?</h2>
        <p className="text-[#898989] mb-8">Sign in and access every feature instantly.</p>
        <button onClick={login} disabled={isLoading} className="p-btn-green text-base px-8 py-3.5">
          {isLoading ? 'Loading…' : 'Sign in with Replit →'}
        </button>
      </section>
    </div>
  );
}
