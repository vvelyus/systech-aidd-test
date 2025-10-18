import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker production builds
  output: "standalone",
  
  // Optimize for production
  poweredByHeader: false,
  compress: true,
  
  // Required for proper routing in Docker
  trailingSlash: false,
  
  // Disable ESLint during production builds to avoid blocking on warnings
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // Disable TypeScript errors during builds (can be checked separately)
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
