"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@paes-m1/utils";
import type { ExamAttemptSummary, Subject } from "@/lib/api";
import { COLOR_PRUEBA, NOMBRE_CORTO } from "@/lib/colores-prueba";

/**
 * Evolución del puntaje, una prueba a la vez.
 *
 * Antes era UNA línea con todos los ensayos mezclados. Eso no era una
 * evolución: un 823 de Lectora seguido de un 260 de M1 dibujaba una caída que
 * no le pasó a nadie. Cada prueba tiene su propio temario y su propia tabla de
 * transformación del DEMRE, así que sus puntajes no se comparan entre sí --
 * solo consigo mismos a lo largo del tiempo.
 *
 * **Una sola serie a la vez, y no cinco superpuestas.** Los colores de prueba
 * son de identidad y funcionan como chips, pero como cinco líneas de 2px
 * fallan: entre M1 (#1d4ed8) y M2 (#7e22ce) hay ΔE 14,7 en visión normal --
 * bajo el mínimo de 15-- y 2,0 en deuteranopía. Son justo las dos pruebas más
 * parecidas y las más fáciles de confundir. Medido, no supuesto. Aislada, cada
 * prueba pasa contraste de sobra contra la superficie y conserva su color.
 *
 * Los ejes y la grilla van en tonos recesivos para que la línea sea lo único
 * prominente, y solo el último punto lleva etiqueta directa: rotular todos
 * satura el gráfico sin agregar información.
 */

interface Props {
  /** Intentos del más reciente al más antiguo, como los entrega la API. */
  intentos: ExamAttemptSummary[];
}

const ANCHO_BASE = 640;
const ALTO = 220;
const MARGEN = { top: 18, right: 52, bottom: 28, left: 44 };

/** Orden de las pruebas: el del temario, no el de cuántos ensayos hay. */
const ORDEN: Subject[] = ["lectora", "m1", "m2", "ciencias", "historia"];

