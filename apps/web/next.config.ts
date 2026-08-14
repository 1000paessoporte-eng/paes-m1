import path from "node:path";
import type { NextConfig } from "next";

// A qué backend habla esta instancia de la web.
//
// - Producción: API_URL, seteada en Vercel.
// - Preview: no hay API_URL, así que se deriva de la URL de rama que Vercel
//   asigna a este despliegue (VERCEL_BRANCH_URL, del tipo
//   "milpaes-web-git-<rama>-<scope>.vercel.app"). Cambiando el nombre del
//   proyecto se obtiene la URL de rama del backend, que Vercel construye con
//   el mismo patrón porque ambos proyectos siguen el mismo repo y la misma
//   rama. Así cada PR queda apuntando a SU backend y a la base de preview,
//   nunca a los datos de producción.
// - Local: la API en el puerto 8000.
const BRANCH_API_ORIGIN = process.env.VERCEL_BRANCH_URL
  ? `https://${process.env.VERCEL_BRANCH_URL.replace("milpaes-web", "milpaes-api")}`
  : undefined;

const API_ORIGIN =
  process.env.API_URL ?? BRANCH_API_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Build standalone (server.js + node_modules mínimos) para la imagen
  // Docker de produccion -- ver apps/web/Dockerfile. Vercel hace su propio
  // empaquetado/tracing y choca con output "standalone", asi que solo se usa
  // fuera de Vercel.
  ...(process.env.VERCEL ? {} : { output: "standalone" as const }),
  // Monorepo: sin esto, el file tracing de standalone puede confundirse con
  // el lockfile del workspace en la raiz y quedar en la carpeta equivocada.
  outputFileTracingRoot: path.join(__dirname, "../../"),

  // Orígenes permitidos en desarrollo. Next solo autoriza "localhost" por
  // defecto: abrir el dev server por 127.0.0.1 o por la IP de la LAN devuelve
  // 403 en los chunks y la página carga sin JavaScript, sin más pista que un
  // aviso en la consola del servidor.
  allowedDevOrigins: [
    "127.0.0.1",
    "192.168.1.11",
    // Túnel público (Cloudflare) usado para probar la app fuera de la LAN.
    "healing-aims-photographs-guaranteed.trycloudflare.com",
  ],

  // El navegador habla siempre con el origen de la web y esta reenvía a la API.
  // Así los equipos de la LAN solo necesitan un puerto abierto y la IP del host
  // no queda quemada en el bundle del cliente.
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` }];
  },
};

export default nextConfig;
