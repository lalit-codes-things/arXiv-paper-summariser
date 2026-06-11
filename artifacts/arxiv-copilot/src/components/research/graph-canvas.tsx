import { motion } from 'framer-motion';

type Graph = {
  nodes: Array<{ id: string; label: string; group: string }>;
  edges: Array<{ source: string; target: string; weight: number }>;
};

export function GraphCanvas({ graph }: { graph: Graph }) {
  const positions = graph.nodes.map((node, index) => ({
    ...node,
    x: 300 + Math.cos((index / graph.nodes.length) * Math.PI * 2) * 220,
    y: 260 + Math.sin((index / graph.nodes.length) * Math.PI * 2) * 200,
  }));
  const byId = Object.fromEntries(positions.map((n) => [n.id, n]));

  return (
    <svg viewBox="0 0 600 520" className="w-full rounded-xl" style={{ minHeight: 400 }}>
      <defs>
        <filter id="glow2">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {graph.edges.map((edge) => {
        const s = byId[edge.source];
        const t = byId[edge.target];
        if (!s || !t) return null;
        return (
          <line
            key={`${edge.source}-${edge.target}`}
            x1={s.x} y1={s.y} x2={t.x} y2={t.y}
            stroke="#191A23"
            strokeOpacity={0.15 + edge.weight * 0.25}
            strokeWidth={1 + edge.weight * 2}
          />
        );
      })}

      {positions.map((node) => (
        <motion.g
          key={node.id}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: graph.nodes.findIndex((n) => n.id === node.id) * 0.05 }}
          whileHover={{ scale: 1.1 }}
        >
          <circle
            cx={node.x} cy={node.y} r={32}
            fill={node.group === 'method' ? '#B9FF66' : '#191A23'}
            filter="url(#glow2)"
          />
          <text
            x={node.x} y={node.y + 4}
            textAnchor="middle"
            fontSize="11"
            fontFamily="Space Grotesk, sans-serif"
            fontWeight="600"
            fill={node.group === 'method' ? '#191A23' : '#ffffff'}
          >
            {node.label}
          </text>
        </motion.g>
      ))}
    </svg>
  );
}
