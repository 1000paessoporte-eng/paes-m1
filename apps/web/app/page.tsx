import { cookies } from "next/headers";
import {
  getAnalyticsSummary,
  getExamResult,
  getMe,
  getRecommendedNode,
  getSkillTree,
  listExamAttempts,
  type BreakdownItem,
} from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { LandingPublica } from "@/components/home/landing-publica";
import { PanelDashboard } from "@/components/dashboard/panel-dashboard";

/**
 * La portada cambia según haya sesión o no: a quien ya entró no tiene sentido
 * ofrecerle iniciar sesión otra vez, así que ve su panel de trabajo.
 */
export default async function HomePage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (!token) return <LandingPublica />;

  let user, attempts;
  try {
    [user, attempts] = await Promise.all([getMe(token), listExamAttempts(token)]);
  } catch {
    // Token vencido, inválido o API caída: se muestra la portada pública en
    // lugar de un error, para que siempre haya un camino de entrada.
    return <LandingPublica />;
  }

  // El resto del panel es complementario: si alguna de estas llamadas falla,
  // la tarjeta correspondiente se degrada a su estado vacío en vez de tumbar
  // toda la página.
  const ultimoRendido = attempts.find((a) => a.status === "submitted");
  const [nodos, recomendado, analytics, porEje] = await Promise.all([
    getSkillTree(token).catch(() => []),
    getRecommendedNode(token).catch(() => null),
    getAnalyticsSummary(token).catch(() => null),
    ultimoRendido
      ? getExamResult(ultimoRendido.attempt_id, token)
          .then((r): BreakdownItem[] => r.by_axis)
          .catch((): BreakdownItem[] => [])
      : Promise.resolve<BreakdownItem[]>([]),
  ]);

  return (
    <PanelDashboard
      user={user}
      attempts={attempts}
      nodos={nodos}
      recomendado={recomendado}
      porEje={porEje}
      analytics={analytics}
    />
  );
}
