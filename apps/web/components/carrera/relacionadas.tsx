import Link from "next/link";
import { nombreCarrera, nombreLegible, slugCarrera, slugUniversidad } from "@/lib/carreras";
import type { CarreraRelacionada } from "@/lib/api";

/**
 * Por dónde seguir desde la ficha de una carrera.
 *
 * Existe porque las 1.855 fichas eran callejones sin salida: 296 palabras y
 * ningún enlace a otra. Quien llega desde Google no busca una carrera
 * concreta —busca DÓNDE le alcanza— y tenía que volver al índice y empezar de
 * nuevo para comparar. Google entraba, no encontraba nada que seguir, y se
 * iba.
 *
 * Va DESPUÉS del llamado a rendir un ensayo, no antes: quien ya se convenció
 * no debería tropezar con veinte salidas justo antes del botón.
 */
export function CarrerasRelacionadas({
  mismaCarrera,
  mismaUniversidad,
  nombre,
  universidad,
}: {
  mismaCarrera: CarreraRelacionada[];
  mismaUniversidad: CarreraRelacionada[];
  nombre: string;
  universidad: string;
}) {
  if (mismaCarrera.length === 0 && mismaUniversidad.length === 0) return null;

  return (
    <section className="px-6 pb-16">
      <div className="mx-auto grid max-w-3xl gap-10">
        {mismaCarrera.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold text-balance break-words">
              {nombreCarrera(nombre)} en otras universidades
            </h2>
            <p className="mt-1 text-sm text-muted">
              De menor a mayor ponderado mínimo de postulación. Las que el DEMRE no
              publica van al final: no tener el dato no significa que se entre con
              menos.
            </p>
            <ul className="mt-4 grid gap-2">
              {/* min-w-0: sin esto el ítem de grid se estira al ancho de su
                  contenido y el truncate de dentro nunca llega a aplicarse. */}
              {mismaCarrera.map((c) => (
                <li key={c.codigo} className="min-w-0">
                  <Link
                    href={`/carrera/${slugCarrera(c)}`}
                    className="flex items-baseline justify-between gap-4 rounded-lg border border-border px-4 py-3 transition-colors hover:bg-surface-hover"
                  >
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">
                        {nombreLegible(c.universidad)}
                      </span>
                      <span className="block truncate text-xs text-muted">
                        {nombreLegible(c.sede)}
                        {c.vacantes ? ` · ${c.vacantes} vacantes` : ""}
                      </span>
                    </span>
                    <span className="shrink-0 text-right">
                      {c.ponderado_min ? (
                        <>
                          <span className="block text-sm font-semibold tabular-nums">
                            {c.ponderado_min}
                          </span>
                          <span className="block text-[11px] text-muted">
                            ponderado mín.
                          </span>
                        </>
                      ) : (
                        <span className="block text-[11px] text-muted">sin mínimo</span>
                      )}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}

        {mismaUniversidad.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold text-balance break-words">
              Otras carreras de {nombreLegible(universidad)}
            </h2>
            <ul className="mt-4 flex flex-wrap gap-2">
              {mismaUniversidad.map((c) => (
                <li key={c.codigo}>
                  <Link
                    href={`/carrera/${slugCarrera(c)}`}
                    className="inline-block max-w-full truncate rounded-full border border-border px-3 py-1.5 text-sm transition-colors hover:bg-surface-hover"
                  >
                    {nombreCarrera(c.nombre)}
                  </Link>
                </li>
              ))}
            </ul>
            <Link
              href={`/carreras/${slugUniversidad(universidad)}`}
              className="mt-4 inline-block break-words text-sm text-accent underline underline-offset-4"
            >
              Ver todas las carreras de {nombreLegible(universidad)} →
            </Link>
          </div>
        )}
      </div>
    </section>
  );
}
