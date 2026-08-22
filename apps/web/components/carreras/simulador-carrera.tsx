"use client";

import { useMemo, useState } from "react";
import type { CarreraPublica } from "@/lib/api";
import { calcularPonderado, factoresDe, type Factor, type Puntajes } from "@/lib/ponderado";

/**
 * "¿Me alcanza?" respondido sin cuenta y sin esperar.
 *
 * Corre entero en el navegador: el ponderado es una suma de pesos por puntajes
 * y las ponderaciones ya vinieron con la página, así que no hay ida y vuelta al
 * servidor por cada tecla. La fórmula vive en lib/ponderado.ts, fuera de este
 * archivo, porque este lleva "use client" y esa lógica tiene que poder probarse
 * sin React.
 *
 * Es el gancho de la página: alguien que llegó desde Google buscando un puntaje
 * obtiene su respuesta antes de que le pidamos nada.
 */
export function SimuladorCarrera({ carrera }: { carrera: CarreraPublica }) {
  const factores = useMemo(() => factoresDe(carrera), [carrera]);
  const [puntajes, setPuntajes] = useState<Puntajes>({});

  const ponderado = calcularPonderado(carrera, puntajes);
  const minimo = carrera.ponderado_min;
  const alcanza = ponderado != null && minimo != null ? ponderado >= minimo : null;
  const faltan =
    ponderado != null && minimo != null && ponderado < minimo
      ? Math.round((minimo - ponderado) * 10) / 10
      : null;

  return (
    <div className="rounded-xl border border-border bg-surface p-6">
      <h2 className="text-xl font-semibold">Simula tu puntaje ponderado</h2>
      <p className="mt-1 text-sm text-muted">
        Escribe los puntajes que tienes o que crees que puedes sacar. El cálculo es el
        oficial y no se guarda nada.
      </p>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        {factores.map(({ factor, etiqueta }) => (
          <CampoPuntaje
            key={factor}
            id={factor}
            etiqueta={etiqueta}
            valor={puntajes[factor] ?? null}
            onChange={(v) => setPuntajes((p) => ({ ...p, [factor]: v }))}
          />
        ))}
      </div>

      {carrera.electivo_alternativo && (
        <p className="mt-3 text-xs text-muted">
          Solo cuenta la mejor entre Historia y Ciencias: basta con que llenes una.
        </p>
      )}

      <div className="mt-6 border-t border-border pt-5">
        {ponderado == null ? (
          <p className="text-sm text-muted">
            Completa los puntajes de arriba para ver tu ponderado. Dejamos el resultado en
            blanco a propósito mientras falte alguno: un ponderado a medias es un número
            creíble y equivocado.
          </p>
        ) : (
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs font-medium text-muted uppercase">
                Tu ponderado
              </p>
              {/* Figuras proporcionales, no tabulares: es una cifra hero, no
                  una columna que se compare fila a fila. */}
              <p className="mt-1 text-5xl font-bold text-accent">{ponderado}</p>
            </div>

            {minimo != null && (
              <div className="text-right">
                <p className="text-xs text-muted">
                  Mínimo de postulación: {minimo}
                </p>
                {alcanza ? (
                  <p className="mt-1 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                    Alcanzas el mínimo para postular
                  </p>
                ) : (
                  <p className="mt-1 text-sm font-semibold text-amber-600 dark:text-amber-400">
                    Te faltan {faltan} puntos
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {minimo == null && ponderado != null && (
          <p className="mt-3 text-sm text-muted">
            Esta carrera no publicó un ponderado mínimo, así que no podemos decirte si
            alcanzas. El número de arriba es tu ponderado con estas ponderaciones.
          </p>
        )}
      </div>
    </div>
  );
}

/** Un puntaje PAES: entero entre 100 y 1000, o vacío. */
function CampoPuntaje({
  id,
  etiqueta,
  valor,
  onChange,
}: {
  id: Factor;
  etiqueta: string;
  valor: number | null;
  onChange: (valor: number | null) => void;
}) {
  // NEM y ranking se expresan en la misma escala 100-1000 que las pruebas.
  return (
    <div>
      <label htmlFor={`puntaje-${id}`} className="text-sm font-medium">
        {etiqueta}
      </label>
      <input
        id={`puntaje-${id}`}
        type="number"
        inputMode="numeric"
        min={100}
        max={1000}
        placeholder="100 a 1000"
        value={valor ?? ""}
        onChange={(e) => {
          const bruto = e.target.value;
          if (bruto === "") return onChange(null);
          const n = Number(bruto);
          // Se acepta lo que escriba y se acota: un 5000 pegado por error no
          // debe producir un ponderado imposible que la persona se crea.
          onChange(Number.isFinite(n) ? Math.min(1000, Math.max(100, Math.round(n))) : null);
        }}
        className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm tabular-nums"
      />
    </div>
  );
}
