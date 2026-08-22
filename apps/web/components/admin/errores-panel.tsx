import type { ErrorCliente } from "@/lib/api";

/**
 * Lo que se está rompiendo en el navegador de los estudiantes.
 *
 * Hasta ahora esto no existía en ninguna parte: un error de JavaScript dejaba
 * la página en blanco en el teléfono de alguien y nosotros nos enterábamos
 * solo si esa persona se molestaba en escribirnos. Con tres alumnos activos
 * eso todavía podía pasar; al abrir al público, no.
 *
 * Se agrupa por mensaje y ruta, ordenado por cuántas veces pasó: lo que hay
 * que arreglar es el error, no cada una de sus apariciones.
 */

const FECHA = new Intl.DateTimeFormat("es-CL", {
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

export function ErroresPanel({ errores }: { errores: ErrorCliente[] }) {
  if (errores.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface p-5">
        <p className="text-sm font-medium text-success">Sin errores en dos semanas</p>
        <p className="mt-1 text-sm text-muted">
          Nada reventó en el navegador de nadie. Si esto se llena, acá va a
          decir qué y en qué página.
        </p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-border rounded-xl border border-border bg-surface">
      {errores.map((e) => (
        <li key={`${e.ruta}|${e.mensaje}`} className="p-4">
          <div className="flex items-baseline justify-between gap-3">
            <p className="min-w-0 flex-1 font-mono text-sm break-words">{e.mensaje}</p>
            <p className="shrink-0 text-xs tabular-nums">
              <strong className="text-danger">{e.veces}</strong>
              <span className="text-muted">
                {" "}
                {e.veces === 1 ? "vez" : "veces"}
              </span>
            </p>
          </div>
          <p className="mt-1 text-xs text-muted">
            {e.ruta} · {e.usuarios === 0 ? "sin sesión" : `${e.usuarios} ${e.usuarios === 1 ? "cuenta" : "cuentas"}`}
            {e.navegador && ` · ${e.navegador}`} · último {FECHA.format(new Date(e.ocurrido_en))}
          </p>
          {e.pila && (
            <details className="mt-2">
              <summary className="cursor-pointer text-xs text-muted hover:text-foreground">
                Ver la traza
              </summary>
              <pre className="mt-2 max-h-48 overflow-auto rounded-lg bg-background p-3 text-[11px] leading-relaxed whitespace-pre-wrap text-muted">
                {e.pila}
              </pre>
            </details>
          )}
        </li>
      ))}
    </ul>
  );
}
