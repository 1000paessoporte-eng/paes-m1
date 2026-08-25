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
  /** Ancho de ventana desde el que el panel cabe en el margen sin tapar el
   *  contenido. Depende de cuánto ocupa el ensayo: con texto base al lado de
   *  las preguntas el contenido es mucho más ancho y el margen se agota. */
  abrirDesde?: number;
}

export function QuestionNavigator({
  items,
  currentIndex,
  onSelect,
  abrirDesde = 1280,
}: Props) {
  const [open, setOpen] = useState(false);

  // Parte abierto solo desde el ancho en que el panel cabe en el margen sin
  // taparle el enunciado a la columna de preguntas. Bajo ese ancho parte
  // plegado como pastilla.
  useEffect(() => {
    // Lectura de estado externo (tamaño de ventana) al montar.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setOpen(window.matchMedia(`(min-width: ${abrirDesde}px)`).matches);
  }, [abrirDesde]);

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
                // El panel es el cartón de respuestas del ensayo: cada
                // pregunta es una burbuja, rellena de grafito si ya se
                // respondió. De un vistazo se lee igual que un cartón a medio
                // llenar, que es exactamente lo que es.
                className={cn(
                  "relative flex aspect-square items-center justify-center rounded-full text-[10px] font-semibold tabular-nums transition",
                  item.answered
                    ? "burbuja burbuja-marcada text-on-fill"
                    : "burbuja text-muted hover:bg-surface-hover hover:text-foreground",
                  // La pregunta en pantalla se marca con un anillo alrededor y
                  // no cambiando el relleno: el relleno ya significa otra cosa.
                  actual && "ring-2 ring-accent ring-offset-1 ring-offset-background"
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

      <p className="flex items-center gap-1.5 border-t border-border px-3 py-1.5 text-[10px] leading-tight text-muted">
        <span
          aria-hidden
          className="burbuja burbuja-marcada inline-block h-2.5 w-2.5 rounded-full"
        />
        respondida ·<span className="text-warning">●</span> marcada
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
