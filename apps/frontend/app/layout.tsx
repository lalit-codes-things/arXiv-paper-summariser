import '@/styles/globals.css';
import { Providers } from '@/components/research/providers';

export const metadata = { title: 'Arxiv Research Copilot', description: 'Production AI research workspace for papers, teams, chat, and graphs.' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><Providers>{children}</Providers></body></html>;
}
