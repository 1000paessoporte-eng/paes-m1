"use client";

import { useState } from "react";
import { formatFullDate, formatShortDate, niceMax, roundedTopBarPath } from "./chart-utils";

const COLOR = "#3987e5"; // azul; contraste ≥3:1 sobre el fondo blanco de la app

interface Point {
  date: string;
  minutes: number;
}

const WIDTH = 600;
const HEIGHT = 220;
const PAD = { top: 12, right: 8, bottom: 24, left: 8 };

export function TimeInvestedChart({ data }: { data: Point[] }) {
  const [hover, setHover] = useState<number | null>(null);
  const [showTable, setShowTable] = useState(false);

  const plotW = WIDTH - PAD.left - PAD.right;
  const plotH = HEIGHT - PAD.top - PAD.bottom;
  const max = niceMax(Math.max(...data.map((d) => d.minutes), 1));
  const band = plotW / data.length;
  const barW = Math.min(24, band * 0.55);

  const gridSteps = [0, 0.25, 0.5, 0.75, 1];

  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-foreground">Tiempo invertido</h3>
          <p className="text-xs text-muted">Minutos de práctica por día · últimos 14 días</p>
        </div>
        <button
          onClick={() => setShowTable((v) => !v)}
          className="text-xs text-muted underline-offset-2 hover:text-foreground hover:underline"
        >
          {showTable ? "Ver gráfico" : "Ver tabla"}
        </button>
      </div>

      {showTable ? (
        <table className="mt-4 w-full text-left text-xs">
          <thead>
            <tr className="text-muted">
              <th className="py-1 font-normal">Día</th>
              <th className="py-1 font-normal">Minutos</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.date} className="border-t border-border">
                <td className="py-1.5 text-foreground">{formatFullDate(d.date)}</td>
                <td className="py-1.5 tabular-nums text-foreground">{d.minutes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="relative mt-2">
          <svg
            viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
            className="w-full overflow-visible"
            role="img"
            aria-label="Minutos de práctica por día"
          >
            {gridSteps.map((s) => {
              const y = PAD.top + plotH * (1 - s);
              return (
                <line
                  key={s}
                  x1={PAD.left}
                  x2={WIDTH - PAD.right}
                  y1={y}
                  y2={y}
                  stroke="var(--border)"
                  strokeWidth={1}
                />
              );
            })}

            {data.map((d, i) => {
              const x = PAD.left + i * band + (band - barW) / 2;
              const h = max > 0 ? (d.minutes / max) * plotH : 0;
              const y = PAD.top + (plotH - h);
              const isHover = hover === i;
              return (
                <g key={d.date}>
                  <rect
                    x={PAD.left + i * band}
                    y={PAD.top}
                    width={band}
                    height={plotH}
                    fill="transparent"
                    onMouseEnter={() => setHover(i)}
                    onMouseLeave={() => setHover((h2) => (h2 === i ? null : h2))}
                  />
                  <path
                    d={
                      h > 0
                        ? roundedTopBarPath(x, y, barW, h, 4)
                        : `M${x},${PAD.top + plotH - 1} h${barW} v1 h${-barW} Z`
                    }
                    fill={COLOR}
                    opacity={isHover ? 1 : 0.85}
                  />
                  {i % 2 === 0 && (
                    <text
                      x={PAD.left + i * band + band / 2}
                      y={HEIGHT - 6}
                      textAnchor="middle"
                      fontSize={9}
                      fill="var(--muted)"
                    >
                      {formatShortDate(d.date)}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>

          {hover != null && (
            <div
              className="pointer-events-none absolute -translate-x-1/2 -translate-y-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs shadow-lg"
              style={{
                left: `${((PAD.left + hover * band + band / 2) / WIDTH) * 100}%`,
                top: `${(PAD.top / HEIGHT) * 100}%`,
              }}
            >
              <p className="font-medium text-foreground">{data[hover].minutes} min</p>
              <p className="text-muted">{formatFullDate(data[hover].date)}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
