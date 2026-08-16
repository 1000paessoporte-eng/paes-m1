import Link from "next/link";
import type { Meta } from "@/lib/api";
import { BarraProgreso } from "@/components/ui/barra-progreso";

/**
 * La meta, vista desde el panel.
 *
 * Es lo primero que un estudiante quiere saber al entrar —cuánto le falta para
 * la carrera que quiere— y hasta ahora vivía escondido en su propia página.
 * Muestra la primera preferencia que todavía no alcanza, porque es la que está
 * en juego; las que ya alcanza no necesitan atención.
 */
export function MetaModulo({ meta }: { meta: Meta | null }) {
  const postulaciones = meta?.postulaciones ?? [];

  if (postulaciones.length === 0) {
    return (
      <section className="card-panel flex flex-col p-6" aria-labelledby="h-meta">
        <h2 id="h-meta" className="font-semibold tracking-tight">
          Mi meta
        </h2>
        <p className="mt-2 flex-1 text-sm leading-relaxed text-muted">
          Elige la carrera a la que quieres entrar y la plataforma te dice cuánto
          te falta y dónde rinde más estudiar. Cada carrera pondera las pruebas
          distinto.
        </p>
        <Link
          href="/meta"
          className="mt-4 inline-block self-start rounded-lg border border-border px-4 py-2 text-sm font-medium transition-colors hover:bg-surface-hover"
        >
          Elegir mi carrera →
        </Link>
      </section>
    );
  }

  // La que está en juego: la preferencia más alta que aún no se alcanza. Si ya
  // alcanza todas, se muestra la primera.
  const foco = postulaciones.find((p) => p.alcanza !== true) ?? postulaciones[0];
  const minimo = foco.carrera.ponderado_min;

  return (
    <section className="card-panel flex flex-col p-6" aria-labelledby="h-meta">
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="h-meta" className="font-semibold tracking-tight">
          Mi meta
        </h2>
        <Link href="/meta" className="text-xs font-medium text-accent hover:underline">
          Ver mi lista
        </Link>
      </div>

      <p className="mt-3 text-sm font-medium">{foco.carrera.nombre}</p>
      <p className="text-xs text-muted">
        {foco.carrera.universidad} · preferencia {foco.preferencia} de{" "}
        {postulaciones.length}
      </p>

      {foco.ponderado != null && minimo != null ? (
        <div className="mt-4">
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-2xl font-bold tabular-nums">{Math.round(foco.ponderado)}</span>
            <span
              className={
                "rounded-full px-2.5 py-0.5 text-xs font-semibold " +
                (foco.alcanza
                  ? "bg-success/10 text-success"
                  : "bg-warning/10 text-warning")
              }
            >
              {foco.alcanza ? "Alcanzas el mínimo" : `Te faltan ${foco.brecha} pts`}
            </span>
          </div>
          <div className="mt-2">
            <BarraProgreso
              porcentaje={Math.min(100, (foco.ponderado / minimo) * 100)}
              color={foco.alcanza ? "var(--success)" : "var(--accent)"}
              etiqueta={`${foco.carrera.nombre}: ${foco.ponderado} de ${minimo}`}
              alto="h-1.5"
            />
          </div>
          <p className="mt-1 text-xs text-muted">Mínimo para postular: {minimo} pts</p>
        </div>
      ) : foco.ponderado != null ? (
        <div className="mt-4">
          <span className="text-2xl font-bold tabular-nums">{Math.round(foco.ponderado)}</span>
          <p className="mt-1 text-xs text-muted">
            Tu puntaje ponderado. Esta carrera no publicó un mínimo de postulación.
          </p>
        </div>
      ) : (
        <p className="mt-4 text-xs text-warning">
          Falta {foco.faltantes.slice(0, 2).join(", ")} para calcular tu puntaje.
        </p>
      )}

      {meta?.plan_para && meta.plan.length > 0 && (
        <p className="mt-4 border-t border-border pt-3 text-xs leading-relaxed text-muted">
          Lo que más te acerca ahora:{" "}
          <Link
            href={
              meta.plan[0].has_lesson
                ? `/aprender/${meta.plan[0].code}`
                : `/practicar/${meta.plan[0].code}`
            }
            className="font-medium text-accent hover:underline"
          >
            {meta.plan[0].name}
          </Link>
        </p>
      )}
    </section>
  );
}
