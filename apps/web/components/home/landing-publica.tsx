import Link from "next/link";
import type { ContentStats } from "@/lib/api";
import { GoogleButton } from "@/components/auth/google-button";
import { TituloRotativo } from "@/components/home/titulo-rotativo";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { Reveal } from "@/components/motion/reveal";
import { Planes } from "@/components/home/planes";
import { SiteFooter } from "@/components/site-footer";
import { diasHastaPaes } from "@/lib/paes-fecha";

/** Portada para visitantes sin sesión: nombre, entrada y qué ofrece el sitio. */

const FEATURES = [
  {
    title: "Modo Ensayo",
    description:
      "Arma el ensayo a tu medida: elige los ejes, cuántas preguntas y el ritmo. El tiempo es proporcional al de la prueba real, y tus respuestas se guardan solas.",
    icon: TimerIcon,
    badgeClass: "bg-accent/10 text-accent",
  },
  {
    title: "Puntaje estimado y resolución",
    description:
      "Al terminar ves tu puntaje en escala 100-1000, el desglose por eje y dificultad, y el desarrollo paso a paso de cada ejercicio.",
    icon: TargetIcon,
    badgeClass: "bg-success/10 text-success",
  },
  {
    title: "Primero aprender, después practicar",
    description:
      "Cada tema de Matemática M1 trae su lección: las propiedades que hay que saber, un ejercicio resuelto donde cada paso explica por qué se hace, y el error en el que cae casi todo el mundo.",
    icon: TreeIcon,
    badgeClass: "bg-accent/10 text-accent",
  },
  {
    title: "Mi meta: la carrera, no el puntaje",
    description:
      "Arma tu lista de hasta 10 preferencias y mira cuánto te falta en cada una, con las ponderaciones oficiales del DEMRE de 1.855 carreras. Sabes dónde rinde más cada hora de estudio.",
    icon: TargetIcon,
    badgeClass: "bg-accent-warm/10 text-accent-warm-strong",
  },
  {
    title: "Árbol de Habilidades",
    description:
      "El temario como nodos que desbloqueas a medida que dominas cada tema, con los prerrequisitos dibujados: 47 nodos entre las cinco pruebas.",
    icon: TreeIcon,
    badgeClass: "bg-warning/10 text-warning",
  },
  {
    title: "Tu progreso en el tiempo",
    description:
      "Historial de todos tus ensayos con la evolución del puntaje, tu mejor marca, el promedio y cuánto subiste respecto del ensayo anterior.",
    icon: ChartIcon,
    badgeClass: "bg-accent-2/10 text-accent-2",
  },
] as const;

const DATOS = [
  { label: "Tiempo real de la prueba", icon: ClockIcon },
  { label: "Puntaje en escala 100–1000", icon: TargetIcon },
  { label: "Gratis mientras estamos en beta", icon: SparkIcon },
] as const;

// Las cinco pruebas, en el orden en que las rinde un postulante. Rotan dentro
// del titular; la primera es la que ve quien no tiene JavaScript.
const PRUEBAS_ROTATIVAS = [
  "Competencia Lectora",
  "Matemática M1",
  "Matemática M2",
  "Ciencias",
  "Historia",
];

const PASOS = [
  {
    title: "Elige tu ensayo",
    description:
      "Qué prueba, qué ejes practicar, cuántas preguntas y a qué ritmo. Tú decides el formato.",
  },
  {
    title: "Ríndelo con tiempo real",
    description:
      "El cronómetro respeta la misma proporción minutos/pregunta que la prueba oficial DEMRE.",
  },
  {
    title: "Revisa y refuerza",
    description:
      "Puntaje estimado, desglose por eje y la resolución paso a paso de cada pregunta que fallaste.",
  },
] as const;

const CONFIANZA = [
  {
    title: "Puntaje con tablas oficiales",
    description:
      "La conversión a escala 100-1000 usa las tablas de transformación publicadas por el DEMRE para cada prueba, no una fórmula inventada.",
    icon: TargetIcon,
  },
  {
    title: "Tiempo real de cada prueba",
    description:
      "El cronómetro respeta la razón oficial minutos/pregunta de cada prueba: Competencia Lectora son 65 preguntas en 150 min; M1, 65 en 140; M2, 55 en 140; Ciencias, 80 en 160; Historia, 65 en 120.",
    icon: ClockIcon,
  },
  {
    title: "Sin letra chica",
    description:
      "Estamos en beta: todo lo que ves hoy es gratis, y sumamos preguntas y funciones nuevas cada semana.",
    icon: SparkIcon,
  },
] as const;

