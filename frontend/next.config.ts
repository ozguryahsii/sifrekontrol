import type { NextConfig } from "next";

const API_URL = process.env.SIFREKONTROL_API ?? "http://127.0.0.1:3003";

const nextConfig: NextConfig = {
  async rewrites() {
    // Şifre tarayıcıdan yalnızca bu sunucuya, oradan da localhost'taki
    // Python API'sine gider; makine dışına hiçbir istek çıkmaz.
    return [{ source: "/api/:path*", destination: `${API_URL}/api/:path*` }];
  },
};

export default nextConfig;
