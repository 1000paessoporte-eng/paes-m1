import { cookies } from "next/headers";
import { getMe, listExamAttempts } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { LandingPublica } from "@/components/home/landing-publica";
import { PanelInicio } from "@/components/home/panel-inicio";

/**
 * La portada cambia según haya sesión o no: a quien ya entró no tiene sentido
 * ofrecerle iniciar sesión otra vez, así que ve su panel con el estado de sus
 * ensayos y los accesos a todo lo que hace la plataforma.
 */
export default async function HomePage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (!token) return <LandingPublica />;

  try {
    const [user, attempts] = await Promise.all([
      getMe(token),
      listExamAttempts(token),
    ]);
    return <PanelInicio user={user} attempts={attempts} />;
  } catch {
    // Token vencido, inválido o API caída: se muestra la portada pública en
    // lugar de un error, para que siempre haya un camino de entrada.
    return <LandingPublica />;
  }
}
