import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker production builds
  output: "standalone",

  // Optimize for production
  poweredByHeader: false,
  compress: true,

  // Required for proper routing in Docker
  trailingSlash: false,
};

export default nextConfig;
