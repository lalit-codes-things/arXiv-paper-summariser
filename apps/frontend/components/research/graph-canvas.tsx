'use client';
import { motion } from 'framer-motion';

type Graph = { nodes: Array<{ id: string; label: string; group: string }>; edges: Array<{ source: string; target: string; weight: number }> };
export function GraphCanvas({ graph }: { graph: Graph }) {
  const positions = graph.nodes.map((node, index) => ({ ...node, x: 240 + Math.cos(index / graph.nodes.length * Math.PI * 2) * 190, y: 240 + Math.sin(index / graph.nodes.length * Math.PI * 2) * 170 }));
  const byId = Object.fromEntries(positions.map((node) => [node.id, node]));
  return <svg viewBox="0 0 480 480" className="h-[520px] w-full rounded-3xl border border-white/10 bg-black/30"><defs><filter id="glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>{graph.edges.map((edge) => { const source = byId[edge.source]; const target = byId[edge.target]; return source && target ? <line key={`${edge.source}-${edge.target}`} x1={source.x} y1={source.y} x2={target.x} y2={target.y} stroke="rgba(129,140,248,.45)" strokeWidth={1 + edge.weight * 3} /> : null; })}{positions.map((node) => <motion.g key={node.id} initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} whileHover={{ scale: 1.08 }}><circle cx={node.x} cy={node.y} r="28" fill={node.group === 'method' ? '#8b5cf6' : '#06b6d4'} filter="url(#glow)"/><text x={node.x} y={node.y + 48} textAnchor="middle" className="fill-zinc-200 text-[11px]">{node.label}</text></motion.g>)}</svg>;
}
