import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";
import { getCarrerasCatalogo } from "@/lib/api";
import { nombreLegible, slugUniversidad } from "@/lib/carreras";

/**
 * El índice de universidades.
 *
 * Es la puerta de entrada al catálogo: sin una página que enlace las 1.855
 * fichas, Google no llega a ellas por más que estén en el sitemap. Se parte en
 * dos niveles (universidad, después carrera) porque 1.855 enlaces juntos se
 * rastrean mal y no le sirven a nadie.
 */
export const revalidate = 86400;

export const metadata: Metadata = {
  title: "Carreras y ponderaciones PAES",
  description:
    "Ponderaciones oficiales del DEMRE de las carreras de las universidades chilenas: cuánto pesa cada prueba, el puntaje ponderado mínimo de postulación y las vacantes.",
  alternates: { canonical: "/carreras" },
};

export default async function CarrerasPage() {
  const catalogo = await getCarrerasCatalogo();

  // Una entrada por universidad, con cuántas carreras tiene. El orden lo trae
  // la API ya resuelto, así que basta con recorrer una vez.
  const universidades = new Map<string, number>();
  for (const c of catalogo) {
    universidades.set(c.universidad, (universidades.get(c.universidad) ?? 0) + 1);
  }

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
              Ponderaciones de {catalogo.length.toLocaleString("es-CL")} carreras
            </h1>
            <p className="mt-3 text-lg text-muted-foreground">
              Cuánto pesa cada prueba en cada carrera, el ponderado mínimo para postular y
              las vacantes. Elige tu universidad y simula tu puntaje.
            </p>
          </div>
        </section>

        <section className="px-6 pb-20">
          <div className="mx-auto max-w-3xl">
            <ul className="grid gap-2 sm:grid-cols-2">
              {[...universidades.entries()].map(([universidad, total]) => (
                <li key={universidad}>
                  <Link
                    href={`/carreras/${slugUniversidad(universidad)}`}
                    className="flex items-center justify-between gap-3 rounded-lg border border-border bg-card p-3 transition-colors hover:border-accent/40"
                  >
                    <span className="min-w-0 flex-1 text-sm">{nombreLegible(universidad)}</span>
                    <span className="shrink-0 text-xs text-muted-foreground tabular-nums">
                      {total}
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
