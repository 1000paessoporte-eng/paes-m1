import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import {
  getAnalyticsSummary,
  getExamResult,
  getMe,
  getMeta,
  getMiPlan,
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

  let user, attempts, onboardingPrevio;
  try {
    [user, attempts, onboardingPrevio] = await Promise.all([
      getMe(token),
      listExamAttempts(token),
      // Se pide acá y no abajo porque de él sale QUÉ prueba mostrar en el
      // módulo del árbol. Si falla, el panel abre en M1 como antes.
      getOnboarding(token).catch(() => null),
    ]);
  } catch {
    // Token vencido o inválido: se manda a iniciar sesión en vez de mostrar un
    // panel vacío que parecería una pérdida de datos.
    redirect("/login?next=/panel");
  }

  // El resto del panel es complementario: si alguna de estas llamadas falla,
  // la tarjeta correspondiente se degrada a su estado vacío en vez de tumbar
  // toda la página.
  // El último ensayo que DICE ALGO, no el último entregado. De él salen el
  // puntaje que encabeza el panel y el desglose por eje. Un ensayo entregado
  // sin responder tiene puntaje 100 —el piso de la escala— y todos los ejes
  // en 0%: usarlo hacía que el panel abriera con una nota que nadie sacó y un
  // diagnóstico sacado de ninguna respuesta.
  const ultimoRendido = attempts.find(
    (a) => a.status === "submitted" && a.representativo !== false && a.answered > 0
  );
  // El árbol y la recomendación salen de la prueba que el alumno de verdad va
  // a rendir, no de M1 siempre.
  //
  // `getSkillTree(token)` y `getRecommendedNode(token)` traen M1 por defecto,
  // así que quien declaró Lectora y Ciencias abría su panel y encontraba
  // "1/17 temas dominados" de Matemática y un "sigue por acá" que lo mandaba
  // a una prueba que no rinde. Se toma la primera de las que declaró; si no
  // respondió el cuestionario, se queda M1, que es la que rinden casi todos.
  const pruebaDelPanel = onboardingPrevio?.pruebas_objetivo?.[0] ?? "m1";
  const [nodos, recomendado, analytics, meta, onboarding, plan, porEje] = await Promise.all([
    getSkillTree(token, pruebaDelPanel).catch(() => []),
    getRecommendedNode(token, pruebaDelPanel).catch(() => null),
    getAnalyticsSummary(token).catch(() => null),
    getMeta(token).catch(() => null),
    getOnboarding(token).catch(() => null),
    // Si falla, el panel se dibuja sin el bloque de Pro. Un aviso comercial no
    // vale romper la pantalla principal del alumno.
    getMiPlan(token).catch(() => null),
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
      plan={plan}
    />
  );
}
