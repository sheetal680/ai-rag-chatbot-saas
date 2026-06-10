import type { NextConfig } from "next";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const SECURITY_HEADERS = [
  // Allow embedding in any iframe
  { key: "X-Frame-Options", value: "ALLOWALL" },
  { key: "Content-Security-Policy", value: "frame-ancestors *" },
  // Stops MIME-type sniffing
  { key: "X-Content-Type-Options", value: "nosniff" },
  // Controls how much referrer info is sent
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  // Disable browser features not needed by this app
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=(), payment=()",
  },
  // Basic XSS protection for older browsers
  { key: "X-XSS-Protection", value: "1; mode=block" },
];

const nextConfig: NextConfig = {
  reactStrictMode: true,

  // Apply security headers to every route
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: SECURITY_HEADERS,
      },
    ];
  },

  // Optional: proxy /api/backend/* → FastAPI (useful if you ever move to
  // server-side data fetching — not required while Axios calls directly)
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${API_URL}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
