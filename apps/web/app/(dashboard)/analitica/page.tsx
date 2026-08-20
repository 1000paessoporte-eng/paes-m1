import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getAnalyticsSummary, getDiagnostico, type Diagnostico } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { StatTile } from "@/components/analytics/stat-tile";
import { TimeInvestedChart } from "@/components/analytics/time-invested-chart";
import { AccuracyChart } from "@/components/analytics/accuracy-chart";
import { DiagnosticoErrores } from "@/components/analytics/diagnostico-errores";
import { DiagnosticoRitmo } from "@/components/analytics/diagnostico-ritmo";
import { Constancia } from "@/components/analytics/constancia";
import { MejoraPrecision } from "@/components/analytics/mejora-precision";
import { EstadoVacio } from "@/components/estado-vacio";

export const metadata = {
  title: "Analítica",
  description: "Tiempo invertido, tasa de acierto y rachas de práctica.",
};


export default async function DashboardAnaliticoPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let summary;
  try {
    summary = await getAnalyticsSummary(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/analitica");
    throw err;
  }

  // El diagnóstico es lo nuevo de esta pantalla, pero no es lo único: si
  // falla, la analítica de siempre se muestra igual. Un dato de más no puede
  // llevarse por delante a los que ya funcionaban.
  let diagnostico: Diagnostico | null = null;
  try {
    diagnostico = await getDiagnostico(token);
  } catch {
    diagnostico = null;
  }

  if (summary.total_questions_answered === 0) {
    return (
      <EstadoVacio
        title="Tu analítica aparece con tu primer ensayo"
        description="Acá vas a ver cuánto tiempo practicaste, cómo evoluciona tu tasa de acierto y tu racha de días seguidos. Necesita al menos un ensayo rendido para tener algo que mostrar."
        accion={{ href: "/examen", label: "Rendir mi primer ensayo →" }}
        icon={
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 20V10M12 20V4M20 20v-7" />
          </svg>
        }
      />
    );
  }

  const accuracyPct =
    summary.overall_accuracy != null ? `${Math.round(summary.overall_accuracy * 100)}%` : "—";

  return (
    <div>
      <h1 className="text-2xl font-semibold">Analítica</h1>
      <p className="mt-1 text-sm text-muted">
        Cuánto has sostenido, cuánto has mejorado y qué te conviene corregir.
      </p>

      {/* Constancia y precisión van PRIMERO, antes del diagnóstico y de los
          gráficos. Los tres bloques de abajo dicen qué corregir, y abrir una
          pantalla de progreso con una lista de errores es la forma más rápida
          de que alguien la cierre. Lo que sostuvo hasta acá se ve antes que lo
          que le falta. */}
      <div className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Constancia
          dias={summary.daily}
          rachaActual={summary.exam_streak_days || summary.current_streak_days}
          mejorRacha={summary.best_exam_streak_days}
          diasActivos={summary.active_days}
        />
        <MejoraPrecision dias={summary.daily} />
      </div>

      {/* El diagnóstico va ARRIBA de los gráficos: los gráficos dicen cuánto
          hiciste, esto dice qué arreglar. Lo segundo es lo accionable. */}
      <div className="mt-6">
        {diagnostico && <DiagnosticoErrores errores={diagnostico.errores} />}
        {diagnostico?.ritmo && <DiagnosticoRitmo ritmo={diagnostico.ritmo} />}
      </div>

      {/* Los totales de siempre. Van DESPUÉS de lo que se mueve: son el
          respaldo del relato, no el relato. */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <StatTile
          label="Precisión global"
          value={accuracyPct}
          icon={
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9" />
              <circle cx="12" cy="12" r="5" />
              <circle cx="12" cy="12" r="1" fill="currentColor" />
            </svg>
          }
        />
        <StatTile
          label="Preguntas respondidas"
          value={String(summary.total_questions_answered)}
          icon={
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
          }
        />
        <StatTile
          label="Tiempo total practicado"
          value={`${Math.round(summary.total_minutes_practiced)} min`}
          icon={
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="13" r="8" />
              <path d="M12 9v4l3 2M9 2h6M12 2v2" />
            </svg>
          }
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <TimeInvestedChart
          data={summary.daily.map((d) => ({ date: d.date, minutes: d.minutes_practiced }))}
        />
        <AccuracyChart
          data={summary.daily.map((d) => ({ date: d.date, accuracy: d.accuracy }))}
        />
      </div>
    </div>
  );
}
