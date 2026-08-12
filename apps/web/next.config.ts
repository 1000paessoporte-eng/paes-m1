import type { NextConfig } from "next";

// El backend FastAPI corre en el mismo host que la web (puerto 8000).
const API_ORIGIN = process.env.API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Túnel público (Cloudflare) usado para probar la app fuera de la LAN.
  allowedDevOrigins: ["healing-aims-photographs-guaranteed.trycloudflare.com"],

  // El navegador habla siempre con el origen de la web y esta reenvía a la API.
  // Así los equipos de la LAN solo necesitan un puerto abierto y la IP del host
  // no queda quemada en el bundle del cliente.
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` }];
  },
};

export default nextConfig;
