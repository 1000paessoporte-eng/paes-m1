import Link from "next/link";

const FEATURES = [
  {
    title: "Árbol de Habilidades",
    description:
      "El temario completo (Números, Álgebra, Geometría, Probabilidad) como nodos que desbloqueas a medida que dominas cada tema, no un índice estático.",
    icon: TreeIcon,
  },
  {
    title: "Modo Examen Focus",
    description:
      "Simulacro real de 2h 20m, atajos de teclado y guardado continuo. Medimos tu ritmo pregunta a pregunta para detectar fatiga antes del error.",
    icon: TimerIcon,
  },
  {
    title: "Smart Feedback",
    description:
      "Cada alternativa incorrecta trae la razón exacta del error conceptual, con rutas de nivelación directas a tus nodos más débiles.",
    icon: TargetIcon,
  },
  {
    title: "Dashboard Analítico",
    description:
      "Tiempo invertido vs. tasa de acierto y rachas de práctica diaria, para que sepas exactamente dónde enfocar la próxima sesión.",
    icon: ChartIcon,
  },
] as const;

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col">
      <section className="bg-grid-fade relative overflow-hidden px-6 pt-24 pb-20 sm:pt-32 sm:pb-28">
        <div
          aria-hidden
          className="pointer-events-none absolute left-1/2 top-0 -z-10 h-[420px] w-[720px] -translate-x-1/2 rounded-full opacity-30 blur-[110px]"
          style={{
            background:
              "radial-gradient(closest-side, var(--accent), var(--accent-2), transparent)",
          }}
        />

        <div className="mx-auto flex max-w-3xl flex-col items-center gap-6 text-center">
          <span className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted">
            PAES M1 · Competencia Matemática
          </span>
          <h1 className="text-4xl font-semibold tracking-tight text-balance sm:text-6xl">
            Domina la M1 con un{" "}
            <span className="text-gradient">árbol de habilidades</span> que
            se adapta a ti
          </h1>
          <p className="max-w-xl text-balance text-muted sm:text-lg">
            Modo examen de alto rendimiento, autopsia del error pregunta a
            pregunta y un dashboard que muestra exactamente dónde enfocar tu
            estudio.
          </p>
          <div className="mt-2 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/arbol"
              className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground transition-all"
            >
              Empezar ahora
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:border-border-strong hover:bg-surface-hover"
            >
              Iniciar sesión
            </Link>
          </div>
        </div>
      </section>

      <section className="border-t border-border px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mx-auto max-w-lg text-center">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Todo lo que una plataforma tradicional no tiene
            </h2>
            <p className="mt-3 text-sm text-muted">
              Cuatro sistemas que trabajan juntos para convertir cada
              pregunta que respondes en una decisión sobre qué estudiar
              después.
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
        </div>
      </section>
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
