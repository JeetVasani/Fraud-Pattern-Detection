import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/random-forest',
        destination: '/components/random-forest',
      },
      {
        source: '/Graph-Visulaization',
        destination: '/components/Graph-Visulaization',
      },
    ];
  },
};

export default nextConfig;
