import '@/styles/globals.css';
import { Providers } from '@/components/research/providers';

export const metadata = {
  title: { default: 'Arxiv Copilot', template: '%s | Arxiv Copilot' },
  description: 'AI-powered research: search, read, and discuss arXiv papers with your team.',
  openGraph: {
    title: 'Arxiv Copilot',
    description: 'Semantic search, AI chat, and collaborative reading for arXiv papers.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><Providers>{children}</Providers></body></html>;
}
