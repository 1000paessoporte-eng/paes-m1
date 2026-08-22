import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SiteFooter } from "@/components/site-footer";
import { getCarrerasCatalogo, type CarreraCatalogo } from "@/lib/api";
import { nombreLegible, slugCarrera, slugUniversidad } from "@/lib/carreras";

/**
 * Las carreras de una universidad.
 *
 * El segundo nivel del índice: desde acá se llega a cada ficha. Una página por
 * universidad (47 en total) mantiene cada listado en un tamaño que se rastrea
 * y se lee.
 */
export const revalidate = 86400;
export const dynamicParams = true;

type Props = { params: Promise<{ universidad: string }> };

/** Las carreras de esa universidad y su nombre real, o null si no existe. */
async function universidadDelSlug(
  slug: string
): Promise<{ nombre: string; carreras: CarreraCatalogo[] } | null> {
  const catalogo = await getCarrerasCatalogo();
  const carreras = catalogo.filter((c) => slugUniversidad(c.universidad) === slug);
  if (carreras.length === 0) return null;
  return { nombre: carreras[0].universidad, carreras };
}

export async function generateStaticParams() {
  // Son 47 y salen de una sola llamada, así que sí conviene prerenderizarlas:
  // son las páginas que reparten el rastreo hacia las 1.855 fichas.
  //
  // Si la API no responde se devuelve una lista vacía en vez de propagar el
  // error. Un build NO puede caerse porque un servicio vivo no conteste: pasó
  // exactamente eso al desplegar esto la primera vez, cuando la web se
  // construyó un minuto antes de que la API publicara este endpoint y el
  // deploy entero falló. Con la lista vacía las páginas se generan igual, solo
  // que en la primera visita (`dynamicParams` ya está en true).
  try {
    const catalogo = await getCarrerasCatalogo();
    return [...new Set(catalogo.map((c) => slugUniversidad(c.universidad)))].map(
      (universidad) => ({ universidad })
    );
  } catch {
    return [];
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { universidad } = await params;
  const datos = await universidadDelSlug(universidad);
  if (!datos) return { title: "Universidad no encontrada" };

  return {
    title: `Carreras y ponderaciones de ${nombreLegible(datos.nombre)}`,
    description: `Las ${datos.carreras.length} carreras de ${nombreLegible(datos.nombre)} con sus ponderaciones PAES oficiales, ponderado mínimo de postulación y vacantes.`,
    alternates: { canonical: `/carreras/${universidad}` },
  };
}

export default async function UniversidadPage({ params }: Props) {
  const { universidad } = await params;
  const datos = await universidadDelSlug(universidad);
  if (!datos) notFound();

  // Las sedes agrupan mejor que una lista plana: la misma carrera aparece en
  // varias ciudades y sin la sede el listado se ve duplicado.
  const porSede = new Map<string, CarreraCatalogo[]>();
  for (const c of datos.carreras) {
    porSede.set(c.sede, [...(porSede.get(c.sede) ?? []), c]);
  }

  return (
    <>
      <main className="flex flex-1 flex-col">
        <section className="hero-glow relative overflow-hidden px-6 pt-16 pb-10">
          <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[14rem]" />
          <div className="relative mx-auto max-w-3xl">
            <nav aria-label="Migas" className="text-sm text-muted">
              <Link href="/carreras" className="hover:text-accent">
                Carreras
              </Link>
            </nav>
            <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              {nombreLegible(datos.nombre)}
            </h1>
            <p className="mt-2 text-muted">
              {datos.carreras.length} carreras con ponderaciones oficiales
            </p>
          </div>
        </section>

        <section className="px-6 pb-20">
          <div className="mx-auto max-w-3xl space-y-8">
            {[...porSede.entries()].map(([sede, carreras]) => (
              <div key={sede}>
                <h2 className="text-sm font-semibold text-muted uppercase">
                  {nombreLegible(sede)}
                </h2>
                <ul className="mt-3 grid gap-2">
                  {carreras.map((c) => (
                    <li key={c.codigo}>
                      <Link
                        href={`/carrera/${slugCarrera(c)}`}
                        className="block rounded-lg border border-border bg-surface p-3 text-sm transition-colors hover:border-accent/40"
                      >
                        {nombreLegible(c.nombre)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
