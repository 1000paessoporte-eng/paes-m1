import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Túnel público (Cloudflare) usado para probar la app fuera de la LAN.
  allowedDevOrigins: ["healing-aims-photographs-guaranteed.trycloudflare.com"],
};

export default nextConfig;
