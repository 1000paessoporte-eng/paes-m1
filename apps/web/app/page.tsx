import { cookies } from "next/headers";
import { redirect } from "next/navigation";
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

  return <LandingPublica />;
}
