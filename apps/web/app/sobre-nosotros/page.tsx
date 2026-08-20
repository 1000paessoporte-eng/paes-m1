import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Quiénes somos",
  description:
    "Qué es 1000paes, en qué creemos y cómo construimos una plataforma de preparación PAES basada en los datos oficiales del DEMRE.",
  alternates: { canonical: "/sobre-nosotros" },
};

/**
 * Página "Quiénes somos".
 *
 * IMPORTANTE: todo lo que se afirma acá tiene que ser verificable. No hay
 * fechas de fundación, tamaño de equipo, cantidad de usuarios ni testimonios,
 * porque inventarlos sería prometerle algo falso a un estudiante que está
 * decidiendo dónde preparar una prueba que le importa. Cuando existan datos
 * reales (equipo, trayectoria, resultados), este es el lugar para agregarlos.
 */

const PRINCIPIOS = [
  {
    title: "Los números salen de la fuente oficial",
    description:
      "La conversión a puntaje 100-1000 usa las tablas de transformación que publica el DEMRE para cada prueba, y los tiempos respetan la razón oficial de minutos por pregunta de cada temario. Cuando algo es una estimación, lo decimos: nunca presentamos un número como si fuera tu puntaje real.",
    icon: TargetIcon,
  },
  {
    title: "Equivocarse tiene que enseñar algo",
    description:
      "Marcar una respuesta como incorrecta no ayuda a nadie. Cada pregunta trae el desarrollo completo de por qué la respuesta correcta lo es, paso a paso, y cada alternativa incorrecta está diseñada a partir de un error conceptual concreto que los estudiantes cometen de verdad.",
    icon: BookIcon,
  },
  {
    title: "Estudiar con un orden, no al azar",
    description:
      "El temario no es una lista plana de temas sueltos. En el Árbol de Habilidades cada tema se apoya en los anteriores, así que siempre sabes qué conviene estudiar ahora y por qué, en vez de saltar de un ejercicio a otro sin criterio.",
    icon: TreeIcon,
  },
  {
    title: "Sin letra chica",
    description:
      "Hoy la plataforma es gratis y no pide tarjeta. Cuando existan planes de pago, los precios y lo que incluye cada uno se van a anunciar en la propia página antes de cobrar nada. Puedes borrar tus datos y descargar un respaldo cuando quieras.",
    icon: ShieldIcon,
  },
] as const;

export default function SobreNosotrosPage() {
  return (
    <>
      <main className="flex flex-1 flex-col">
        <section className="hero-glow relative overflow-hidden px-6 pt-20 pb-16">
          <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[20rem]" />
          <div className="relative mx-auto max-w-2xl">
            <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
              Quiénes somos
            </span>
            <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              Preparar la PAES no debería depender de cuánto puedas pagar
            </h1>
            <p className="mt-4 leading-relaxed text-muted">
              1000paes es una plataforma chilena para preparar la Prueba de
              Acceso a la Educación Superior. La construimos alrededor de una
              idea simple: un estudiante que practica debería terminar cada
              sesión sabiendo exactamente dos cosas —{" "}
              <strong className="text-foreground">
                en qué puntaje está parado hoy
              </strong>{" "}
              y{" "}
              <strong className="text-foreground">
                qué tiene que estudiar mañana
              </strong>
              . Todo lo que hay en la plataforma existe para responder esas dos
              preguntas.
            </p>
          </div>
        </section>

        <section className="border-t border-border px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-semibold tracking-tight">
              En qué creemos
            </h2>
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {PRINCIPIOS.map((p) => (
                <div
                  key={p.title}
                  className="rounded-xl border border-border bg-surface p-6"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
                    <p.icon />
                  </div>
                  <h3 className="mt-4 text-sm font-semibold text-foreground">
                    {p.title}
                  </h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted">
                    {p.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-border bg-surface/50 px-6 py-16">
          <div className="mx-auto max-w-2xl">
            <h2 className="text-2xl font-semibold tracking-tight">
              En qué estamos trabajando
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-muted">
              1000paes está en beta y crece cada semana. Estas son las cosas en
              las que estamos trabajando ahora mismo, para que sepas hacia dónde
              va la plataforma que estás usando:
            </p>
            <ul className="mt-6 flex flex-col gap-3 text-sm text-muted">
              {[
                "Ampliar el banco de preguntas de Competencia Matemática M1 y M2.",
                "Habilitar las otras tres pruebas: Competencia Lectora, Historia y Ciencias Sociales, y Ciencias.",
                "Recomendación automática del tema que más te conviene reforzar según tu propio historial.",
                "Panel para profesores y colegios, con el avance de un curso completo.",
              ].map((item) => (
                <li key={item} className="flex gap-2.5">
                  <span aria-hidden className="mt-0.5 shrink-0 text-accent">
                    <ArrowIcon />
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="border-t border-border px-6 py-16">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-2xl font-semibold tracking-tight">
              Empieza cuando quieras
            </h2>
            <p className="mt-3 text-sm text-muted">
              No necesitas tarjeta ni compromiso. Crea tu cuenta, rinde un
              ensayo y mira dónde estás parado.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Link
                href="/registro"
                className="btn-glow rounded-lg px-6 py-3 text-sm font-semibold text-accent-foreground"
              >
                Crear cuenta gratis →
              </Link>
              <Link
                href="/preguntas-frecuentes"
                className="rounded-lg border border-border px-6 py-3 text-sm font-medium transition-colors hover:bg-surface-hover"
              >
                Preguntas frecuentes
              </Link>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}

function TargetIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1" fill="currentColor" />
    </svg>
  );
}

function BookIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2V5z" />
      <path d="M8 7h7M8 11h7" />
    </svg>
  );
}

function TreeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="4" r="2" />
      <circle cx="6" cy="14" r="2" />
      <circle cx="18" cy="14" r="2" />
      <path d="M12 6v4M12 10L6 12M12 10l6 2" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l7 3v6c0 4-3 7.5-7 9-4-1.5-7-5-7-9V6l7-3z" />
      <path d="M9.5 12l2 2 3.5-4" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}