export function LandingPublica({
  stats,
  pagoDisponible = false,
}: {
  stats: ContentStats | null;
  pagoDisponible?: boolean;
}) {
  return (
    <main className="flex flex-1 flex-col">
      <section className="hero-glow relative overflow-hidden px-6 pt-24 pb-24 sm:pt-28">
        <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[26rem]" />

        <div className="relative mx-auto grid max-w-6xl grid-cols-1 items-center gap-16 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="flex flex-col items-center gap-6 text-center lg:items-start lg:text-left">
            <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
              PAES · Las cinco pruebas · Admisión 2027
            </span>

            <h1 className="text-5xl font-bold tracking-tight text-balance sm:text-6xl">
              Ensayos de{" "}
              <TituloRotativo palabras={PRUEBAS_ROTATIVAS} />
            </h1>

            <p className="max-w-xl text-balance text-lg font-medium text-foreground sm:text-xl">
              La PAES se acerca. Prepárate con datos reales, no con
              suposiciones.
            </p>

            <p className="max-w-xl text-balance text-muted">
              Con el tiempo real de cada prueba, tu puntaje estimado según las
              tablas oficiales del DEMRE y la resolución paso a paso de cada
              ejercicio. Practica, mide y mejora.
            </p>

            <ul className="flex flex-wrap justify-center gap-2 lg:justify-start">
              {DATOS.map((dato) => (
                <li
                  key={dato.label}
                  className="flex items-center gap-1.5 rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground"
                >
                  <dato.icon className="text-accent" />
                  {dato.label}
                </li>
              ))}
            </ul>

            <div className="mt-2 flex flex-col items-center gap-3 lg:items-start">
              <Link
                href="/registro"
                className="btn-glow rounded-xl px-8 py-3.5 text-base font-semibold text-accent-foreground"
              >
                Empezar mi primer ensayo →
              </Link>
              <div className="flex items-center gap-3 self-stretch text-xs text-muted">
                <span className="h-px flex-1 bg-border" />
                o
                <span className="h-px flex-1 bg-border" />
              </div>
              <GoogleButton redirectTo="/examen" />
              <p className="text-sm text-muted">
                <Link
                  href="/demo"
                  className="font-medium text-accent underline-offset-4 hover:underline"
                >
                  Pruébalo sin cuenta
                </Link>
                {" · "}
                <Link
                  href="/login"
                  className="underline-offset-4 hover:text-foreground hover:underline"
                >
                  Ya tengo cuenta
                </Link>
              </p>
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-sm lg:mx-0">
            <PuntajeMockup />
          </div>
        </div>
      </section>

      <FranjaCifras stats={stats} />

      <section id="como-funciona" className="border-t border-border px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mx-auto max-w-lg text-center">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Así funciona
            </h2>
            <p className="mt-3 text-sm text-muted">
              Sin vueltas: armas tu ensayo, lo rindes y sabes exactamente qué
              reforzar.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
            {PASOS.map((paso, i) => (
              <div key={paso.title} className="flex flex-col items-center text-center sm:items-start sm:text-left">
                <span
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-accent-foreground"
                  style={{
                    background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
                  }}
                >
                  {i + 1}
                </span>
                <h3 className="mt-4 text-sm font-semibold text-foreground">
                  {paso.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">
                  {paso.description}
                </p>
              </div>
            ))}
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
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-lg ${feature.badgeClass}`}
                >
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

      <section className="border-t border-border bg-surface/50 px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mx-auto max-w-lg text-center">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Hecho con los datos reales de la PAES
            </h2>
            <p className="mt-3 text-sm text-muted">
              Nada de fórmulas inventadas: el puntaje y los tiempos salen de
              lo que publica el DEMRE.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {CONFIANZA.map((item) => (
              <div
                key={item.title}
                className="rounded-xl border border-border bg-background p-5"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <item.icon />
                </div>
                <h3 className="mt-3 text-sm font-semibold text-foreground">
                  {item.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Lo que necesitas saber ──────────────────────────────────── */}
      <section className="border-t border-border px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mx-auto max-w-lg text-center">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Lo que necesitas saber de la PAES
            </h2>
            <p className="mt-3 text-sm text-muted">
              Los datos oficiales de las cinco pruebas, según el temario del
              DEMRE. El tiempo de tu ensayo se calcula con esta proporción.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {PRUEBAS_INFO.map((prueba) => (
              <div
                key={prueba.nombre}
                className="card-hover rounded-xl border border-border bg-surface p-6"
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="font-semibold text-foreground">{prueba.nombre}</h3>
                  <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent">
                    Disponible
                  </span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {prueba.descripcion}
                </p>
                <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-border pt-4 text-sm">
                  <div>
                    <dt className="text-xs text-muted">Preguntas</dt>
                    <dd className="font-semibold tabular-nums">{prueba.preguntas}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted">Duración oficial</dt>
                    <dd className="font-semibold">{prueba.duracion}</dd>
                  </div>
                </dl>
              </div>
            ))}
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {DATOS_PAES.map((dato) => (
              <div
                key={dato.title}
                className="rounded-xl border border-border bg-surface p-5"
              >
                <h3 className="text-sm font-semibold text-foreground">
                  {dato.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">
                  {dato.description}
                </p>
              </div>
            ))}
          </div>

          <p className="mt-8 text-center text-sm text-muted">
            ¿Te quedan dudas sobre cómo funciona la plataforma?{" "}
            <Link
              href="/preguntas-frecuentes"
              className="font-medium text-accent hover:underline"
            >
              Mira las preguntas frecuentes
            </Link>
            .
          </p>
        </div>
      </section>

      {/* ── Cierre motivacional ─────────────────────────────────────── */}
      <CierreMotivacional />

      <Planes pagoDisponible={pagoDisponible} />

      <SiteFooter />
    </main>
  );
}

/** Datos oficiales de cada prueba, tomados del temario DEMRE. */
const PRUEBAS_INFO = [
  {
    nombre: "Competencia Lectora",
    descripcion:
      "Obligatoria para todos: textos literarios, no literarios y discontinuos, con preguntas de localizar, interpretar y evaluar.",
    preguntas: "65",
    duracion: "2 h 30 min",
  },
  {
    nombre: "Competencia Matemática M1",
    descripcion:
      "La prueba base de matemática: cubre el temario de 7° básico a 2° medio. La rinden todas las carreras que piden matemática.",
    preguntas: "65",
    duracion: "2 h 20 min",
  },
  {
    nombre: "Competencia Matemática M2",
    descripcion:
      "Evalúa todo lo de M1 más contenido avanzado de 3° y 4° medio. La piden carreras científicas, de ingeniería y de salud.",
    preguntas: "55",
    duracion: "2 h 20 min",
  },
  {
    nombre: "Ciencias",
    descripcion:
      "Módulo común de Biología, Física y Química más un módulo electivo. Es la prueba más larga de las cinco.",
    preguntas: "80",
    duracion: "2 h 40 min",
  },
  {
    nombre: "Historia y Ciencias Sociales",
    descripcion:
      "Historia, formación ciudadana y economía. Evalúa sobre todo análisis de fuentes: tablas, textos y datos.",
    preguntas: "65",
    duracion: "2 h",
  },
] as const;

const DATOS_PAES = [
  {
    title: "Cada prueba, sus ejes",
    description:
      "Matemática se divide en Números, Álgebra y funciones, Geometría, y Probabilidad; Lectora en localizar, interpretar y evaluar. Tu resultado se desglosa por cada eje.",
  },
  {
    title: "Puntaje de 100 a 1000",
    description:
      "La conversión desde tus respuestas correctas no es lineal: depende de la tabla oficial de cada aplicación.",
  },
  {
    title: "Equivocarse no descuenta",
    description:
      "Las respuestas incorrectas no restan puntaje, así que siempre conviene contestar todas las preguntas.",
  },
] as const;

/** Banda de cierre: recuerda cuánto falta para la prueba y empuja a empezar. */
function CierreMotivacional() {
  const dias = diasHastaPaes();

  return (
    <section className="hero-glow relative overflow-hidden border-t border-border px-6 py-20">
      <div className="relative mx-auto max-w-2xl text-center">
        {dias !== null && (
          <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
            Faltan {dias} {dias === 1 ? "día" : "días"} para la PAES
          </span>
        )}
        <h2 className="mt-4 text-3xl font-bold tracking-tight text-balance sm:text-4xl">
          El puntaje no se decide el día de la prueba
        </h2>
        <p className="mt-4 text-balance leading-relaxed text-muted">
          Se decide en los meses de antes, en cada ejercicio que entendiste de
          verdad en vez de dejar pasar. Empieza hoy con un ensayo y descubre
          exactamente en qué estás parado.
        </p>
        <Link
          href="/registro"
          className="btn-glow mt-8 inline-flex rounded-lg px-8 py-3.5 text-base font-semibold text-accent-foreground transition-transform hover:-translate-y-0.5"
        >
          Empezar gratis →
        </Link>
        <p className="mt-3 text-xs text-muted">
          Sin tarjeta. Sin compromiso. Toma un minuto.
        </p>
      </div>
    </section>
  );
}

const EJES_EJEMPLO = [
  { nombre: "Números", valor: 82, colorVar: "var(--accent)" },
  { nombre: "Álgebra y funciones", valor: 74, colorVar: "var(--accent-2)" },
  { nombre: "Geometría", valor: 65, colorVar: "var(--success)" },
  { nombre: "Probabilidad", valor: 58, colorVar: "var(--warning)" },
] as const;

/** Vista previa ilustrativa del resultado de un ensayo (no son datos reales). */
/**
 * Cifras del banco, contadas en la base al momento de servir la página.
 *
 * Nada de "más de 500 ejercicios": el número que se muestra es el que hay. Si
 * la API no respondió, la franja no se dibuja — un dato de menos es preferible
 * a uno inflado, sobre todo en la única página que promete que acá no se
 * inventan datos.
 */
function FranjaCifras({ stats }: { stats: ContentStats | null }) {
  if (!stats) return null;

  const cifras = [
    { valor: stats.questions, etiqueta: "preguntas verificadas" },
    { valor: stats.subjects, etiqueta: "pruebas PAES" },
    { valor: stats.skill_nodes, etiqueta: "temas en el árbol" },
    { valor: stats.passages, etiqueta: "textos de lectura" },
  ];

  return (
    <section
      className="border-t border-border bg-surface/60 px-6 py-10"
      aria-label="Cifras del banco de preguntas"
    >
      <Reveal>
        <dl className="mx-auto grid max-w-4xl grid-cols-2 gap-6 sm:grid-cols-4">
          {cifras.map((c) => (
            <div key={c.etiqueta} className="text-center">
              <dt className="sr-only">{c.etiqueta}</dt>
              <dd>
                <span className="block text-3xl font-bold tracking-tight tabular-nums sm:text-4xl">
                  <NumeroAnimado valor={c.valor} />
                </span>
                <span className="mt-1 block text-xs text-muted sm:text-sm">
                  {c.etiqueta}
                </span>
              </dd>
            </div>
          ))}
        </dl>
      </Reveal>
    </section>
  );
}

function PuntajeMockup() {
  const radio = 46;
  const circunferencia = 2 * Math.PI * radio;
  const progreso = 0.78;

  return (
    <div className="relative">
      <div className="float-chip absolute -top-4 -right-3 z-10 flex items-center gap-1.5 rounded-full border border-success/30 bg-background px-3 py-1.5 text-xs font-semibold text-success shadow-lg shadow-foreground/5 sm:-right-6">
        <UpIcon />
        +38 pts vs. tu último ensayo
      </div>

      <div className="rounded-2xl border border-border bg-surface p-6 shadow-xl shadow-foreground/5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted">
            Resultado de ejemplo
          </span>
          <span className="rounded-full bg-surface-hover px-2 py-0.5 text-[11px] text-muted">
            Ensayo #4
          </span>
        </div>

        <div className="mt-5 flex items-center gap-5">
          <svg width="104" height="104" viewBox="0 0 104 104" className="shrink-0 -rotate-90">
            <circle cx="52" cy="52" r={radio} fill="none" stroke="var(--border)" strokeWidth="8" />
            <circle
              cx="52"
              cy="52"
              r={radio}
              fill="none"
              stroke="var(--accent)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circunferencia}
              strokeDashoffset={circunferencia * (1 - progreso)}
            />
          </svg>
          <div>
            <p className="text-3xl font-bold tracking-tight text-foreground">
              780<span className="text-base font-medium text-muted">/1000</span>
            </p>
            <p className="text-xs text-muted">Puntaje estimado</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3">
          {EJES_EJEMPLO.map((eje) => (
            <div key={eje.nombre}>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-foreground">{eje.nombre}</span>
                <span className="text-muted">{eje.valor}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-hover">
                <div
                  className="h-full rounded-full"
                  style={{ width: `${eje.valor}%`, background: eje.colorVar }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
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

function TargetIcon({ className }: { className?: string }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className}>
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

function ClockIcon({ className }: { className?: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.5 2" />
    </svg>
  );
}

function SparkIcon({ className }: { className?: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className={className}>
      <path d="M12 2l1.8 5.6L19.5 9l-5.7 1.4L12 16l-1.8-5.6L4.5 9l5.7-1.4z" />
    </svg>
  );
}

function UpIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 15l6-6 6 6" />
    </svg>
  );
}
