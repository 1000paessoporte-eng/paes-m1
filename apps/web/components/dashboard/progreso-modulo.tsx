import Link from "next/link";
import type { BreakdownItem } from "@/lib/api";

/**
 * Puntaje estimado y desglose por eje del último ensayo rendido.
 *
 * El desglose sale del `by_axis` que ya calcula el backend al cerrar un
 * intento: no se recalcula acá para que el panel y la pantalla de resultado
 * nunca muestren números distintos.
 */

// El color por eje es el mismo que usa la vista previa de la landing, para que
// un eje se reconozca por su color en toda la plataforma. El orden de las
// claves es el del temario DEMRE: el backend agrupa por eje sin garantizar un
// orden, y verlos siempre en la misma secuencia hace comparables dos ensayos.
const COLOR_POR_EJE: Record<string, string> = {
  "Números": "var(--accent)",
  "Álgebra y Funciones": "var(--accent-2)",
  "Geometría": "var(--success)",
  "Probabilidad y Estadística": "var(--accent-warm)",
};

interface Props {
  puntaje: number | null;
  variacion: number | null;
  porEje: BreakdownItem[];
}

const ORDEN_EJES = Object.keys(COLOR_POR_EJE);

export function ProgresoModulo({ puntaje, variacion, porEje }: Props) {
  const ejesOrdenados = [...porEje].sort((a, b) => {
    const ia = ORDEN_EJES.indexOf(a.name);
    const ib = ORDEN_EJES.indexOf(b.name);
    // Un eje que no esté en el temario conocido va al final, no al principio.
    return (ia < 0 ? ORDEN_EJES.length : ia) - (ib < 0 ? ORDEN_EJES.length : ib);
  });

  return (
    <section className="card-panel flex flex-col p-6" aria-labelledby="h-progreso">
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="h-progreso" className="font-semibold tracking-tight">
          Mi progreso
        </h2>
        <Link
          href="/analitica"
          className="text-xs font-medium text-accent hover:underline"
        >
          Ver analítica
        </Link>
      </div>

      {puntaje == null ? (
        <EstadoVacio />
      ) : (
        <>
          <div className="mt-5 flex items-center gap-5">
            <AnilloPuntaje puntaje={puntaje} />
            <div>
              <p className="text-3xl font-bold tracking-tight tabular-nums">
                {puntaje}
                <span className="text-base font-medium text-muted">/1000</span>
              </p>
              <p className="text-xs text-muted">Puntaje estimado</p>
              {variacion != null && variacion !== 0 && (
                <p
                  className={`mt-1.5 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                    variacion > 0
                      ? "bg-success/10 text-success"
                      : "bg-danger/10 text-danger"
                  }`}
                >
                  {variacion > 0 ? "▲" : "▼"} {variacion > 0 ? "+" : ""}
                  {variacion} vs. anterior
                </p>
              )}
            </div>
          </div>

          {porEje.length > 0 && (
            <div className="mt-6 border-t border-border pt-5">
              <p className="text-xs font-medium text-muted">
                Rendimiento por eje temático
              </p>
              <ul className="mt-4 flex flex-col gap-3.5">
                {ejesOrdenados.map((eje) => (
                  <BarraEje key={eje.name} eje={eje} />
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </section>
  );
}

/** Anillo del puntaje, escalado sobre el rango real PAES (100-1000). */
function AnilloPuntaje({ puntaje }: { puntaje: number }) {
  const radio = 46;
  const circunferencia = 2 * Math.PI * radio;
  const progreso = Math.min(1, Math.max(0, (puntaje - 100) / 900));

  return (
    <svg
      width="104"
      height="104"
      viewBox="0 0 104 104"
      className="shrink-0 -rotate-90"
      role="img"
      aria-label={`Puntaje estimado ${puntaje} de 1000`}
    >
      <circle cx="52" cy="52" r={radio} fill="none" stroke="var(--border)" strokeWidth="8" />
      <circle
        cx="52"
        cy="52"
        r={radio}
        fill="none"
        stroke="var(--accent)"
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={circunferencia}
        strokeDashoffset={circunferencia * (1 - progreso)}
      />
    </svg>
  );
}

function BarraEje({ eje }: { eje: BreakdownItem }) {
  const color = COLOR_POR_EJE[eje.name] ?? "var(--accent)";
  const pct = Math.round(eje.percentage);

  return (
    <li>
      <div className="flex items-baseline justify-between gap-3 text-sm">
        <span className="truncate">{eje.name}</span>
        <span className="shrink-0 tabular-nums text-muted">
          <span className="font-semibold text-foreground">{pct}%</span>{" "}
          <span className="text-xs">
            ({eje.correct}/{eje.total})
          </span>
        </span>
      </div>
      <div
        className="mt-1.5 h-2 overflow-hidden rounded-full bg-surface-hover"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={eje.name}
      >
        <div
          className="h-full rounded-full transition-[width] duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </li>
  );
}

function EstadoVacio() {
  return (
    <div className="mt-4 flex flex-1 flex-col justify-center rounded-xl border border-dashed border-border-strong p-5 text-center">
      <p className="text-sm text-muted">
        Tu puntaje estimado y el desglose por eje aparecen acá apenas termines
        tu primer ensayo.
      </p>
    </div>
  );
}
