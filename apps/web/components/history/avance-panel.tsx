import { COLOR_PRUEBA, NOMBRE_CORTO } from "@/lib/colores-prueba";
import type { AvancePrueba } from "@/lib/progreso";

/** El puntaje máximo de la PAES. El mínimo es 100, no 0: la barra parte ahí. */
const PUNTAJE_MAX = 1000;
const PUNTAJE_MIN = 100;

function pct(puntaje: number): number {
  return ((puntaje - PUNTAJE_MIN) / (PUNTAJE_MAX - PUNTAJE_MIN)) * 100;
}

/**
 * Cuánto subió desde su primer ensayo, prueba por prueba.
 *
 * Es la pantalla entera en una frase: alguien que estudia hace tres semanas no
 * recuerda con qué puntaje llegó, y sin ese punto de partida cada ensayo se
 * juzga solo contra el anterior --que sube y baja por el día que tuvo-- en vez
 * de contra el lugar del que salió.
 *
 * NO se maquilla el número. Si bajó, dice que bajó: un panel que solo sabe
 * felicitar deja de significar algo la primera vez que el alumno nota que le
 * mintió. Lo que sí se elige es el TITULAR: cuando hay avance, el avance manda;
 * cuando no, manda la mejor marca, que es igual de cierta y no abre la pantalla
 * con un número en rojo.
 */
export function AvancePanel({ avances }: { avances: AvancePrueba[] }) {
  if (avances.length === 0) return null;

  const principal = avances[0];
  const subio = principal.delta > 0;

  return (
    <section className="mb-6 overflow-hidden rounded-2xl border border-border bg-surface">
      <div className="border-b border-border p-5 sm:p-6">
        <p className="text-xs font-medium tracking-wide text-muted uppercase">
          {subio ? "Tu avance desde que llegaste" : "Tu mejor marca hasta ahora"}
        </p>

        {subio ? (
          <>
            {/* Sin tabular-nums: es una figura, no una columna que se compara
                hacia abajo, y las cifras proporcionales se leen mejor grandes. */}
            <p className="mt-1 text-5xl leading-none font-bold text-success sm:text-6xl">
              +{principal.delta}
              <span className="ml-2 align-middle text-lg font-semibold text-muted">
                puntos
              </span>
            </p>
            <p className="mt-2.5 text-sm text-muted">
              En {NOMBRE_CORTO[principal.subject]} partiste en{" "}
              <strong className="text-foreground">{principal.primero}</strong> y tus
              últimos ensayos promedian{" "}
              <strong className="text-foreground">{principal.ahora}</strong>. Eso no
              se te va a olvidar en la prueba.
            </p>
          </>
        ) : (
          <>
            <p className="mt-1 text-5xl leading-none font-bold sm:text-6xl">
              {principal.mejor}
              <span className="ml-2 align-middle text-lg font-semibold text-muted">
                puntos
              </span>
            </p>
            <p className="mt-2.5 text-sm text-muted">
              Es lo mejor que has hecho en {NOMBRE_CORTO[principal.subject]}, y ya lo
              lograste una vez. Tus últimos ensayos promedian {principal.ahora}:{" "}
              {principal.delta === 0
                ? "estás igual que en el primero"
                : `${Math.abs(principal.delta)} puntos bajo tu primero`}
              , así que el siguiente es para volver a acercarte.
            </p>
          </>
        )}
      </div>

      {/* Una fila por prueba: el titular habla de una sola, y quien rinde tres
          necesita ver las tres sin que se promedien entre ellas. */}
      <ul className="divide-y divide-border">
        {avances.map((a) => (
          <li key={a.subject} className="px-5 py-3.5 sm:px-6">
            <div className="flex items-baseline justify-between gap-3">
              <span
                className="text-sm font-semibold"
                style={{ color: COLOR_PRUEBA[a.subject] }}
              >
                {NOMBRE_CORTO[a.subject]}
              </span>
              <span className="text-xs text-muted">
                {a.ensayos} {a.ensayos === 1 ? "ensayo" : "ensayos"}
              </span>
            </div>

            {/* El recorrido, no dos números sueltos: se ve de dónde salió,
                dónde está y cuánto de la escala cubrió. */}
            <div className="mt-2 flex items-center gap-3">
              <span className="w-9 shrink-0 text-right text-xs text-muted tabular-nums">
                {a.primero}
              </span>
              <div className="relative h-2 flex-1 rounded-full bg-surface-hover">
                <div
                  className="absolute inset-y-0 rounded-full"
                  style={{
                    left: `${pct(Math.min(a.primero, a.ahora))}%`,
                    width: `${Math.abs(pct(a.ahora) - pct(a.primero))}%`,
                    backgroundColor: COLOR_PRUEBA[a.subject],
                  }}
                />
                <span
                  className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface"
                  style={{
                    left: `${pct(a.ahora)}%`,
                    backgroundColor: COLOR_PRUEBA[a.subject],
                  }}
                />
              </div>
              <span className="w-9 shrink-0 text-xs font-semibold tabular-nums">
                {a.ahora}
              </span>
              <span
                className={
                  a.delta > 0
                    ? "w-12 shrink-0 text-xs font-semibold text-success tabular-nums"
                    : a.delta < 0
                      ? "w-12 shrink-0 text-xs font-semibold text-danger tabular-nums"
                      : "w-12 shrink-0 text-xs text-muted tabular-nums"
                }
              >
                {a.delta > 0 ? `+${a.delta}` : a.delta < 0 ? a.delta : "="}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
