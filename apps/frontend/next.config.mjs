const nextConfig = {
  output: 'standalone',
  experimental: { typedRoutes: true },
  env: {
    NEXT_PUBLIC_V5_API_URL: process.env.NEXT_PUBLIC_V5_API_URL ?? 'http://localhost:8001',
    NEXT_PUBLIC_V3_API_URL: process.env.NEXT_PUBLIC_V3_API_URL ?? 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/v3/:path*',
        destination: `${process.env.NEXT_PUBLIC_V3_API_URL ?? 'http://localhost:8000'}/api/v3/:path*`,
      },
      {
        source: '/api/v5/:path*',
        destination: `${process.env.NEXT_PUBLIC_V5_API_URL ?? 'http://localhost:8001'}/api/v1/:path*`,
      },
    ];
  },
};
export default nextConfig;
