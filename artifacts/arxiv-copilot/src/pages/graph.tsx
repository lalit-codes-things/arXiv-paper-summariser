import { AppShell } from '@/components/research/shell';
import { GraphCanvas } from '@/components/research/graph-canvas';

const DEMO_GRAPH = {
  nodes: [
    { id: 'transformer', label: 'Transformer', group: 'method' },
    { id: 'attention', label: 'Attention', group: 'method' },
    { id: 'bert', label: 'BERT', group: 'model' },
    { id: 'gpt', label: 'GPT', group: 'model' },
    { id: 'rag', label: 'RAG', group: 'method' },
    { id: 'diffusion', label: 'Diffusion', group: 'method' },
    { id: 'llm', label: 'LLM', group: 'model' },
    { id: 'vit', label: 'ViT', group: 'model' },
  ],
  edges: [
    { source: 'transformer', target: 'attention', weight: 0.9 },
    { source: 'transformer', target: 'bert', weight: 0.8 },
    { source: 'transformer', target: 'gpt', weight: 0.8 },
    { source: 'attention', target: 'rag', weight: 0.6 },
    { source: 'gpt', target: 'llm', weight: 0.9 },
    { source: 'bert', target: 'llm', weight: 0.7 },
    { source: 'transformer', target: 'vit', weight: 0.7 },
    { source: 'diffusion', target: 'vit', weight: 0.4 },
    { source: 'rag', target: 'llm', weight: 0.8 },
  ],
};

export default function GraphPage() {
  return (
    <AppShell>
      <div className="mb-8">
        <span className="p-tag mb-3 inline-block">Conceptual map</span>
        <h1 className="text-4xl font-bold text-[#191A23] mb-2">Knowledge Graph</h1>
        <p className="text-[#898989]">Method and model relationships across the research landscape.</p>
      </div>
      <div className="p-card p-6">
        <GraphCanvas graph={DEMO_GRAPH} />
      </div>
    </AppShell>
  );
}
