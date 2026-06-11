import { Link } from 'wouter';

const features = [
  { title: 'Semantic search', desc: 'Hybrid vector + keyword search across thousands of arXiv papers.' },
  { title: 'AI paper chat', desc: "Ask Claude anything about a paper's methodology, findings, or limitations." },
  { title: 'Personalized feed', desc: 'A ranked feed that learns your research interests over time.' },
  { title: 'Trending radar', desc: 'See which papers are gaining momentum across the platform.' },
  { title: 'Knowledge graph', desc: 'Explore citation networks and topic clusters visually.' },
  { title: 'Team workspace', desc: 'Annotate, discuss, and collaborate on papers with your team.' },
];

export default function Home() {
  return (
    <main className="min-h-screen grid-bg">
      <div className="mx-auto max-w-5xl px-6 py-24">
        <div className="text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-zinc-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Live platform · Real arXiv data
          </div>
          <h1 className="text-5xl font-semibold tracking-tight md:text-7xl">
            Research papers,<br />
            <span className="text-indigo-400">AI-powered.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-zinc-400">
            Search, read, annotate, and discuss arXiv papers with your team. Powered by semantic embeddings,
            real AI chat, and personalized ranking.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link href="/dashboard">
              <button className="rounded-xl bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-zinc-200">
                Open dashboard
              </button>
            </Link>
            <Link href="/papers">
              <button className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20">
                Browse papers
              </button>
            </Link>
            <Link href="/search">
              <button className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20">
                Try search
              </button>
            </Link>
          </div>
        </div>
        <div className="mt-24 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div key={feature.title} className="rounded-2xl border border-white/10 bg-white/[.04] p-6 backdrop-blur-xl">
              <h3 className="font-medium text-white">{feature.title}</h3>
              <p className="mt-2 text-sm text-zinc-400">{feature.desc}</p>
            </div>
          ))}
        </div>
        <div className="mt-24 rounded-2xl border border-white/10 bg-white/[.04] p-8 text-center">
          <h2 className="text-2xl font-semibold">Get started in 30 seconds</h2>
          <p className="mt-3 text-zinc-400">No account required. Search papers immediately.</p>
          <div className="mt-6 flex justify-center">
            <Link href="/search">
              <button className="rounded-xl bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-zinc-200">
                Try semantic search →
              </button>
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
