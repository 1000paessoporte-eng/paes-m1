import type { Metadata } from "next";
import Link from "next/link";
import { DatosEstructurados } from "@/components/datos-estructurados";
import { SiteFooter } from "@/components/site-footer";
import { getLecciones, type LeccionIndice, type Subject } from "@/lib/api";
import { COLOR_PRUEBA } from "@/lib/colores-prueba";

/**
 * El índice de lecciones.
 *
 * Existe por la misma razón que /carreras: sin una página que las enlace,
 * Google no llega a las lecciones por más que estén en el sitemap, y una
 * persona tampoco. Es además la única página del sitio que se puede compartir
 * con un profesor sin que pida cuenta.
 */
export const revalidate = 86400;

export const metadata: Metadata = {
  title: "Lecciones del temario PAES",
  description:
    "La teoría de cada tema del temario PAES: las propiedades que hay que saber, un ejercicio resuelto donde cada paso explica por qué se hace, y el error en el que cae casi todo el mundo. Gratis y sin cuenta.",
  alternates: { canonical: "/aprender" },
};

const NOMBRE_PRUEBA: Record<string, string> = {
  lectora: "Competencia Lectora",
  m1: "Competencia Matemática M1",
  m2: "Competencia Matemática M2",
  ciencias: "Ciencias",
  historia: "Historia y Ciencias Sociales",
};

export default async function AprenderIndicePage() {
  // Si la API no responde, la página lo dice en vez de mostrarse vacía como si
  // no hubiera lecciones. Mismo criterio que el índice de carreras.
  let lecciones: LeccionIndice[] = [];
  try {
    lecciones = await getLecciones();
  } catch {
    lecciones = [];
  }

  // Agrupadas por prueba y, dentro, por eje: es el orden del temario, que es
  // como el estudiante busca ("álgebra de M1"), no el orden de la base.
  const porPrueba = new Map<string, Map<string, LeccionIndice[]>>();
  for (const l of lecciones) {
    const ejes = porPrueba.get(l.subject) ?? new Map<string, LeccionIndice[]>();
    ejes.set(l.axis_label, [...(ejes.get(l.axis_label) ?? []), l]);
    porPrueba.set(l.subject, ejes);
  }

  return (
    <>
      <main className="flex flex-1 flex-col">
        <section className="hero-glow relative overflow-hidden px-6 pt-20 pb-12">
          <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[18rem]" />
          <div className="relative mx-auto max-w-3xl">
            <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
              Gratis y sin cuenta
            </span>
            <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              {lecciones.length > 0
                ? `${lecciones.length} lecciones del temario PAES`
                : "Lecciones del temario PAES"}
            </h1>
            <p className="mt-3 text-lg text-muted">
              Cada tema trae las propiedades que hay que saber, un ejercicio
              resuelto donde cada paso explica <em>por qué</em> se hace, y el
              error en el que cae casi todo el mundo.
            </p>
          </div>
        </section>

        <section className="px-6 pb-20">
          <div className="mx-auto max-w-3xl">
            {lecciones.length === 0 && (
              <p className="rounded-lg border border-border bg-surface p-4 text-sm text-muted">
                No pudimos cargar el listado en este momento. Vuelve a
                intentarlo en unos minutos: las lecciones están, es la conexión
                la que falló.
              </p>
            )}

            {[...porPrueba.entries()].map(([subject, ejes]) => (
              // Cada prueba con SU color, el mismo del árbol, del ensayo y
              // del titular de la portada. Las cinco secciones eran títulos
              // negros idénticos sobre listas grises idénticas: con 53
              // lecciones en una sola página, saber de un vistazo dónde
              // empieza y termina cada prueba es la mitad del trabajo.
              <div key={subject} className="mt-10 first:mt-0">
                <h2 className="flex items-center gap-2.5 text-xl font-semibold tracking-tight">
                  <span
                    aria-hidden
                    className="h-5 w-1.5 shrink-0 rounded-full"
                    style={{
                      backgroundColor:
                        COLOR_PRUEBA[subject as Subject] ?? "var(--accent)",
                    }}
                  />
                  {NOMBRE_PRUEBA[subject] ?? subject}
                </h2>
                {[...ejes.entries()].map(([eje, items]) => (
                  <div key={eje} className="mt-5">
                    <h3 className="text-xs font-semibold tracking-wide text-muted uppercase">
                      {eje}
                    </h3>
                    <ul className="mt-2 grid gap-2 sm:grid-cols-2">
                      {items.map((l) => (
                        <li key={l.node_code}>
                          <Link
                            href={`/aprender/${l.node_code}`}
                            className="card-hover flex items-center justify-between gap-3 rounded-lg border border-border bg-surface p-3 text-sm"
                          >
                            <span className="min-w-0 flex-1">{l.node_name}</span>
                            <span
                              aria-hidden
                              className="shrink-0"
                              style={{
                                color:
                                  COLOR_PRUEBA[subject as Subject] ?? "var(--muted)",
                              }}
                            >
                              →
                            </span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ))}

            <div className="mt-12 rounded-xl border border-accent/40 bg-accent/5 p-6 text-center">
              <h2 className="font-semibold">Leer no basta</h2>
              <p className="mt-1.5 text-sm text-muted">
                Con una cuenta gratis practicas cada tema con corrección
                inmediata y rindes ensayos cronometrados como la prueba real.
              </p>
              <Link
                href="/registro"
                className="btn-glow mt-4 inline-flex rounded-lg px-6 py-3 text-sm font-semibold text-accent-foreground"
              >
                Empezar gratis →
              </Link>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />

      <DatosEstructurados
        datos={{
          "@context": "https://schema.org",
          "@type": "ItemList",
          name: "Lecciones del temario PAES",
          numberOfItems: lecciones.length,
          itemListElement: lecciones.map((l, i) => ({
            "@type": "ListItem",
            position: i + 1,
            name: l.node_name,
            url: `https://1000paes.cl/aprender/${l.node_code}`,
          })),
        }}
      />
    </>
  );
}
