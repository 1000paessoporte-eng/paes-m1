import type { Metadata } from "next";
import {
  getContentStats,
  getProductos,
  getUniversidades,
  getUsoPublico,
  type ContentStats,
  type Universidad,
  type UsoPublico,
} from "@/lib/api";
import { LandingPublica } from "@/components/home/landing-publica";

// La portada es la página que más se enlaza desde fuera, y llega con toda
// clase de colas ("?fbclid=", "?utm_source="). Sin canónica, cada una de esas
// variantes es una URL distinta para Google y el peso del dominio se reparte
// entre copias de la misma página.
export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

// A quien ya tiene sesión lo manda al panel `proxy.ts`, antes de llegar acá.
// Vivía en esta función, leyendo la cookie con `cookies()`, y eso obligaba a
// renderizar la portada en cada visita: era la única página pública que no se
// cacheaba en el CDN. Ver el comentario de `proxy.ts`.
//
// Con la cookie fuera, las cuatro llamadas de abajo ya vienen cacheadas y la
// página se sirve desde el borde. Se revalida cada diez minutos: las cifras
// del banco y del uso cambian cuando alguien agrega preguntas o rinde un
// ensayo, no en el segundo.
export const revalidate = 600;

export default async function HomePage() {
  // Las cifras del banco salen de la base, no de una constante. Si la API no
  // responde, la portada se dibuja sin ellas: mejor un dato menos que un
  // número inventado, que es la primera regla del proyecto. Lo mismo vale para
  // las otras tres llamadas, y por eso van en paralelo y cada una con su
  // propio respaldo: que se caiga una no puede dejar la portada en blanco.
  const [stats, uso, universidades, pagoDisponible] = await Promise.all([
    conRespaldo<ContentStats | null>(() => getContentStats(), null),
    conRespaldo<UsoPublico | null>(() => getUsoPublico(), null),
    conRespaldo<Universidad[]>(() => getUniversidades(), []),
    // Si el catálogo de productos no responde, la portada muestra los planes
    // sin botón de compra en vez de ofrecer uno que llevaría a un error.
    conRespaldo(async () => (await getProductos()).pago_disponible, false),
  ]);

  return (
    <LandingPublica
      stats={stats}
      uso={uso}
      universidades={universidades}
      pagoDisponible={pagoDisponible}
    />
  );
}

async function conRespaldo<T>(pedir: () => Promise<T>, respaldo: T): Promise<T> {
  try {
    return await pedir();
  } catch {
    return respaldo;
  }
}
