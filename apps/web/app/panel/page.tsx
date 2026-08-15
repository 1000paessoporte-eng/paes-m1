import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import {
  getAnalyticsSummary,
  getExamResult,
  getMe,
  getMeta,
  getOnboarding,
  getRecommendedNode,
  getSkillTree,
  listExamAttempts,
  type BreakdownItem,
} from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { PanelDashboard } from "@/components/dashboard/panel-dashboard";

export const metadata = {
  title: "Mi panel",
  description: "Tu progreso, tus ensayos y qué practicar ahora.",
};

/**
 * Panel del estudiante: la pantalla de trabajo una vez iniciada la sesión.
 *
 * Vive en su propia ruta (y no dentro de "/") para que la portada pública y el
 * panel sean dos páginas distintas: la de "/" es la cara del producto para
 * quien llega desde una búsqueda, esta es la herramienta para quien ya entró.
 */
export default async function PanelPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (!token) redirect("/login?next=/panel");

  let user, attempts;
  try {
    [user, attempts] = await Promise.all([getMe(token), listExamAttempts(token)]);
  } catch {
    // Token vencido o inválido: se manda a iniciar sesión en vez de mostrar un
    // panel vacío que parecería una pérdida de datos.
    redirect("/login?next=/panel");
  }

  // El resto del panel es complementario: si alguna de estas llamadas falla,
  // la tarjeta correspondiente se degrada a su estado vacío en vez de tumbar
  // toda la página.
  const ultimoRendido = attempts.find((a) => a.status === "submitted");
  const [nodos, recomendado, analytics, meta, onboarding, porEje] = await Promise.all([
    getSkillTree(token).catch(() => []),
    getRecommendedNode(token).catch(() => null),
    getAnalyticsSummary(token).catch(() => null),
    getMeta(token).catch(() => null),
    getOnboarding(token).catch(() => null),
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
      ejesDe={ultimoRendido?.subject ?? null}
      analytics={analytics}
      meta={meta}
      onboarding={onboarding}
    />
  );
}
