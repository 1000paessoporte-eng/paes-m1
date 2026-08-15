"use client";

import { useSyncExternalStore } from "react";

/**
 * Selector de tema: claro, automático u oscuro.
 *
 * Son tres estados y no dos a propósito. "Automático" es el que sirve al
 * estudiante que estudia de día y de noche: el teléfono ya cambia solo a las
 * ocho de la tarde y la página lo sigue sin que tenga que hacer nada. Los
 * otros dos existen para quien quiere mandar por sobre eso.
 *
 * Lo que se guarda es la *elección*, no el color resultante: si eligió
 * "automático" no se guarda nada, y así el día que cambie la configuración de
 * su teléfono la página cambia con él.
 *
 * El tema ya fue aplicado por el script del layout antes de pintar; este
 * componente solo lo cambia y refleja el estado.
 */

type Tema = "system" | "light" | "dark";

const OPCIONES: { valor: Tema; etiqueta: string; icono: string }[] = [
  { valor: "light", etiqueta: "Claro", icono: "☀" },
  { valor: "system", etiqueta: "Automático", icono: "◐" },
  { valor: "dark", etiqueta: "Oscuro", icono: "☾" },
];

// `localStorage` es estado que vive fuera de React. Leerlo con un efecto y
// guardarlo en useState provoca un render extra en cada montaje; con
// useSyncExternalStore React lo lee donde corresponde y sabe que en el
// servidor no existe.
const oyentes = new Set<() => void>();

function suscribir(cb: () => void) {
  oyentes.add(cb);
  // `storage` avisa de cambios hechos en OTRA pestaña: si el estudiante tiene
  // dos abiertas, ambas quedan con el mismo tema.
  window.addEventListener("storage", cb);
  return () => {
    oyentes.delete(cb);
    window.removeEventListener("storage", cb);
  };
}

function leer(): Tema {
  const v = localStorage.getItem("tema");
  return v === "dark" || v === "light" ? v : "system";
}

/** En el servidor no hay elección guardada; el script del layout ya se encargó. */
function leerEnServidor(): Tema {
  return "system";
}

function aplicar(tema: Tema) {
  const raiz = document.documentElement;
  if (tema === "system") {
    raiz.removeAttribute("data-theme");
    localStorage.removeItem("tema");
  } else {
    raiz.setAttribute("data-theme", tema);
    localStorage.setItem("tema", tema);
  }
  oyentes.forEach((cb) => cb());
}

export function TemaToggle() {
  const tema = useSyncExternalStore(suscribir, leer, leerEnServidor);

  return (
    <div
      role="radiogroup"
      aria-label="Tema de la página"
      className="flex items-center gap-0.5 rounded-full border border-border bg-surface p-0.5"
    >
      {OPCIONES.map((o) => {
        const activo = tema === o.valor;
        return (
          <button
            key={o.valor}
            type="button"
            role="radio"
            aria-checked={activo}
            aria-label={o.etiqueta}
            title={o.etiqueta}
            onClick={() => aplicar(o.valor)}
            className={
              "flex h-7 w-7 items-center justify-center rounded-full text-xs transition-colors " +
              (activo
                ? "bg-accent text-accent-foreground"
                : "text-muted hover:bg-surface-hover hover:text-foreground")
            }
          >
            <span aria-hidden>{o.icono}</span>
          </button>
        );
      })}
    </div>
  );
}
