const repoName = 'arXiv-paper-summariser';
const isGithubPages = process.env.GITHUB_PAGES === 'true';

const nextConfig = {
  output: 'export',
  distDir: 'out',
  trailingSlash: true,
  basePath: isGithubPages ? `/${repoName}` : '',
  assetPrefix: isGithubPages ? `/${repoName}/` : '',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_V5_API_URL: process.env.NEXT_PUBLIC_V5_API_URL ?? 'http://localhost:8001',
    NEXT_PUBLIC_V3_API_URL: process.env.NEXT_PUBLIC_V3_API_URL ?? 'http://localhost:8000',
  },
};

export default nextConfig;
