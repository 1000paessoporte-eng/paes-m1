"use client";

import { useState } from "react";
import { formatFullDate, formatShortDate } from "./chart-utils";

const COLOR = "#d95926"; // naranja, validado (dataviz skill) junto al azul del chart de tiempo

interface Point {
  date: string;
  accuracy: number | null; // 0..1, null = sin datos ese día
}

const WIDTH = 600;
const HEIGHT = 220;
const PAD = { top: 12, right: 8, bottom: 24, left: 30 };

export function AccuracyChart({ data }: { data: Point[] }) {
  const [hover, setHover] = useState<number | null>(null);
  const [showTable, setShowTable] = useState(false);

  const plotW = WIDTH - PAD.left - PAD.right;
  const plotH = HEIGHT - PAD.top - PAD.bottom;
  const band = data.length > 1 ? plotW / (data.length - 1) : plotW;

  const xAt = (i: number) => PAD.left + i * band;
  const yAt = (acc: number) => PAD.top + plotH * (1 - acc);

  // Segmentos contiguos con datos (no interpolar a través de días sin actividad).
  const segments: number[][] = [];
  let current: number[] = [];
  data.forEach((d, i) => {
    if (d.accuracy != null) {
      current.push(i);
    } else if (current.length) {
      segments.push(current);
      current = [];
    }
  });
  if (current.length) segments.push(current);

  const gridSteps = [0, 0.25, 0.5, 0.75, 1];

  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-foreground">Tasa de acierto</h3>
          <p className="text-xs text-muted">% de respuestas correctas por día · últimos 14 días</p>
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
              <th className="py-1 font-normal">Precisión</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.date} className="border-t border-border">
                <td className="py-1.5 text-foreground">{formatFullDate(d.date)}</td>
                <td className="py-1.5 tabular-nums text-foreground">
                  {d.accuracy != null ? `${Math.round(d.accuracy * 100)}%` : "—"}
                </td>
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
            aria-label="Tasa de acierto por día"
          >
            {gridSteps.map((s) => {
              const y = PAD.top + plotH * (1 - s);
              return (
                <g key={s}>
                  <line
                    x1={PAD.left}
                    x2={WIDTH - PAD.right}
                    y1={y}
                    y2={y}
                    stroke="var(--border)"
                    strokeWidth={1}
                  />
                  <text x={0} y={y + 3} fontSize={9} fill="var(--muted)">
                    {Math.round(s * 100)}%
                  </text>
                </g>
              );
            })}

            {segments.map((seg, si) => {
              const linePath = seg
                .map((i, k) => `${k === 0 ? "M" : "L"}${xAt(i)},${yAt(data[i].accuracy as number)}`)
                .join(" ");
              const areaPath =
                `${linePath} ` +
                `L${xAt(seg[seg.length - 1])},${PAD.top + plotH} ` +
                `L${xAt(seg[0])},${PAD.top + plotH} Z`;
              return (
                <g key={si}>
                  <path d={areaPath} fill={COLOR} opacity={0.1} stroke="none" />
                  <path
                    d={linePath}
                    fill="none"
                    stroke={COLOR}
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </g>
              );
            })}

            {hover != null && (
              <line
                x1={xAt(hover)}
                x2={xAt(hover)}
                y1={PAD.top}
                y2={PAD.top + plotH}
                stroke="var(--border-strong)"
                strokeWidth={1}
              />
            )}

            {data.map((d, i) => (
              <g key={d.date}>
                <rect
                  x={xAt(i) - band / 2}
                  y={PAD.top}
                  width={band}
                  height={plotH}
                  fill="transparent"
                  onMouseEnter={() => setHover(i)}
                  onMouseLeave={() => setHover((h) => (h === i ? null : h))}
                />
                {d.accuracy != null && (
                  <circle
                    cx={xAt(i)}
                    cy={yAt(d.accuracy)}
                    r={hover === i ? 5 : 4}
                    fill={COLOR}
                    stroke="var(--surface)"
                    strokeWidth={2}
                  />
                )}
                {i % 2 === 0 && (
                  <text
                    x={xAt(i)}
                    y={HEIGHT - 6}
                    textAnchor="middle"
                    fontSize={9}
                    fill="var(--muted)"
                  >
                    {formatShortDate(d.date)}
                  </text>
                )}
              </g>
            ))}
          </svg>

          {hover != null && (
            <div
              className="pointer-events-none absolute -translate-x-1/2 -translate-y-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs shadow-lg"
              style={{
                left: `${(xAt(hover) / WIDTH) * 100}%`,
                top: `${(PAD.top / HEIGHT) * 100}%`,
              }}
            >
              <p className="font-medium text-foreground">
                {data[hover].accuracy != null
                  ? `${Math.round((data[hover].accuracy as number) * 100)}%`
                  : "Sin actividad"}
              </p>
              <p className="text-muted">{formatFullDate(data[hover].date)}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
