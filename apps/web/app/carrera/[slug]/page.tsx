import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SimuladorCarrera } from "@/components/carreras/simulador-carrera";
import { DatosEstructurados } from "@/components/datos-estructurados";
import { SiteFooter } from "@/components/site-footer";
import { ApiError, getCarrera, type CarreraPublica } from "@/lib/api";
import { codigoDesdeSlug, nombreLegible, slugCarrera } from "@/lib/carreras";
import { factoresDe } from "@/lib/ponderado";

/**
 * La ficha pública de una carrera.
 *
 * Es la página que existe para que Google la encuentre: son 1.855 URLs con la
 * pregunta que un postulante chileno escribe en agosto ("cuánto puntaje
 * necesito para Enfermería en la UdeC"). El dato ya estaba en la base desde
 * que se cargó la oferta del DEMRE; hasta ahora vivía detrás del login, donde
 * no lo veía nadie que todavía no fuera usuario.
 *
 * No se prerenderizan en el build: 1.855 páginas cada una con su llamada a la
 * API alargarían el build de Vercel sin necesidad. Se generan en la primera
 * visita y quedan cacheadas un día (`revalidate`), que es la frecuencia real
 * con que cambia el dato: una vez por proceso de admisión.
 */
export const revalidate = 86400;
export const dynamicParams = true;

export function generateStaticParams() {
  return [];
}

type Props = { params: Promise<{ slug: string }> };

