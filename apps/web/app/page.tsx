import type { Metadata } from "next";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import {
  getContentStats,
  getProductos,
  getUniversidades,
  getUsoPublico,
  type ContentStats,
  type Universidad,
  type UsoPublico,
} from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { LandingPublica } from "@/components/home/landing-publica";

// La portada es la página que más se enlaza desde fuera, y llega con toda
// clase de colas ("?fbclid=", "?utm_source="). Sin canónica, cada una de esas
// variantes es una URL distinta para Google y el peso del dominio se reparte
// entre copias de la misma página.
export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

export default async function HomePage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (token) redirect("/panel");

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
