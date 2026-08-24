import { cn } from "@paes-m1/utils";
import { TextoRico } from "@/components/texto-rico";

/**
 * El desarrollo de una pregunta, después de rendirla.
 *
 * Antes era un rectángulo gris con el texto corrido dentro. El problema no
 * era el texto: 1.353 de las 2.445 explicaciones del banco ya vienen escritas
 * como una entrada y una secuencia de pasos numerados, y se pintaban todas
 * seguidas separadas por saltos de línea. La estructura estaba ahí y la
 * pantalla la tiraba a la basura.
 *
 * Acá se respeta esa forma: la idea que abre el ejercicio arriba, los pasos
 * como pasos —numerados, uno por fila, colgando de una guía vertical— y la
 * respuesta al cierre. Se puede seguir con el dedo, que es como se estudia
 * una resolución.
 *
 * Y antes de todo eso, si se falló, el error propio. `distractor_justification`
 * viajaba en la respuesta de la API desde siempre y esta pantalla no lo
 * mostraba: el alumno que pagó veía la misma resolución genérica que
 * cualquiera, sin que nadie le dijera qué le pasó por la cabeza.
 */
export function Resolucion({
  explicacion,
  respuestaCorrecta,
  errorPropio,
}: {
  explicacion: string | null | undefined;
  respuestaCorrecta?: string;
  /** El porqué de la alternativa que se marcó. Solo va si se falló. */
  errorPropio?: string | null;
}) {
  const bloques = partirEnBloques(explicacion ?? "");

  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-border bg-surface">
      {errorPropio && (
        <div className="border-b border-danger/20 bg-danger/5 px-4 py-3.5">
          <p className="text-[11px] font-semibold tracking-wide text-danger uppercase">
            Por qué te equivocaste
          </p>
          <p className="mt-1.5 text-sm leading-relaxed text-foreground">{errorPropio}</p>
        </div>
      )}

      <div className="px-4 py-4">
        <p className="text-[11px] font-semibold tracking-wide text-muted uppercase">
          Cómo se resuelve
        </p>

        {bloques.length === 0 ? (
          <p className="mt-2 text-sm text-muted">
            Esta pregunta todavía no tiene desarrollo escrito.
          </p>
        ) : (
          <div className="mt-3 space-y-4">
            {bloques.map((bloque, i) =>
              bloque.tipo === "pasos" ? (
                <ol key={i} className="space-y-0">
                  {bloque.pasos.map((paso, j) => (
                    <li key={j} className="relative flex gap-3 pb-4 last:pb-0">
                      {/* La guía une los pasos y se corta en el último: es lo
                          que hace que se lean como una secuencia y no como
                          cuatro frases sueltas. */}
                      {j < bloque.pasos.length - 1 && (
                        <span
                          aria-hidden
                          className="absolute top-7 bottom-0 left-[13.5px] w-px bg-accent/25"
                        />
                      )}
                      <span className="relative z-10 mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-accent/30 bg-accent/10 text-xs font-bold text-accent tabular-nums">
                        {paso.numero}
                      </span>
                      <div className="min-w-0 flex-1 pt-1 text-sm leading-relaxed">
                        <TextoRico texto={paso.texto} inline />
                      </div>
                    </li>
                  ))}
                </ol>
              ) : (
                <div
                  key={i}
                  className={cn(
                    "text-sm leading-relaxed",
                    // El primer bloque de prosa es la idea que abre el
                    // ejercicio ("la palabra clave es «ambas»"). Es lo que hay
                    // que entender para que los pasos signifiquen algo, así
                    // que se destaca en vez de perderse arriba de ellos.
                    i === 0
                      ? "border-l-2 border-accent/40 py-0.5 pl-3 font-medium text-foreground"
                      : "text-muted"
                  )}
                >
                  <TextoRico texto={bloque.texto} />
                </div>
              )
            )}
          </div>
        )}

        {respuestaCorrecta && (
          <div className="mt-4 flex items-baseline gap-2 border-t border-border pt-3">
            <span className="text-[11px] font-semibold tracking-wide text-muted uppercase">
              Respuesta
            </span>
            <span className="min-w-0 text-sm font-semibold text-success">
              <TextoRico texto={respuestaCorrecta} inline />
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

type Bloque =
  | { tipo: "prosa"; texto: string }
  | { tipo: "pasos"; pasos: { numero: string; texto: string }[] };

/** `1) haz esto` al principio de una línea. */
const PASO = /^(\d+)\)\s*(.*)$/;

/**
 * Separa la explicación en prosa y secuencias de pasos.
 *
 * Los bloques van separados por línea en blanco, igual que en `TextoRico`, y
 * dentro de un bloque los pasos van uno por línea. Un bloque cuenta como
 * secuencia solo si TODAS sus líneas están numeradas: media lista numerada es
 * prosa que casualmente empieza con un número, y forzarla a pasos la
 * descuadraría.
 */
function partirEnBloques(explicacion: string): Bloque[] {
  return explicacion
    .split(/\n\s*\n/)
    .map((b) => b.trim())
    .filter(Boolean)
    .map((bloque) => {
      const lineas = bloque.split("\n").map((l) => l.trim()).filter(Boolean);
      const pasos = lineas.map((l) => l.match(PASO));
      if (lineas.length > 1 && pasos.every(Boolean)) {
        return {
          tipo: "pasos" as const,
          pasos: pasos.map((m) => ({ numero: m![1], texto: m![2] })),
        };
      }
      return { tipo: "prosa" as const, texto: bloque };
    });
}