export function ProgressChart({ intentos }: Props) {
  const quieto = useReducedMotion();
  const [activo, setActivo] = useState<number | null>(null);
  const idGradiente = useId();

  // Un ensayo sin puntaje estimado no tiene dónde ubicarse en el eje: se queda
  // fuera de la serie, no en cero.
  const porPrueba = useMemo(() => {
    const mapa = new Map<Subject, ExamAttemptSummary[]>();
    for (const intento of intentos) {
      if (intento.estimated_score == null) continue;
      mapa.set(intento.subject, [...(mapa.get(intento.subject) ?? []), intento]);
    }
    // La API entrega el más reciente primero; el eje temporal necesita el
    // orden en que los vivió el alumno.
    for (const [prueba, lista] of mapa) {
      mapa.set(
        prueba,
        [...lista].sort(
          (a, b) => new Date(a.started_at).getTime() - new Date(b.started_at).getTime()
        )
      );
    }
    return mapa;
  }, [intentos]);

  const disponibles = ORDEN.filter((p) => (porPrueba.get(p)?.length ?? 0) > 0);

  // Arranca en la prueba donde hay más que ver. Abrir en una con un solo
  // ensayo mostraría el estado vacío teniendo trece puntos al lado.
  const [prueba, setPrueba] = useState<Subject | null>(null);
  const elegida =
    prueba && disponibles.includes(prueba)
      ? prueba
      : [...disponibles].sort(
          (a, b) => (porPrueba.get(b)?.length ?? 0) - (porPrueba.get(a)?.length ?? 0)
        )[0];

  if (!elegida) return null;

  const serie = porPrueba.get(elegida) ?? [];

  return (
    <figure
      className="viz-root m-0"
      style={{ "--serie": COLOR_PRUEBA[elegida] } as React.CSSProperties}
    >
      <figcaption className="mb-1 text-sm font-semibold">
        Evolución de tu puntaje en {NOMBRE_CORTO[elegida]}
      </figcaption>
      <p className="mb-3 text-xs text-muted">
        Cada prueba se mide con su propia tabla del DEMRE, así que los puntajes
        solo se comparan dentro de una misma prueba.
      </p>

      {/* El filtro va sobre el gráfico y en una sola fila. Lleva la cuenta de
          ensayos porque es la que decide si hay algo que mirar. */}
      {disponibles.length > 1 && (
        <div
          role="tablist"
          aria-label="Elige la prueba"
          className="mb-4 flex flex-wrap gap-1.5"
        >
          {disponibles.map((p) => {
            const activa = p === elegida;
            return (
              <button
                key={p}
                role="tab"
                aria-selected={activa}
                onClick={() => {
                  setPrueba(p);
                  setActivo(null);
                }}
                style={{ "--color-prueba": COLOR_PRUEBA[p] } as React.CSSProperties}
                className={cn(
                  "flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs transition-colors",
                  activa
                    ? "border-[var(--color-prueba)] bg-[var(--color-prueba)]/10 font-medium text-foreground"
                    : "border-border text-muted hover:bg-surface-hover hover:text-foreground"
                )}
              >
                {/* El punto de color acompaña al nombre: la identidad nunca
                    queda solo en el color. */}
                <span
                  aria-hidden
                  className="h-2 w-2 shrink-0 rounded-full bg-[var(--color-prueba)]"
                />
                {NOMBRE_CORTO[p]}
                <span className="text-muted tabular-nums">
                  {porPrueba.get(p)?.length}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {serie.length < 2 ? (
        <p className="rounded-lg border border-border bg-surface-hover px-4 py-6 text-center text-sm text-muted">
          Llevas un ensayo de {NOMBRE_CORTO[elegida]}
          {serie[0]?.estimated_score != null && (
            <>
              , con <strong className="text-foreground">{serie[0].estimated_score} puntos</strong>
            </>
          )}
          . Rinde uno más y acá vas a ver si subiste.
        </p>
      ) : (
        <Grafico
          serie={serie}
          activo={activo}
          setActivo={setActivo}
          idGradiente={idGradiente}
          quieto={quieto}
          prueba={elegida}
        />
      )}
    </figure>
  );
}

function Grafico({
  serie,
  activo,
  setActivo,
  idGradiente,
  quieto,
  prueba,
}: {
  serie: ExamAttemptSummary[];
  activo: number | null;
  setActivo: (i: number | null) => void;
  idGradiente: string;
  quieto: boolean | null;
  prueba: Subject;
}) {
  // El viewBox se ajusta al ancho REAL del contenedor para que la escala sea
  // 1:1. Con un viewBox fijo de 640 el SVG se encogía a 308px en un celular y
  // arrastraba el texto con él: las etiquetas de los ejes quedaban en 5,3px
  // efectivos, ilegibles. Medido, no estimado.
  const contenedor = useRef<HTMLDivElement>(null);
  const [ancho, setAncho] = useState(ANCHO_BASE);
  useEffect(() => {
    const nodo = contenedor.current;
    if (!nodo) return;
    const observador = new ResizeObserver(([entrada]) => {
      const medido = entrada.contentRect.width;
      if (medido > 0) setAncho(medido);
    });
    observador.observe(nodo);
    return () => observador.disconnect();
  }, []);

  const puntajes = serie.map((i) => i.estimated_score ?? 0);
  const min = Math.min(...puntajes);
  const max = Math.max(...puntajes);

  // Dominio con holgura para que la línea no quede pegada a los bordes,
  // acotado a la escala real de la PAES (100 a 1000).
  const holgura = Math.max(40, (max - min) * 0.25);
  const yMin = Math.max(100, Math.floor((min - holgura) / 50) * 50);
  const yMax = Math.min(1000, Math.ceil((max + holgura) / 50) * 50);
  const rango = yMax - yMin || 1;

  const anchoUtil = Math.max(80, ancho - MARGEN.left - MARGEN.right);
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
  const anchoZona = anchoUtil / (serie.length - 1);

  return (
    <>
      <p className="mb-3 text-xs text-muted">
        {serie.length} ensayos de {NOMBRE_CORTO[prueba]}, del más antiguo al más
        reciente
      </p>

      <div ref={contenedor} className="relative">
        <svg
          viewBox={`0 0 ${ancho} ${ALTO}`}
          className="w-full"
          role="img"
          aria-label={`Gráfico de línea con la evolución del puntaje en ${serie.length} ensayos de ${NOMBRE_CORTO[prueba]}. Puntaje inicial ${puntajes[0]}, puntaje más reciente ${puntajes[puntajes.length - 1]}.`}
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
                x2={ancho - MARGEN.right}
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

          <motion.path
            d={area}
            fill={`url(#${idGradiente})`}
            initial={quieto ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          />

          {/* La línea se DIBUJA de izquierda a derecha, que es la dirección
              del tiempo. Es tu historia de puntajes: verla trazarse dice
              "esto pasó, en este orden" mejor que aparecer completa.
              La clave la reinicia al cambiar de prueba, para que el trazo
              vuelva a contar la historia de la prueba nueva. */}
          <motion.path
            key={prueba}
            d={linea}
            fill="none"
            className="stroke-[var(--serie)]"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
            initial={quieto ? false : { pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
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
              x={p.cx - anchoZona / 2}
              y={MARGEN.top}
              width={anchoZona}
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
              left: `${(activoPunto.cx / ancho) * 100}%`,
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
    </>
  );
}
