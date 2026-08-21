import type { Hito } from "@/lib/progreso";

/**
 * Lo que ya consiguió, y lo que tiene más cerca de conseguir.
 *
 * Los hitos son HECHOS contables --ensayos rendidos, preguntas respondidas,
 * puntos cruzados--, nunca elogios. "Vas muy bien" no lo cree nadie que acaba
 * de fallar catorce preguntas; "respondiste 250 preguntas" es verificable y el
 * alumno sabe que le costó.
 *
 * Y al lado de lo logrado va siempre lo siguiente, con cuánto falta: un muro de
 * medallas cuenta dónde estuvo, no para qué volver mañana.
 */
export function HitosPanel({
  logrados,
  siguientes,
}: {
  logrados: Hito[];
  siguientes: Hito[];
}) {
  if (logrados.length === 0 && siguientes.length === 0) return null;

  // Solo los dos más cerca: la lista completa de metas pendientes se lee como
  // una cuenta de lo que le falta, que es exactamente el efecto contrario.
  const proximos = siguientes.slice(0, 2);

  return (
    <section className="mb-6 rounded-2xl border border-border bg-surface p-5 sm:p-6">
      <h2 className="text-sm font-semibold">Lo que llevas conseguido</h2>

      {logrados.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-2">
          {logrados.map((h) => (
            <li
              key={h.titulo}
              className="flex items-center gap-1.5 rounded-full border border-success/30 bg-success/10 px-3 py-1.5 text-xs font-medium text-success"
            >
              <svg
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5" />
              </svg>
              {h.titulo}
            </li>
          ))}
        </ul>
      )}

      {proximos.length > 0 && (
        <>
          <h3 className="mt-6 text-xs font-medium tracking-wide text-muted uppercase">
            Lo que tienes más cerca
          </h3>
          <ul className="mt-3 space-y-3.5">
            {proximos.map((h) => {
              const falta = h.meta - h.actual;
              const avance = Math.min(100, (h.actual / h.meta) * 100);
              return (
                <li key={h.titulo}>
                  <div className="flex items-baseline justify-between gap-3 text-sm">
                    <span className="font-medium">{h.titulo}</span>
                    <span className="shrink-0 text-xs text-muted tabular-nums">
                      te {falta === 1 ? "falta" : "faltan"}{" "}
                      {falta.toLocaleString("es-CL")}{" "}
                      {falta === 1 ? h.unidadSingular : h.unidad}
                    </span>
                  </div>
                  <div
                    className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-surface-hover"
                    role="progressbar"
                    aria-valuenow={h.actual}
                    aria-valuemin={0}
                    aria-valuemax={h.meta}
                    aria-label={h.titulo}
                  >
                    <div
                      className="h-full rounded-full bg-accent transition-[width] duration-700"
                      style={{ width: `${avance}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </section>
  );
}
