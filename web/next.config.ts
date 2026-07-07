import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Image budgets are a design contract (card thumbs <40KB, lead <60KB); the
  // ingestion layer resizes to webp before store. Formats declared here.
  images: {
    formats: ["image/webp"],
  },
};

export default nextConfig;
