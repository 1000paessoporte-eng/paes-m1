import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getContentStats, getProductos, type ContentStats } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { LandingPublica } from "@/components/home/landing-publica";

/**
 * Portada pública: lo que ve quien llega a 1000paes.cl desde una búsqueda.
 *
 * Con la sesión iniciada no tiene sentido volver a explicar el producto ni
 * ofrecer "crear cuenta", así que se pasa al panel. La cookie solo se lee para
 * decidir eso; el panel valida el token de verdad contra la API.
 */
export default async function HomePage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (token) redirect("/panel");

  // Las cifras del banco salen de la base, no de una constante. Si la API no
  // responde, la portada se dibuja sin ellas: mejor un dato menos que un
  // número inventado, que es la primera regla del proyecto.
  let stats: ContentStats | null = null;
  try {
    stats = await getContentStats();
  } catch {
    stats = null;
  }

  // Igual que las cifras: si el catálogo no responde, la portada muestra los
  // planes sin botón de compra en vez de ofrecer uno que llevaría a un error.
  let pagoDisponible = false;
  try {
    pagoDisponible = (await getProductos()).pago_disponible;
  } catch {
    pagoDisponible = false;
  }

  return <LandingPublica stats={stats} pagoDisponible={pagoDisponible} />;
}
