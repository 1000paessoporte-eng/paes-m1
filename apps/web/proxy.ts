import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { TOKEN_COOKIE } from "@/lib/auth";

/**
 * Manda al panel a quien ya tiene sesión, y deja la portada quieta.
 *
 * Esto vivía dentro de `app/page.tsx`, que leía la cookie con `cookies()` para
 * decidir entre la landing y el panel. Leer la cookie durante el render obliga
 * a Next a tratar la portada como dinámica, y el efecto se veía en producción:
 * era —junto a /planes— la ÚNICA página pública que no se cacheaba en el CDN
 * (`x-vercel-cache: MISS`, `cache-control: no-store`), mientras /carrera,
 * /aprender y el resto respondían desde el borde en ~190 ms. Cada visita
 * anónima pagaba un render entero más cuatro llamadas a la API: ~600 ms en
 * caliente y hasta 1,8 s en frío.
 *
 * Y es la página que peor lo puede permitirse: todo el tráfico que llega de
 * Google cae ahí SIN sesión, y el tiempo hasta el primer byte pesa en los
 * Core Web Vitals con los que Google ordena los resultados.
 *
 * Acá arriba la decisión cuesta lo que cuesta mirar una cookie, y corre en el
 * borde antes de tocar el render. La portada vuelve a ser estática.
 *
 * En Next 16 este archivo se llama `proxy.ts`: la convención `middleware.ts`
 * quedó deprecada y renombrada, con la misma funcionalidad.
 */
export function proxy(request: NextRequest) {
  if (request.cookies.get(TOKEN_COOKIE)?.value) {
    return NextResponse.redirect(new URL("/panel", request.url));
  }
  return NextResponse.next();
}

export const config = {
  // SOLO la portada. Un matcher más ancho pondría este archivo en el camino de
  // cada petición del sitio —incluidos los assets— para resolver algo que pasa
  // en una sola ruta.
  matcher: "/",
};
