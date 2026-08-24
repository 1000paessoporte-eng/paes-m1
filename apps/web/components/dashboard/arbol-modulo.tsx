import Link from "next/link";
import type { SkillNode } from "@/lib/api";

/**
 * Vista previa del Árbol de Habilidades: en qué va el estudiante y qué sigue.
 *
 * No reproduce el grafo completo (eso es /arbol). Muestra la ruta inmediata:
 * lo último dominado, el nodo sugerido para practicar ahora, y lo que se
 * desbloquea después.
 */

const ETIQUETA_EJE: Record<string, string> = {
  numeros: "Números",
  algebra: "Álgebra y Funciones",
  geometria: "Geometría",
  probabilidad: "Probabilidad y Estadística",
};

interface Props {
  nodos: SkillNode[];
  recomendado: SkillNode | null;
}

export function ArbolModulo({ nodos, recomendado }: Props) {
  const dominados = nodos.filter((n) => n.status === "mastered");
  const disponibles = nodos.filter((n) => n.status === "unlocked");
  const bloqueados = nodos.filter((n) => n.status === "locked");
  const total = nodos.length;
  const pctDominado = total > 0 ? Math.round((dominados.length / total) * 100) : 0;

  // La ruta que se dibuja: los dos últimos dominados, el sugerido, y lo que
  // viene después. Si no hay sugerido (todo dominado), se rellena con lo que
  // haya para que el módulo nunca quede vacío.
  const siguiente =
    recomendado ?? disponibles[0] ?? bloqueados[0] ?? null;
  // "Lo que viene después" salía de los BLOQUEADOS, y desde que el árbol dejó
  // de bloquear no queda ninguno: la ruta se cortaba en el tema sugerido. Ahora
  // sale de lo que falta por dominar, que es lo que siempre quiso decir.
  const porDominar = [...disponibles, ...bloqueados];
  const posteriores = porDominar
    .filter((n) => n.code !== siguiente?.code)
    .slice(0, 2);
  const ruta = [
    ...dominados.slice(-2),
    ...(siguiente ? [siguiente] : []),
    ...posteriores,
  ];

  return (
    <section className="card-panel flex flex-col p-6" aria-labelledby="h-arbol">
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="h-arbol" className="font-semibold tracking-tight">
          Árbol de Habilidades
        </h2>
        <Link href="/arbol" className="text-xs font-medium text-accent hover:underline">
          Abrir el árbol
        </Link>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
        <span className="tabular-nums">
          <span className="text-lg font-bold">{dominados.length}</span>
          <span className="text-muted">/{total} temas dominados</span>
        </span>
        <span className="h-4 w-px bg-border" aria-hidden />
        <span className="text-muted tabular-nums">
          {disponibles.length} disponibles para practicar
        </span>
      </div>

      <div
        className="mt-3 h-2 overflow-hidden rounded-full bg-surface-hover"
        role="progressbar"
        aria-valuenow={pctDominado}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Avance en el árbol de habilidades"
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${pctDominado}%`,
            background: "linear-gradient(90deg, var(--accent), var(--accent-2))",
          }}
        />
      </div>

      {ruta.length === 0 ? (
        <p className="mt-5 text-sm text-muted">
          El árbol se arma con tu primer ensayo.
        </p>
      ) : (
        <ol className="mt-6 flex flex-col gap-0">
          {ruta.map((nodo, i) => (
            <NodoRuta
              key={nodo.code}
              nodo={nodo}
              sugerido={nodo.code === siguiente?.code}
              ultimo={i === ruta.length - 1}
            />
          ))}
        </ol>
      )}
    </section>
  );
}

function NodoRuta({
  nodo,
  sugerido,
  ultimo,
}: {
  nodo: SkillNode;
  sugerido: boolean;
  ultimo: boolean;
}) {
  const dominado = nodo.status === "mastered";
  const bloqueado = nodo.status === "locked";

  return (
    <li className="flex gap-3">
      {/* Columna del conector: el punto del nodo y la línea hacia el siguiente */}
      <div className="flex flex-col items-center">
        <span
          className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 text-[10px] font-bold ${
            dominado
              ? "border-success bg-success text-on-fill"
              : sugerido
                ? "border-accent-warm bg-accent-warm text-on-fill"
                : bloqueado
                  ? "border-border-strong bg-background text-muted"
                  : "border-accent bg-background text-accent"
          }`}
          aria-hidden
        >
          {dominado ? "✓" : bloqueado ? "" : "•"}
        </span>
        {!ultimo && (
          <span
            className={`w-0.5 flex-1 ${dominado ? "bg-success/40" : "bg-border"}`}
            aria-hidden
          />
        )}
      </div>

      <div className={`min-w-0 flex-1 ${ultimo ? "pb-0" : "pb-5"}`}>
        <div className="flex flex-wrap items-center gap-2">
          <p
            className={`truncate text-sm font-medium ${
              bloqueado && !sugerido ? "text-muted" : "text-foreground"
            }`}
          >
            {nodo.name}
          </p>
          {sugerido && (
            <span className="rounded-full bg-accent-warm/10 px-2 py-0.5 text-[11px] font-semibold text-accent-warm-strong">
              Sigue por acá
            </span>
          )}
        </div>
        <p className="mt-0.5 text-xs text-muted">
          {ETIQUETA_EJE[nodo.axis] ?? nodo.axis}
          {nodo.attempts > 0 && (
            <> · {Math.round(nodo.accuracy * 100)}% de acierto</>
          )}
        </p>

        {/* Dos caminos, no uno. Cuando el nodo tenía lección, el panel mandaba
            SIEMPRE a leerla y practicar quedaba a dos clics: en toda la vida de
            la plataforma se respondieron 4 preguntas en Modo Práctica. Quien ya
            sabe el tema y solo quiere ejercitar no debería tener que pasar por
            la teoría para llegar. */}
        {sugerido && !bloqueado && (
          <div className="mt-2 flex flex-wrap gap-2">
            {nodo.has_lesson && (
              <Link
                href={`/aprender/${nodo.code}`}
                className="inline-flex rounded-lg border border-border px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-surface-hover"
              >
                Estudiar la teoría
              </Link>
            )}
            <Link
              href={`/practicar/${nodo.code}`}
              className="inline-flex rounded-lg border border-accent-warm/40 px-3 py-1.5 text-xs font-semibold text-accent-warm-strong transition-colors hover:bg-accent-warm/5"
            >
              Practicar este tema →
            </Link>
          </div>
        )}
      </div>
    </li>
  );
}
