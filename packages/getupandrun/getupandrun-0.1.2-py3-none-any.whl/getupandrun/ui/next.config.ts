import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Use PORT from environment (Railway sets this automatically)
  env: {
    PORT: process.env.PORT || "3000",
  },
};

export default nextConfig;
