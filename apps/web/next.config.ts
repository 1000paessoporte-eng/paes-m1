import path from "node:path";
import type { NextConfig } from "next";

// A qué backend habla esta instancia de la web.
//
// - Producción y preview: API_URL, seteada en Vercel para cada entorno. En
//   preview apunta a milpaes-api-preview.vercel.app, un alias estable del
//   backend de pruebas, que usa la base `paes_preview` y no la de producción.
//
//   Se intentó derivar la URL del backend desde VERCEL_BRANCH_URL, pero no
//   sirve: con nombres de rama largos Vercel trunca el alias y le agrega un
//   hash DISTINTO en cada proyecto (…-git-mi-rama-488173 en la API frente a
//   …-git-mi-rama-1146d8 en la web), así que una URL no se puede deducir de la
//   otra. El alias hay que reapuntarlo cuando un PR cambia el backend:
//   `vercel alias set <deployment> milpaes-api-preview.vercel.app`.
//
// - Local: la API en el puerto 8000.
const API_ORIGIN = process.env.API_URL ?? "http://127.0.0.1:8000";

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

  // Cabeceras de seguridad. Producción solo traía HSTS, que lo pone Vercel:
  // faltaba todo lo demás en un sitio con cuentas, sesiones y datos de
  // estudiantes que en su mayoría son menores de edad.
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // Nadie puede meter el sitio en un iframe: sin esto, una página
          // ajena puede superponer botones invisibles sobre los nuestros y
          // hacer que el estudiante haga clic donde no cree (clickjacking).
          { key: "X-Frame-Options", value: "DENY" },
          // El navegador respeta el Content-Type declarado en vez de adivinar
          // por el contenido, que es como un archivo subido termina
          // ejecutándose como script.
          { key: "X-Content-Type-Options", value: "nosniff" },
          // Al salir del sitio se manda el dominio, nunca la ruta completa: la
          // URL de un ensayo o de una recuperación de contraseña no tiene por
          // qué viajar en el Referer.
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          // No usamos cámara, micrófono ni ubicación: se apagan de entrada.
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), payment=()",
          },
          // ── Content-Security-Policy ──────────────────────────────────
          //
          // Es la cabecera que más importa acá, y la razón es concreta: el
          // token de sesión vive en una cookie que SÍ puede leer JavaScript
          // (decisión consciente, ver apps/api/src/paes_api/core/security.py).
          // Con eso, un XSS no es "sale un alert": es la sesión del estudiante
          // en manos de otro.
          //
          // La pieza clave contra eso es `connect-src 'self'`: aunque alguien
          // lograra inyectar código y leer el token, el navegador no lo deja
          // mandarlo a ningún servidor que no sea el nuestro. Sin salida, el
          // robo no se completa.
          //
          // `script-src` lleva 'unsafe-inline' porque Next inyecta scripts en
          // línea para hidratar y el tema se aplica con uno antes de pintar.
          // Quitarlo pide nonces por petición, y eso es incompatible con las
          // páginas prerenderizadas, que acá son casi todas. Aun así el resto
          // de directivas sostienen lo importante.
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              // Sin esto, inyectar <base> secuestra TODAS las rutas relativas.
              "base-uri 'self'",
              // Nada de Flash, applets ni embeds: vía clásica de ejecución.
              "object-src 'none'",
              // Un formulario inyectado no puede mandar datos fuera. El pago
              // no se rompe: Flow se abre navegando, no enviando un form.
              "form-action 'self'",
              // Lo mismo que X-Frame-Options, para navegadores que ya solo
              // miran la CSP.
              "frame-ancestors 'none'",
              "img-src 'self' data: blob:",
              // next/font descarga las tipografías en el build y las sirve
              // desde el propio dominio: no hace falta abrir Google Fonts.
              "font-src 'self' data:",
              "style-src 'self' 'unsafe-inline'",
              // Analytics y Speed Insights de Vercel se sirven desde el mismo
              // dominio (/_vercel/...), así que 'self' los cubre.
              "script-src 'self' 'unsafe-inline' https://accounts.google.com",
              "connect-src 'self' https://accounts.google.com",
              // El login con Google todavía está apagado, pero la directiva ya
              // lo contempla: si se enciende y esto no está, falla en silencio.
              "frame-src https://accounts.google.com",
              "upgrade-insecure-requests",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
