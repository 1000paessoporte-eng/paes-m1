"use client";

import { useEffect, useState } from "react";
import { cn } from "@paes-m1/utils";

/**
 * Navegador flotante de preguntas.
 *
 * Va anclado al costado derecho como una ventana pequeña que se puede plegar:
 * durante el ensayo lo importante es la pregunta, así que la cuadrícula no
 * debe robarle ancho al enunciado. Plegado queda como una pastilla con el
 * avance, que sigue siendo un atajo de un toque para volver a abrirlo.
 */

export interface NavigatorItem {
  id: number;
  answered: boolean;
  flagged: boolean;
}

interface Props {
  items: NavigatorItem[];
  currentIndex: number;
  onSelect: (index: number) => void;
}

export function QuestionNavigator({ items, currentIndex, onSelect }: Props) {
  const [open, setOpen] = useState(false);

  // Parte abierto solo desde 1280px, que es el ancho a partir del cual el
  // panel cabe en el margen sin taparle el enunciado a la columna central
  // (max-w-3xl). Bajo ese ancho parte plegado como pastilla.
  useEffect(() => {
    // Lectura de estado externo (tamaño de ventana) al montar.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setOpen(window.matchMedia("(min-width: 1280px)").matches);
  }, []);

  const respondidas = items.filter((i) => i.answered).length;

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-expanded={false}
        className="fixed right-3 bottom-3 z-30 flex items-center gap-2 rounded-full border border-border bg-background/95 px-3 py-2 text-xs font-medium shadow-lg backdrop-blur transition hover:bg-surface-hover sm:right-6 sm:bottom-4"
      >
        <GridIcon />
        <span className="tabular-nums">
          {respondidas}/{items.length}
        </span>
      </button>
    );
  }

  return (
    <aside
      aria-label="Navegador de preguntas"
      className="fixed right-3 bottom-3 z-30 w-[13.5rem] rounded-xl border border-border bg-background/95 shadow-lg backdrop-blur sm:right-6 sm:bottom-4 xl:top-24 xl:bottom-auto"
    >
      <div className="flex items-center justify-between gap-2 border-b border-border px-3 py-2">
        <span className="text-xs font-semibold">
          Preguntas{" "}
          <span className="font-normal text-muted tabular-nums">
            {respondidas}/{items.length}
          </span>
        </span>
        <button
          type="button"
          onClick={() => setOpen(false)}
          aria-label="Plegar el navegador"
          className="rounded p-0.5 text-muted transition hover:bg-surface-hover hover:text-foreground"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <div className="max-h-[45vh] overflow-y-auto p-2 lg:max-h-[52vh]">
        <div className="grid grid-cols-6 gap-1">
          {items.map((item, i) => {
            const actual = i === currentIndex;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelect(i)}
                aria-current={actual ? "true" : undefined}
                aria-label={`Pregunta ${i + 1}${
                  item.answered ? ", respondida" : ", sin responder"
                }${item.flagged ? ", marcada para revisar" : ""}`}
                className={cn(
                  "relative flex aspect-square items-center justify-center rounded border text-[10px] font-semibold tabular-nums transition",
                  actual
                    ? "border-accent bg-accent text-accent-foreground"
                    : item.answered
                      ? "border-success/50 bg-success/15 text-success hover:bg-success/25"
                      : "border-border bg-surface text-muted hover:bg-surface-hover hover:text-foreground"
                )}
              >
                {i + 1}
                {item.flagged && (
                  <span
                    aria-hidden
                    className="absolute -top-px -right-px h-1.5 w-1.5 rounded-full bg-warning"
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>

      <p className="border-t border-border px-3 py-1.5 text-[10px] leading-tight text-muted">
        <span className="text-success">■</span> respondida ·{" "}
        <span className="text-warning">●</span> marcada
      </p>
    </aside>
  );
}

function GridIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  );
}
