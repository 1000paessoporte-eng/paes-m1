import { formatShortDate, niceMax, roundedTopBarPath } from "@/components/analytics/chart-utils";

interface Props {
  titulo: string;
  descripcion: string;
  datos: { dia: string; valor: number }[];
}

const ALTO = 120;
const ANCHO = 620;
const PADDING_INF = 18;

/**
 * Barras diarias de los últimos 30 días. Mismo lenguaje visual que los
 * gráficos de Analítica, pero sin interacción: acá el detalle exacto no
 * aporta, importa la forma de la curva.
 */
export function SerieChart({ titulo, descripcion, datos }: Props) {
  const total = datos.reduce((acc, d) => acc + d.valor, 0);
  const maximo = niceMax(Math.max(...datos.map((d) => d.valor), 0));
  const anchoBarra = ANCHO / Math.max(datos.length, 1);

  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <div className="flex items-baseline justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold">{titulo}</h3>
          <p className="mt-0.5 text-xs text-muted">{descripcion}</p>
        </div>
        <p className="shrink-0 text-2xl font-semibold tracking-tight">{total}</p>
      </div>

      {total === 0 ? (
        <p className="mt-6 mb-2 text-center text-xs text-muted">
          Sin actividad en los últimos 30 días.
        </p>
      ) : (
        <svg
          viewBox={`0 0 ${ANCHO} ${ALTO}`}
          className="mt-4 w-full"
          role="img"
          aria-label={`${titulo}: ${total} en 30 días`}
        >
          {datos.map((d, i) => {
            const alturaUtil = ALTO - PADDING_INF;
            const alto = maximo > 0 ? (d.valor / maximo) * alturaUtil : 0;
            const x = i * anchoBarra + anchoBarra * 0.15;
            const ancho = anchoBarra * 0.7;
            return (
              <path
                key={d.dia}
                d={roundedTopBarPath(x, alturaUtil - alto, ancho, alto, 2)}
                className="fill-accent/70"
              />
            );
          })}
          <line
            x1="0"
            y1={ALTO - PADDING_INF}
            x2={ANCHO}
            y2={ALTO - PADDING_INF}
            className="stroke-border"
            strokeWidth="1"
          />
          <text x="0" y={ALTO - 4} className="fill-muted" fontSize="10">
            {formatShortDate(datos[0].dia)}
          </text>
          <text
            x={ANCHO}
            y={ALTO - 4}
            textAnchor="end"
            className="fill-muted"
            fontSize="10"
          >
            {formatShortDate(datos[datos.length - 1].dia)}
          </text>
        </svg>
      )}
    </div>
  );
}
