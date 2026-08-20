import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import {
  BuscadorConParams,
  BuscadorEsqueleto,
} from "@/components/carreras/buscador-carreras";
import { SiteFooter } from "@/components/site-footer";
import { getUniversidades, type Universidad } from "@/lib/api";
import { nombreLegible, slugUniversidad } from "@/lib/carreras";

/**
 * El índice de universidades.
 *
 * Es la puerta de entrada al catálogo: sin una página que enlace las 1.855
 * fichas, Google no llega a ellas por más que estén en el sitemap. Se parte en
 * dos niveles (universidad, después carrera) porque 1.855 enlaces juntos se
 * rastrean mal y no le sirven a nadie.
 */
/**
 * Una hora, no un día, a diferencia del resto del catálogo.
 *
 * Esta página se arma con una llamada a la API en tiempo de build. Si esa
 * llamada falla, abajo se cae a una lista vacía para no tumbar el deploy, y
 * ese estado degradado queda cacheado. Una hora acota cuánto puede durar; el
 * dato en sí cambia una vez al año, así que la frescura no es lo que manda
 * acá.
 */
export const revalidate = 3600;

export const metadata: Metadata = {
  title: "Carreras y ponderaciones PAES",
  description:
    "Ponderaciones oficiales del DEMRE de las carreras de las universidades chilenas: cuánto pesa cada prueba, el puntaje ponderado mínimo de postulación y las vacantes.",
  alternates: { canonical: "/carreras" },
};

export default async function CarrerasPage() {
  // Ver el comentario de `revalidate`: un build no puede caerse porque la API
  // no conteste, así que el error se traga y la página lo dice en vez de
  // mostrar un índice vacío como si no hubiera carreras.
  //
  // El conteo por universidad lo hace Postgres con un GROUP BY. Antes esta
  // página se bajaba las 1.855 filas del catálogo para terminar contándolas en
  // un Map y escribir 47 números.
  let universidades: Universidad[] = [];
  try {
    universidades = await getUniversidades();
  } catch {
    universidades = [];
  }

  const totalCarreras = universidades.reduce((suma, u) => suma + u.carreras, 0);

  return (
    <>
      <main className="flex flex-1 flex-col">
        <section className="hero-glow relative overflow-hidden px-6 pt-20 pb-12">
          <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[18rem]" />
          <div className="relative mx-auto max-w-3xl">
            <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
              Datos oficiales del DEMRE
            </span>
            <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              {totalCarreras > 0
                ? `Ponderaciones de ${totalCarreras.toLocaleString("es-CL")} carreras`
                : "Carreras y ponderaciones PAES"}
            </h1>
            <p className="mt-3 text-lg text-muted-foreground">
              Cuánto pesa cada prueba en cada carrera, el ponderado mínimo para postular y
              las vacantes. Busca la tuya o elige tu universidad, y simula tu puntaje.
            </p>

            {/* El buscador va arriba de todo: "cuánto necesito para Enfermería
                en la UdeC" es la pregunta con la que la gente llega, y el
                índice por universidad obliga a saber la respuesta antes de
                preguntarla. */}
            <div className="mt-6">
              {/* Suspense obligatorio: useSearchParams obliga a renderizar en
                  el cliente todo lo que lo contenga, y el índice de
                  universidades tiene que seguir siendo estático. */}
              <Suspense fallback={<BuscadorEsqueleto />}>
                <BuscadorConParams />
              </Suspense>
            </div>
          </div>
        </section>

        <section className="px-6 pb-20">
          <div className="mx-auto max-w-3xl">
            <h2 className="mb-3 text-sm font-semibold tracking-wide text-muted uppercase">
              O elige tu universidad
            </h2>

            {universidades.length === 0 && (
              <p className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground">
                No pudimos cargar el listado en este momento. Vuelve a intentarlo en unos
                minutos: los datos están, es la conexión la que falló.
              </p>
            )}

            <ul className="grid gap-2 sm:grid-cols-2">
              {universidades.map(({ universidad, carreras }) => (
                <li key={universidad}>
                  <Link
                    href={`/carreras/${slugUniversidad(universidad)}`}
                    className="flex items-center justify-between gap-3 rounded-lg border border-border bg-card p-3 transition-colors hover:border-accent/40"
                  >
                    <span className="min-w-0 flex-1 text-sm">{nombreLegible(universidad)}</span>
                    <span className="shrink-0 text-xs text-muted-foreground tabular-nums">
                      {carreras}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
