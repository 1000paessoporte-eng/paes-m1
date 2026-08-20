import Link from "next/link";
import type { Diagnostico } from "@/lib/api";

/**
 * Los errores de razonamiento en que el alumno cae repetidamente.
 *
 * Toda plataforma de ensayos dice CUÁL era la alternativa correcta. Ninguna
 * dice por qué la cabeza del estudiante fue hacia la otra. Ese texto --el
 * error conceptual exacto que induce a cada distractor-- está escrito para las
 * 5.586 alternativas incorrectas del banco desde el primer día, y no se
 * mostraba en ninguna pantalla.
 *
 * Lo que lo vuelve útil no es enseñarlo pregunta por pregunta, sino AGRUPADO:
 * "cuatro veces sumaste los exponentes en vez de multiplicarlos" es accionable
 * de una forma en que "fallaste 4 de Números" no lo es. Uno manda a estudiar
 * un eje entero; el otro apunta a la regla que hay que arreglar.
 */
export function DiagnosticoErrores({ errores }: { errores: Diagnostico["errores"] }) {
  if (errores.length === 0) return null;

  return (
    <section className="mt-6">
      <h2 className="mb-1 text-sm font-semibold tracking-wide text-muted uppercase">
        En qué te estás equivocando
      </h2>
      <p className="mb-3 text-xs leading-relaxed text-muted">
        No es el tema, es el razonamiento exacto que te llevó a la alternativa
        equivocada. Lo que más se repite, primero.
      </p>

      <ul className="flex flex-col gap-2">
        {errores.map((e) => (
          <li
            key={e.descripcion}
            className="rounded-xl border border-border bg-surface p-4"
          >
            {/* El enunciado va PRIMERO y en gris: el texto del error está
                escrito asumiendo que se ve la pregunta, y suelto se lee al
                revés en las del tipo "¿cuál NO representa...?". */}
            <p className="mb-2 line-clamp-2 text-xs leading-relaxed text-muted">
              {e.pregunta}
            </p>
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm leading-relaxed text-foreground">{e.descripcion}</p>
              {/* La insignia solo si se repitió: poner "1 vez" en todas es
                  ruido, y además le quita fuerza a las que sí son un patrón. */}
              {e.veces > 1 && (
                <span className="shrink-0 rounded-full bg-accent-warm/10 px-2.5 py-0.5 text-xs font-semibold text-accent-warm-strong tabular-nums">
                  {e.veces} veces
                </span>
              )}
            </div>
            <p className="mt-2 text-xs text-muted">
              {e.axis_label} · {e.node_name} ·{" "}
              <Link
                href={`/aprender/${e.node_code}`}
                className="font-medium text-accent underline-offset-4 hover:underline"
              >
                Repasar este tema →
              </Link>
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