/** Trae la carrera del slug, o null si el código no existe o no viene. */
async function carreraDelSlug(slug: string): Promise<CarreraPublica | null> {
  const codigo = codigoDesdeSlug(slug);
  if (!codigo) return null;
  try {
    return await getCarrera(codigo);
  } catch (error) {
    // 404 es un caso normal acá: la URL la escribe cualquiera. Cualquier otro
    // error (API caída, 500) sí tiene que propagarse y activar error.tsx, para
    // no publicar un "no existe" cuando en realidad no pudimos preguntar.
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const carrera = await carreraDelSlug(slug);
  if (!carrera) return { title: "Carrera no encontrada" };

  const titulo = `${limpiar(carrera.nombre)} en ${nombreLegible(carrera.universidad)}`;
  const minimo = carrera.ponderado_min
    ? `Puntaje ponderado mínimo de postulación: ${carrera.ponderado_min} puntos.`
    : "Consulta las ponderaciones oficiales del proceso.";

  return {
    title: titulo,
    description: `Ponderaciones PAES ${carrera.proceso} de ${limpiar(carrera.nombre)} en ${nombreLegible(carrera.universidad)}, sede ${nombreLegible(carrera.sede)}. ${minimo} Simula tu puntaje gratis.`,
    alternates: { canonical: `/carrera/${slugCarrera(carrera)}` },
    openGraph: {
      title: titulo,
      description: `Ponderaciones oficiales del proceso ${carrera.proceso} y simulador de puntaje ponderado.`,
      type: "article",
    },
  };
}

export default async function CarreraPage({ params }: Props) {
  const { slug } = await params;
  const carrera = await carreraDelSlug(slug);
  if (!carrera) notFound();

  const factores = factoresDe(carrera);
  const nombre = limpiar(carrera.nombre);

  return (
    <>
      <main className="flex flex-1 flex-col">
        <section className="hero-glow relative overflow-hidden px-6 pt-16 pb-10">
          <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[16rem]" />
          <div className="relative mx-auto max-w-3xl">
            <nav aria-label="Migas" className="text-sm text-muted-foreground">
              <Link href="/carreras" className="hover:text-accent">
                Carreras
              </Link>
              <span className="mx-2">/</span>
              <span>{nombreLegible(carrera.universidad)}</span>
            </nav>

            <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">{nombre}</h1>
            <p className="mt-2 text-lg text-muted-foreground">
              {nombreLegible(carrera.universidad)} · sede {nombreLegible(carrera.sede)}
            </p>

            {/* Lo que la persona vino a buscar va primero, antes de cualquier
                explicación nuestra. */}
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <Dato
                etiqueta="Ponderado mínimo"
                valor={carrera.ponderado_min ? `${carrera.ponderado_min}` : null}
                nota={
                  carrera.ponderado_min
                    ? "puntos para poder postular"
                    : "El DEMRE no publicó un mínimo para esta carrera"
                }
                destacado
              />
              <Dato
                etiqueta="Promedio mínimo"
                valor={carrera.promedio_min ? `${carrera.promedio_min}` : null}
                nota={
                  carrera.promedio_min
                    ? "promedio Lectora y M1"
                    : "Sin promedio mínimo publicado"
                }
              />
              <Dato
                etiqueta="Vacantes"
                valor={carrera.vacantes ? `${carrera.vacantes}` : null}
                nota={carrera.vacantes ? "cupos ofrecidos" : "Sin vacantes publicadas"}
              />
            </div>

            {/* Decir qué NO es este número importa tanto como el número: un
                puntaje de corte y un mínimo de postulación son cosas distintas
                y confundirlos hace que alguien no postule pudiendo. */}
            <p className="mt-4 text-sm text-muted-foreground">
              Son los requisitos oficiales de <strong>postulación</strong> del proceso{" "}
              {carrera.proceso}, no los puntajes de corte. El corte depende de quiénes
              postulen ese año y se conoce recién al cerrar el proceso.
            </p>
          </div>
        </section>

        <section className="px-6 pb-12">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-xl font-semibold">Cómo se pondera</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Cada factor pesa lo que fija la universidad. Suman 100%.
            </p>

            <ul className="mt-4 space-y-2">
              {factores.map(({ factor, etiqueta, peso }) => (
                <li
                  key={factor}
                  className="flex items-center gap-4 rounded-lg border border-border bg-card p-3"
                >
                  <span className="min-w-0 flex-1 truncate text-sm">{etiqueta}</span>
                  <div
                    className="h-2 w-32 overflow-hidden rounded-full bg-muted"
                    role="presentation"
                  >
                    <div className="h-full bg-accent" style={{ width: `${peso}%` }} />
                  </div>
                  <span className="w-12 text-right text-sm font-semibold tabular-nums">
                    {peso}%
                  </span>
                </li>
              ))}
            </ul>

            {carrera.electivo_alternativo && (
              <p className="mt-3 text-sm text-muted-foreground">
                Esta carrera acepta <strong>Historia ó Ciencias</strong>: ambas pesan lo
                mismo y solo cuenta la mejor de las dos, así que basta con dar una.
              </p>
            )}
          </div>
        </section>

        <section className="px-6 pb-16">
          <div className="mx-auto max-w-3xl">
            <SimuladorCarrera carrera={carrera} />
          </div>
        </section>

        <section className="px-6 pb-20">
          <div className="mx-auto max-w-3xl rounded-xl border border-accent/30 bg-accent/5 p-6">
            <h2 className="text-lg font-semibold">
              ¿Te falta puntaje para {nombre}?
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Rinde un ensayo con preguntas reales y mira exactamente qué temas te están
              costando. Gratis y sin tarjeta.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <Link
                href="/demo"
                className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground"
              >
                Probar sin cuenta
              </Link>
              <Link
                href="/registro"
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium"
              >
                Crear cuenta gratis
              </Link>
            </div>
          </div>

          <p className="mx-auto mt-6 max-w-3xl text-xs text-muted-foreground">
            Ponderaciones del proceso de admisión {carrera.proceso}, publicadas por el
            DEMRE. Código de carrera {carrera.codigo}.{" "}
            <a href={carrera.fuente} className="underline" rel="nofollow noopener">
              Ver la fuente oficial
            </a>
            .
          </p>
        </section>
      </main>
      <SiteFooter />

      {/* Datos estructurados: es lo que permite que el resultado de Google
          muestre la carrera y la universidad, no solo el título de la página. */}
      <DatosEstructurados
        datos={{
          "@context": "https://schema.org",
          "@type": "EducationalOccupationalProgram",
          name: nombre,
          provider: { "@type": "CollegeOrUniversity", name: nombreLegible(carrera.universidad) },
          educationalProgramMode: "full-time",
          occupationalCategory: nombre,
          offers: carrera.vacantes
            ? { "@type": "Offer", availability: `${carrera.vacantes} vacantes` }
            : undefined,
        }}
      />
    </>
  );
}

/** Una cifra con su etiqueta, o el estado vacío honesto si no hay dato. */
function Dato({
  etiqueta,
  valor,
  nota,
  destacado = false,
}: {
  etiqueta: string;
  valor: string | null;
  nota: string;
  destacado?: boolean;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <p className="text-xs font-medium text-muted-foreground uppercase">{etiqueta}</p>
      {valor ? (
        <p
          className={
            destacado ? "mt-1 text-4xl font-bold text-accent" : "mt-1 text-3xl font-semibold"
          }
        >
          {valor}
        </p>
      ) : (
        <p className="mt-1 text-2xl font-semibold text-muted-foreground">—</p>
      )}
      <p className="mt-1 text-xs text-muted-foreground">{nota}</p>
    </div>
  );
}

/**
 * Quita el sufijo entre paréntesis del nombre oficial.
 *
 * En el PDF del DEMRE los nombres vienen como "ARQUITECTURA (23)", donde el
 * número es una nota al pie de la tabla original. Fuera de esa tabla no
 * significa nada y en un título se lee como un error.
 */
function limpiar(nombre: string): string {
  return nombreLegible(nombre.replace(/\s*\(\d+\)\s*$/, "")).trim();
}
