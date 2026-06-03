import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: { ink: '#0a0a0b', panel: '#111114', muted: '#70707a' },
      boxShadow: { glow: '0 0 80px rgba(99,102,241,.18)' },
    },
  },
  plugins: [],
};

export default config;
