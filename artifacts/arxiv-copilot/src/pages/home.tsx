import { Link } from 'wouter';
import { ArrowRight, Search, Sparkles, Zap, GitGraph, Users, TrendingUp, Rss } from 'lucide-react';

const features = [
  {
    Icon: Search,
    label: 'Semantic Search',
    desc: 'Query 2M+ arXiv papers using natural language. Finds what keyword search misses.',
  },
  {
    Icon: Sparkles,
    label: 'AI Paper Chat',
    desc: 'Ask questions about any paper — methodology, findings, limitations — and get clear answers.',
  },
  {
    Icon: Rss,
    label: 'Personalized Feed',
    desc: 'Papers ranked by your interests, reading history, and activity across the platform.',
  },
  {
    Icon: TrendingUp,
    label: 'Trending Radar',
    desc: 'See which papers are gaining momentum across cs.AI, cs.CL, cs.LG, and more.',
  },
  {
    Icon: GitGraph,
    label: 'Knowledge Graph',
    desc: 'Explore citation networks, topic clusters, and method relationships visually.',
  },
  {
    Icon: Users,
    label: 'Team Workspace',
    desc: 'Annotate, discuss, and build collaborative summaries on papers with your team.',
  },
];

const categories = ['cs.AI', 'cs.CL', 'cs.LG', 'cs.CV', 'stat.ML', 'cs.RO', 'eess.AS', 'cs.IR'];

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <header className="border-b border-[#191A23]/10 px-8 py-4 flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-2.5 font-bold text-[#191A23] text-lg">
          <div className="w-8 h-8 bg-[#B9FF66] rounded-lg flex items-center justify-center text-sm font-black">A</div>
          ArXiv Copilot
        </div>
        <div className="flex items-center gap-3">
          <Link href="/search">
            <button className="p-btn-outline text-sm">Search papers</button>
          </Link>
          <Link href="/papers">
            <button className="p-btn-dark text-sm">Browse <ArrowRight className="h-3.5 w-3.5" /></button>
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-8 py-20 md:py-28">
        <div className="max-w-3xl">
          <span className="p-tag mb-6 inline-block">Real arXiv data · Updated daily</span>
          <h1 className="text-5xl md:text-7xl font-bold text-[#191A23] leading-[1.05] tracking-tight mb-6">
            Research papers,<br />
            <span className="bg-[#B9FF66] px-2 rounded-md">discovered.</span>
          </h1>
          <p className="text-xl text-[#898989] leading-relaxed mb-10 max-w-2xl">
            Search, read, and explore 2 million arXiv papers with semantic search,
            AI-powered summaries, and real-time ingestion from every category.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/search">
              <button className="p-btn-dark px-6 py-3 text-base">
                Search papers <ArrowRight className="h-4 w-4" />
              </button>
            </Link>
            <Link href="/papers">
              <button className="p-btn-green px-6 py-3 text-base">
                Browse by category
              </button>
            </Link>
          </div>
        </div>

        {/* Stats strip */}
        <div className="mt-16 grid grid-cols-3 gap-4 max-w-lg">
          {[
            { n: '2M+', label: 'Papers indexed' },
            { n: '200+', label: 'Categories' },
            { n: 'Daily', label: 'New preprints' },
          ].map(({ n, label }) => (
            <div key={label} className="bg-[#F3F3F3] border border-[#191A23]/10 rounded-2xl p-4 text-center">
              <div className="text-2xl font-bold text-[#191A23]">{n}</div>
              <div className="text-xs text-[#898989] mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-8 pb-24">
        <div className="flex items-center gap-4 mb-10">
          <h2 className="text-3xl font-bold text-[#191A23]">What you can do</h2>
          <span className="p-tag">6 tools</span>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map(({ Icon, label, desc }) => (
            <div key={label} className="p-card p-6 group cursor-default">
              <div className="w-10 h-10 bg-[#B9FF66] rounded-xl flex items-center justify-center mb-4">
                <Icon className="h-5 w-5 text-[#191A23]" />
              </div>
              <h3 className="font-semibold text-[#191A23] text-base mb-2">{label}</h3>
              <p className="text-sm text-[#898989] leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Categories */}
      <section className="bg-[#191A23] py-16 px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
            <h2 className="text-3xl font-bold text-white">Browse by category</h2>
            <Link href="/papers">
              <button className="p-btn-green text-sm">View all papers <ArrowRight className="h-3.5 w-3.5" /></button>
            </Link>
          </div>
          <div className="flex flex-wrap gap-3">
            {categories.map((cat) => (
              <Link key={cat} href={`/papers?cat=${cat}`}>
                <div className="border border-white/20 text-white rounded-full px-4 py-2 text-sm font-medium hover:bg-[#B9FF66] hover:text-[#191A23] hover:border-[#B9FF66] transition-all cursor-pointer">
                  {cat}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-8 py-24">
        <div className="bg-[#B9FF66] border border-[#191A23] rounded-3xl p-10 md:p-16 flex flex-col md:flex-row items-center justify-between gap-8">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-[#191A23] mb-3">
              Start exploring in seconds.
            </h2>
            <p className="text-[#191A23]/70 text-lg">No account required.</p>
          </div>
          <Link href="/search">
            <button className="p-btn-dark px-8 py-3.5 text-base shrink-0">
              Try semantic search <ArrowRight className="h-4 w-4" />
            </button>
          </Link>
        </div>
      </section>
    </div>
  );
}
