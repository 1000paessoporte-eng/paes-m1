import Link from "next/link";
import { GoogleButton } from "@/components/auth/google-button";
import { Planes } from "@/components/home/planes";

/** Portada para visitantes sin sesión: nombre, entrada y qué ofrece el sitio. */

const FEATURES = [
  {
    title: "Modo Ensayo",
    description:
      "Arma el ensayo a tu medida: elige los ejes, cuántas preguntas y el ritmo. El tiempo es proporcional al de la prueba real, y tus respuestas se guardan solas.",
    icon: TimerIcon,
  },
  {
    title: "Puntaje estimado y resolución",
    description:
      "Al terminar ves tu puntaje en escala 100-1000, el desglose por eje y dificultad, y el desarrollo paso a paso de cada ejercicio.",
    icon: TargetIcon,
  },
  {
    title: "Árbol de Habilidades",
    description:
      "El temario completo como nodos que desbloqueas a medida que dominas cada tema: Números, Álgebra, Geometría y Probabilidad.",
    icon: TreeIcon,
  },
  {
    title: "Tu progreso en el tiempo",
    description:
      "Historial de todos tus ensayos con la evolución del puntaje, tu mejor marca, el promedio y cuánto subiste respecto del ensayo anterior.",
    icon: ChartIcon,
  },
] as const;

export function LandingPublica() {
  return (
    <main className="flex flex-1 flex-col">
      <section className="px-6 pt-24 pb-24 sm:pt-32">
        <div className="mx-auto flex max-w-3xl flex-col items-center gap-6 text-center">
          <span className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted">
            PAES M1 · Competencia Matemática · Admisión 2027
          </span>

          <h1 className="text-6xl font-bold tracking-tight text-balance text-accent sm:text-8xl">
            milpaes
          </h1>

          <p className="max-w-xl text-balance text-muted sm:text-lg">
            Ensayos de matemática con el tiempo real de la prueba, tu puntaje
            estimado y la resolución de cada ejercicio. Practica, mide y mejora.
          </p>

          <div className="mt-2 flex flex-col items-center gap-4">
            <GoogleButton redirectTo="/examen" />
            <Link
              href="/login"
              className="btn-glow rounded-lg px-6 py-3 text-sm font-medium text-accent-foreground transition-all"
            >
              Iniciar sesión
            </Link>
            <Link
              href="/registro"
              className="text-sm text-muted underline-offset-4 hover:text-foreground hover:underline"
            >
              Crear una cuenta nueva
            </Link>
            <Link
              href="/demo"
              className="text-sm font-medium text-accent underline-offset-4 hover:underline"
            >
              Pruébalo sin cuenta →
            </Link>
          </div>
        </div>
      </section>

      <section id="ofrecemos" className="border-t border-border px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mx-auto max-w-lg text-center">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Lo que ofrecemos
            </h2>
            <p className="mt-3 text-sm text-muted">
              Cuatro herramientas que trabajan juntas para convertir cada
              pregunta que respondes en una decisión sobre qué estudiar después.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="card-hover rounded-xl border border-border bg-surface p-6"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-hover text-accent">
                  <feature.icon />
                </div>
                <h3 className="mt-4 text-sm font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>

          <p className="mt-10 text-center text-sm text-muted">
            Para rendir un ensayo necesitas una cuenta.{" "}
            <Link href="/registro" className="font-medium text-accent hover:underline">
              Créala en un minuto
            </Link>
            .
          </p>
        </div>
      </section>

      <Planes />

      <footer className="border-t border-border px-6 py-10">
        <div className="mx-auto max-w-5xl text-center text-xs leading-relaxed text-muted">
          <p>
            milpaes no tiene relación con el DEMRE. El puntaje mostrado es una
            estimación referencial: el puntaje real depende de la forma rendida
            y del proceso de admisión.
          </p>
          <p className="mt-3">
            <Link href="/terminos" className="hover:text-foreground hover:underline">
              Términos
            </Link>{" "}
            ·{" "}
            <Link href="/privacidad" className="hover:text-foreground hover:underline">
              Privacidad
            </Link>
          </p>
        </div>
      </footer>
    </main>
  );
}

function TreeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="4" r="2" />
      <circle cx="6" cy="14" r="2" />
      <circle cx="18" cy="14" r="2" />
      <circle cx="6" cy="20.5" r="1.5" />
      <circle cx="18" cy="20.5" r="1.5" />
      <path d="M12 6v4M12 10L6 12M12 10l6 2M6 16v2.5M18 16v2.5" />
    </svg>
  );
}

function TimerIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="13" r="8" />
      <path d="M12 9v4l3 2M9 2h6M12 2v2" />
    </svg>
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

function ChartIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 20V10M12 20V4M20 20v-7" />
    </svg>
  );
}
