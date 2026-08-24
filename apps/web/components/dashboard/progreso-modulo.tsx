"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import type { BreakdownItem, Subject } from "@/lib/api";
import { NOMBRE_CORTO } from "@/lib/colores-prueba";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { BarraProgreso } from "@/components/ui/barra-progreso";

/**
 * Puntaje estimado y desglose por eje del último ensayo rendido.
 *
 * El desglose sale del `by_axis` que ya calcula el backend al cerrar un
 * intento: no se recalcula acá para que el panel y la pantalla de resultado
 * nunca muestren números distintos.
 */

// Un eje se reconoce por su color en toda la plataforma, así que el mapa cubre
// los trece ejes de las cinco pruebas y no solo los de matemática. Dentro de
// cada prueba los colores se separan entre sí; entre pruebas pueden repetirse,
// porque un ensayo nunca mezcla dos.
const COLOR_POR_EJE: Record<string, string> = {
  // Competencia Matemática
  "Números": "var(--accent)",
  "Álgebra y Funciones": "var(--accent-2)",
  "Geometría": "var(--success)",
  "Probabilidad y Estadística": "var(--accent-warm)",
  // Competencia Lectora
  "Localizar información": "var(--accent)",
  "Interpretar y relacionar": "var(--accent-2)",
  "Evaluar y reflexionar": "var(--success)",
  // Ciencias
  "Biología": "var(--success)",
  "Física": "var(--accent)",
  "Química": "var(--accent-2)",
  // Historia y Ciencias Sociales
  "Historia": "var(--accent)",
  "Formación ciudadana": "var(--accent-2)",
  "Economía y sociedad": "var(--accent-warm)",
};

const NOMBRE_PRUEBA: Record<string, string> = {
  lectora: "Competencia Lectora",
  m1: "Matemática M1",
  m2: "Matemática M2",
  ciencias: "Ciencias",
  historia: "Historia y Cs. Sociales",
};

interface Props {
  puntaje: number | null;
  variacion: number | null;
  /** La prueba del último ensayo. El puntaje no se lee sin ella. */
  prueba: Subject | null;
  porEje: BreakdownItem[];
  /** Prueba del ensayo del que salen estos ejes. */
  ejesDe?: string | null;
}

// El orden del temario DEMRE: el backend agrupa por eje sin garantizar un
// orden, y verlos siempre en la misma secuencia hace comparables dos ensayos.
const ORDEN_EJES = Object.keys(COLOR_POR_EJE);

export function ProgresoModulo({ puntaje, prueba, variacion, porEje, ejesDe }: Props) {
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
                <NumeroAnimado valor={puntaje} />
                <span className="text-base font-medium text-muted">/1000</span>
              </p>
              <p className="text-xs text-muted">
                Puntaje estimado{prueba ? ` · ${NOMBRE_CORTO[prueba]}` : ""}
              </p>
              {variacion != null && variacion !== 0 && (
                <p
                  className={`mt-1.5 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                    variacion > 0
                      ? "bg-success/10 text-success"
                      : "bg-danger/10 text-danger"
                  }`}
                >
                  {variacion > 0 ? "▲" : "▼"} {variacion > 0 ? "+" : ""}
                  {variacion} vs. tu ensayo anterior de esta prueba
                </p>
              )}
            </div>
          </div>

          {porEje.length > 0 && (
            <div className="mt-6 border-t border-border pt-5">
              {/* De qué ensayo salen estos números. Sin esto, un ensayo
                  abandonado deja los ejes en 0% y parece que se perdieron los
                  datos de todos los anteriores. */}
              <p className="text-xs font-medium text-muted">
                Rendimiento por eje
                {ejesDe && NOMBRE_PRUEBA[ejesDe]
                  ? ` · último ensayo de ${NOMBRE_PRUEBA[ejesDe]}`
                  : " · último ensayo"}
              </p>
              <ul className="mt-4 flex flex-col gap-3.5">
                {ejesOrdenados.map((eje, i) => (
                  <BarraEje key={eje.name} eje={eje} orden={i} />
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </section>
  );
}

/**
 * Anillo del puntaje, escalado sobre el rango real PAES (100-1000).
 *
 * El trazo se dibuja al aparecer, como si alguien lo estuviera marcando. Es la
 * cifra que el estudiante viene a mirar, así que se gana medio segundo de
 * atención antes de quedarse quieta.
 */
function AnilloPuntaje({ puntaje }: { puntaje: number }) {
  const quieto = useReducedMotion();
  const radio = 46;
  const circunferencia = 2 * Math.PI * radio;
  const progreso = Math.min(1, Math.max(0, (puntaje - 100) / 900));
  const offsetFinal = circunferencia * (1 - progreso);

  return (
    <svg
      width="104"
      height="104"
      viewBox="0 0 104 104"
      className="shrink-0 -rotate-90"
      role="img"
      aria-label={`Puntaje estimado ${puntaje} de 1000`}
    >
      <circle
        cx="52"
        cy="52"
        r={radio}
        fill="none"
        stroke="var(--border)"
        strokeWidth="8"
      />
      <motion.circle
        cx="52"
        cy="52"
        r={radio}
        fill="none"
        stroke="var(--accent)"
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={circunferencia}
        initial={quieto ? false : { strokeDashoffset: circunferencia }}
        whileInView={{ strokeDashoffset: offsetFinal }}
        viewport={{ once: true }}
        transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
        style={{ strokeDashoffset: offsetFinal }}
      />
    </svg>
  );
}

function BarraEje({ eje, orden }: { eje: BreakdownItem; orden: number }) {
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
      <div className="mt-1.5">
        {/* Las barras entran en cascada, de arriba abajo: el ojo las recorre en
            el mismo orden en que se leen las etiquetas. */}
        <BarraProgreso
          porcentaje={pct}
          color={color}
          etiqueta={eje.name}
          delay={orden * 0.08}
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
