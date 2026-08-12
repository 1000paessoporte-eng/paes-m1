"use client";

import { useId, useState } from "react";
import type { ExamAttemptSummary } from "@/lib/api";

/**
 * Evolución del puntaje a lo largo de los ensayos rendidos.
 *
 * Es una serie única, por lo que no lleva caja de leyenda: el título nombra la
 * serie. Los ejes y la grilla van en tonos recesivos para que la línea sea lo
 * único prominente, y solo el último punto lleva etiqueta directa: rotular
 * todos los puntos satura el gráfico sin agregar información.
 */

interface Props {
  /** Intentos del más reciente al más antiguo, como los entrega la API. */
  intentos: ExamAttemptSummary[];
}

const ANCHO = 640;
const ALTO = 220;
const MARGEN = { top: 18, right: 52, bottom: 28, left: 44 };

export function ProgressChart({ intentos }: Props) {
  const [activo, setActivo] = useState<number | null>(null);
  const idGradiente = useId();

  // La lista viene del más reciente al más antiguo; el eje temporal necesita
  // el orden inverso.
  const serie = [...intentos].reverse();
  if (serie.length < 2) return null;

  const puntajes = serie.map((i) => i.estimated_score ?? 0);
  const min = Math.min(...puntajes);
  const max = Math.max(...puntajes);

  // Dominio con holgura para que la línea no quede pegada a los bordes,
  // acotado a la escala real de la PAES (100 a 1000).
  const holgura = Math.max(40, (max - min) * 0.25);
  const yMin = Math.max(100, Math.floor((min - holgura) / 50) * 50);
  const yMax = Math.min(1000, Math.ceil((max + holgura) / 50) * 50);
  const rango = yMax - yMin || 1;

  const anchoUtil = ANCHO - MARGEN.left - MARGEN.right;
  const altoUtil = ALTO - MARGEN.top - MARGEN.bottom;

  const x = (i: number) => MARGEN.left + (i / (serie.length - 1)) * anchoUtil;
  const y = (valor: number) =>
    MARGEN.top + altoUtil - ((valor - yMin) / rango) * altoUtil;

  const puntos = serie.map((intento, i) => ({
    intento,
    cx: x(i),
    cy: y(intento.estimated_score ?? 0),
  }));

  const linea = puntos.map((p, i) => `${i === 0 ? "M" : "L"}${p.cx},${p.cy}`).join(" ");
  const area = `${linea} L${puntos[puntos.length - 1].cx},${MARGEN.top + altoUtil} L${puntos[0].cx},${MARGEN.top + altoUtil} Z`;

  const marcasY = [yMin, Math.round((yMin + yMax) / 2), yMax];
  const ultimo = puntos[puntos.length - 1];
  const activoPunto = activo !== null ? puntos[activo] : null;

  return (
    <figure className="viz-root m-0">
      <figcaption className="mb-1 text-sm font-semibold">
        Evolución de tu puntaje estimado
      </figcaption>
      <p className="mb-3 text-xs text-muted">
        {serie.length} ensayos, del más antiguo al más reciente
      </p>

      <div className="relative">
        <svg
          viewBox={`0 0 ${ANCHO} ${ALTO}`}
          className="w-full"
          role="img"
          aria-label={`Gráfico de línea con la evolución del puntaje en ${serie.length} ensayos. Puntaje inicial ${puntajes[0]}, puntaje más reciente ${puntajes[puntajes.length - 1]}.`}
          onMouseLeave={() => setActivo(null)}
        >
          <defs>
            <linearGradient id={idGradiente} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" className="[stop-color:var(--serie)] [stop-opacity:0.18]" />
              <stop offset="100%" className="[stop-color:var(--serie)] [stop-opacity:0]" />
            </linearGradient>
          </defs>

          {/* Grilla horizontal, deliberadamente tenue */}
          {marcasY.map((valor) => (
            <g key={valor}>
              <line
                x1={MARGEN.left}
                x2={ANCHO - MARGEN.right}
                y1={y(valor)}
                y2={y(valor)}
                className="stroke-[var(--grilla)]"
                strokeWidth={1}
              />
              <text
                x={MARGEN.left - 8}
                y={y(valor)}
                textAnchor="end"
                dominantBaseline="middle"
                className="fill-[var(--tenue)] text-[11px] tabular-nums"
              >
                {valor}
              </text>
            </g>
          ))}

          <path d={area} fill={`url(#${idGradiente})`} />

          <path
            d={linea}
            fill="none"
            className="stroke-[var(--serie)]"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* Anillo del color de la superficie para separar los puntos de la línea */}
          {puntos.map((p, i) => (
            <circle
              key={p.intento.attempt_id}
              cx={p.cx}
              cy={p.cy}
              r={activo === i ? 5.5 : 4}
              className="fill-[var(--serie)] stroke-[var(--superficie)]"
              strokeWidth={2}
            />
          ))}

          <text
            x={ultimo.cx + 10}
            y={ultimo.cy}
            dominantBaseline="middle"
            className="fill-[var(--texto)] text-[12px] font-semibold tabular-nums"
          >
            {ultimo.intento.estimated_score}
          </text>

          {/* Zonas de detección más anchas que los puntos, para facilitar el hover */}
          {puntos.map((p, i) => (
            <rect
              key={`hit-${p.intento.attempt_id}`}
              x={p.cx - anchoUtil / (serie.length - 1) / 2}
              y={MARGEN.top}
              width={anchoUtil / (serie.length - 1)}
              height={altoUtil}
              fill="transparent"
              onMouseEnter={() => setActivo(i)}
              onFocus={() => setActivo(i)}
              tabIndex={0}
              role="button"
              aria-label={`Ensayo ${i + 1}: ${p.intento.estimated_score} puntos`}
              className="cursor-pointer outline-none"
            />
          ))}

          {activoPunto && (
            <line
              x1={activoPunto.cx}
              x2={activoPunto.cx}
              y1={MARGEN.top}
              y2={MARGEN.top + altoUtil}
              className="stroke-[var(--grilla)]"
              strokeWidth={1}
            />
          )}
        </svg>

        {/* Tooltip en HTML: hereda tipografía y es más fácil de posicionar que en SVG */}
        {activoPunto && (
          <div
            className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs whitespace-nowrap shadow-sm"
            style={{
              left: `${(activoPunto.cx / ANCHO) * 100}%`,
              top: `${(activoPunto.cy / ALTO) * 100}%`,
            }}
          >
            <span className="font-semibold tabular-nums">
              {activoPunto.intento.estimated_score} pts
            </span>
            <span className="ml-1.5 text-muted">
              {activoPunto.intento.correct}/{activoPunto.intento.total_questions} correctas
            </span>
          </div>
        )}
      </div>
    </figure>
  );
}
