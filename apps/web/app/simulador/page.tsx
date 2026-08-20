import type { Metadata } from "next";
import { DatosEstructurados } from "@/components/datos-estructurados";
import { SimuladorMultiple } from "@/components/carreras/simulador-multiple";
import { SiteFooter } from "@/components/site-footer";

/**
 * "¿Cuánto me falta para mi carrera?", sin cuenta.
 *
 * Es Mi meta abierto. La ficha de una carrera ya trae su simulador, pero
 * responde por UNA, y nadie postula a una sola: la pregunta real es cuál de
 * todas está más cerca. Eso exige escribir los puntajes una vez y comparar, y
 * hasta ahora solo se podía con cuenta.
 *
 * Es lo único que este producto tiene y la competencia no: las 1.855
 * ponderaciones oficiales del DEMRE cruzadas con el puntaje real de la
 * persona. Tenerlo detrás del login era esconder el argumento para quedarse.
 */
export const metadata: Metadata = {
  title: "Simulador de puntaje ponderado PAES",
  description:
    "Calcula tu puntaje ponderado en varias carreras a la vez con las ponderaciones oficiales del DEMRE, y mira cuánto te falta en cada una. Gratis y sin cuenta.",
  alternates: { canonical: "/simulador" },
};

export default function SimuladorPage() {
  return (
    <>
      <main className="flex flex-1 flex-col">
        <section className="hero-glow relative overflow-hidden px-6 pt-20 pb-10">
          <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[16rem]" />
          <div className="relative mx-auto max-w-3xl">
            <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
              Gratis y sin cuenta
            </span>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-balance sm:text-4xl">
              ¿Cuánto te falta para tu carrera?
            </h1>
            <p className="mt-3 text-lg text-muted">
              Escribe tus puntajes una vez, arma tu lista de carreras y mira en
              cuál estás más cerca. Con las ponderaciones oficiales del DEMRE.
            </p>
            <p className="mt-3 text-xs text-muted">
              El cálculo corre en tu navegador y tus puntajes no salen de él.
            </p>
          </div>
        </section>

        <section className="px-6 pb-20">
          <div className="mx-auto max-w-3xl">
            <SimuladorMultiple />
          </div>
        </section>
      </main>
      <SiteFooter />

      <DatosEstructurados
        datos={{
          "@context": "https://schema.org",
          "@type": "WebApplication",
          name: "Simulador de puntaje ponderado PAES",
          applicationCategory: "EducationalApplication",
          inLanguage: "es-CL",
          isAccessibleForFree: true,
          offers: { "@type": "Offer", price: "0", priceCurrency: "CLP" },
        }}
      />
    </>
  );
}
