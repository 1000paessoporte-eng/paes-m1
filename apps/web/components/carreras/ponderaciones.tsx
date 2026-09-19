import { cn } from "@paes-m1/utils";

/**
 * La lista de cuánto pesa cada factor en una carrera, como chips.
 *
 * Responde "cuánto vale cada materia" de un vistazo, sin abrir la ficha. Se
 * usa en cada resultado del buscador y podría reutilizarse en la ficha.
 *
 * Solo muestra los factores con peso > 0: una carrera que no pondera M2 no
 * gana nada con un "M2 0%". El orden es fijo —el mismo en todas— para que dos
 * carreras se comparen leyendo en la misma posición, no cazando la etiqueta.
 */

/** Lo que aporta cada factor, con la etiqueta corta con que se muestra. El
 *  orden de este arreglo es el orden en pantalla. */
const FACTORES = [
  ["nem", "NEM"],
  ["ranking", "Ranking"],
  ["lectora", "Lectora"],
  ["m1", "M1"],
  ["m2", "M2"],
  ["historia", "Historia"],
  ["ciencias", "Ciencias"],
  ["prueba_especial", "P. especial"],
] as const;

type ConPesos = {
  [K in (typeof FACTORES)[number][0]]?: number | null;
} & { electivo_alternativo?: boolean };

export function Ponderaciones({
  carrera,
  className,
}: {
  carrera: ConPesos;
  className?: string;
}) {
  const conPeso = FACTORES.filter(([campo]) => (carrera[campo] ?? 0) > 0);
  if (conPeso.length === 0) return null;

  return (
    <div className={cn("flex flex-wrap gap-1", className)}>
      {conPeso.map(([campo, etiqueta]) => (
        <span
          key={campo}
          className="inline-flex items-center gap-1 rounded-md bg-surface-hover px-1.5 py-0.5 text-[11px] text-muted"
        >
          {etiqueta}
          <strong className="font-semibold text-foreground tabular-nums">
            {carrera[campo]}%
          </strong>
        </span>
      ))}
      {carrera.electivo_alternativo && (
        <span className="inline-flex items-center rounded-md bg-surface-hover px-1.5 py-0.5 text-[11px] text-muted">
          Historia o Ciencias
        </span>
      )}
    </div>
  );
}
