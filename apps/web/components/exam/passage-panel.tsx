import { cn } from "@paes-m1/utils";

import { TextoRico } from "@/components/texto-rico";
import type { ExamQuestion } from "@/lib/api";

type Passage = NonNullable<ExamQuestion["passage"]>;

const ETIQUETA_TIPO: Record<string, string> = {
  literario: "Texto literario",
  no_literario: "Texto no literario",
  discontinuo: "Texto discontinuo",
};

/**
 * Texto base de una pregunta de Competencia Lectora.
 *
 * En esa prueba la pregunta no se entiende sin el texto, así que el pasaje se
 * muestra junto a ella y no en una pantalla aparte. Varias preguntas seguidas
 * comparten el mismo pasaje: el componente lo deja fijo mientras el estudiante
 * avanza entre ellas, para que no tenga que volver a buscarlo.
 */
export function PassagePanel({
  passage,
  className,
}: {
  passage: Passage;
  className?: string;
}) {
  return (
    <aside
      className={cn("card-panel max-h-[70vh] overflow-y-auto p-5", className)}
      aria-label="Texto de lectura"
    >
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2 border-b border-border pb-3">
        <h2 className="font-semibold tracking-tight">{passage.title}</h2>
        <span className="rounded-full bg-surface-hover px-2 py-0.5 text-[11px] text-muted">
          {ETIQUETA_TIPO[passage.kind] ?? passage.kind}
        </span>
      </div>

      {/* En serif y no en la sans de la interfaz. No es adorno: este es el
          único bloque del ensayo que se lee de corrido, y una serif lo separa
          del cromo que lo rodea --enunciado, alternativas, relojes-- además de
          sostener mejor varios párrafos seguidos en pantalla. */}
      <div className="font-lectura flex flex-col gap-3 text-[0.95rem] leading-[1.7]">
        {passage.body.split("\n\n").map((parrafo, i) => (
          <TextoRico key={i} texto={parrafo} />
        ))}
      </div>

      {passage.source_note && (
        <p className="mt-4 border-t border-border pt-3 text-xs text-muted">
          {passage.source_note}
        </p>
      )}
    </aside>
  );
}
