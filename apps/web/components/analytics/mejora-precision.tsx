import Link from "next/link";

interface Dia {
  questions_answered: number;
  correct: number;
}

/**
 * Cuántas respuestas necesita cada mitad para que la comparación signifique algo.
 *
 * Con cinco preguntas por lado, acertar una de más mueve la precisión veinte
 * puntos y la pantalla anuncia una mejora que fue azar. Preferimos no mostrar
 * nada antes que celebrar ruido: el alumno que descubre que el número no era
 * cierto deja de creerle a todos los demás.
 */
const MINIMO_POR_MITAD = 15;

/**
 * Su precisión de la semana pasada contra la de esta.
 *
 * El gráfico de acierto diario ya existe, pero un serrucho de catorce puntos no
 * responde la pregunta que el alumno se hace --"¿estoy mejorando o no?"--:
 * obliga a promediar a ojo dos mitades de una línea que sube y baja todos los
 * días. Esto lo promedia y lo dice en una frase.
 */
export function MejoraPrecision({ dias }: { dias: Dia[] }) {
  const mitad = Math.floor(dias.length / 2);
  const antes = agregar(dias.slice(0, mitad));
  const ahora = agregar(dias.slice(mitad));

  // Sin datos suficientes NO se devuelve null. Devolver null dejaba media
  // pantalla en blanco al lado de "Tu constancia", y un hueco se lee como algo
  // que se cayó, no como algo que todavía no existe. Se dice qué falta para
  // que aparezca, que además es una razón concreta para volver.
  // Sin datos suficientes NO se devuelve null. Devolver null dejaba media
  // pantalla en blanco al lado de "Tu constancia", y un hueco se lee como algo
  // que se cayó, no como algo que todavía no existe.
  if (antes.preguntas < MINIMO_POR_MITAD || ahora.preguntas < MINIMO_POR_MITAD) {
    // A la semana PASADA ya no se le pueden agregar respuestas: si el déficit
    // está ahí, esto no se desbloquea practicando hoy sino dejando pasar los
    // días. Decir "te faltan N" en ese caso sería mandar a alguien a hacer
    // algo que no sirve.
    const faltanEstaSemana = MINIMO_POR_MITAD - ahora.preguntas;
    const esperandoLaSemana = faltanEstaSemana <= 0;

    return (
      <section className="rounded-xl border border-dashed border-border bg-transparent p-5">
        <h2 className="text-sm font-semibold">Cómo va tu precisión</h2>
        <p className="mt-2 text-sm text-muted">
          Acá vas a ver si estás acertando más que la semana pasada. Para
          compararlo hacen falta al menos{" "}
          <strong className="text-foreground">{MINIMO_POR_MITAD} respuestas</strong>{" "}
          en cada una de las dos semanas: con menos, acertar una de más mueve el
          porcentaje veinte puntos y estaríamos celebrando azar.
        </p>

        <div className="mt-4 flex items-end gap-8">
          <div>
            <p className="font-display text-3xl leading-none font-bold tabular-nums">
              {antes.preguntas}
            </p>
            <p className="mt-1 text-xs text-muted">semana anterior</p>
          </div>
          <div>
            <p className="font-display text-3xl leading-none font-bold tabular-nums">
              {ahora.preguntas}
            </p>
            <p className="mt-1 text-xs text-muted">esta semana</p>
          </div>
        </div>

        <p className="mt-4 text-sm">
          {esperandoLaSemana ? (
            <span className="text-muted">
              Esta semana ya la tienes. La comparación aparece sola cuando la
              semana anterior también junte {MINIMO_POR_MITAD}: sigue
              practicando y en unos días se desbloquea.
            </span>
          ) : (
            <Link href="/examen" className="text-accent font-medium">
              Te faltan {faltanEstaSemana}{" "}
              {faltanEstaSemana === 1 ? "respuesta" : "respuestas"} esta semana →
            </Link>
          )}
        </p>
      </section>
    );
  }

  const pctAntes = Math.round((antes.correctas / antes.preguntas) * 100);
  const pctAhora = Math.round((ahora.correctas / ahora.preguntas) * 100);
  const delta = pctAhora - pctAntes;

  return (
    <section className="rounded-xl border border-border bg-surface p-5">
      <h2 className="text-sm font-semibold">Cómo va tu precisión</h2>

      <p className="mt-3 text-sm text-muted">
        {delta > 0 ? (
          <>
            Pasaste de acertar el <strong className="text-foreground">{pctAntes}%</strong>{" "}
            a acertar el{" "}
            <strong className="text-success">{pctAhora}%</strong>. Son{" "}
            {delta} puntos porcentuales en una semana.
          </>
        ) : delta < 0 ? (
          <>
            Esta semana acertaste el{" "}
            <strong className="text-foreground">{pctAhora}%</strong>, contra el{" "}
            {pctAntes}% de la anterior. Suele pasar al entrar a temas nuevos: el
            porcentaje baja antes de volver a subir.
          </>
        ) : (
          <>
            Vas parejo: <strong className="text-foreground">{pctAhora}%</strong> las dos
            semanas.
          </>
        )}
      </p>

      {/* Las dos barras van del MISMO color: es la misma medida en dos momentos,
          no dos categorías. Lo que se compara es el largo, y darles color
          distinto haría creer que miden cosas distintas. */}
      <div className="mt-4 space-y-2.5">
        <Barra etiqueta="Semana anterior" pct={pctAntes} preguntas={antes.preguntas} />
        <Barra etiqueta="Esta semana" pct={pctAhora} preguntas={ahora.preguntas} />
      </div>
    </section>
  );
}

function agregar(dias: Dia[]) {
  return dias.reduce(
    (acc, d) => ({
      preguntas: acc.preguntas + d.questions_answered,
      correctas: acc.correctas + d.correct,
    }),
    { preguntas: 0, correctas: 0 }
  );
}

function Barra({
  etiqueta,
  pct,
  preguntas,
}: {
  etiqueta: string;
  pct: number;
  preguntas: number;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3 text-xs">
        <span className="text-muted">{etiqueta}</span>
        <span className="text-muted tabular-nums">
          {pct}% de {preguntas} preguntas
        </span>
      </div>
      <div className="mt-1 h-2.5 overflow-hidden rounded-full bg-surface-hover">
        <div
          className="h-full rounded-full bg-accent transition-[width] duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
