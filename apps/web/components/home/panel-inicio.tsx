import Link from "next/link";
import { Planes } from "@/components/home/planes";
import type { AuthUserOut, ExamAttemptSummary } from "@/lib/api";
import { formatearTiempo } from "@/lib/tiempo";

/**
 * Portada para quien ya inició sesión: en vez de ofrecerle iniciar sesión de
 * nuevo, le muestra su estado y accesos a todo lo que hace la plataforma.
 */

const SECCIONES = [
  {
    href: "/examen",
    titulo: "Modo Ensayo",
    descripcion:
      "Arma un ensayo eligiendo ejes, cantidad de preguntas y ritmo, con el tiempo proporcional al de la prueba real.",
    accion: "Rendir un ensayo",
    principal: true,
    icon: TimerIcon,
  },
  {
    href: "/historial",
    titulo: "Mi progreso",
    descripcion:
      "Todos tus ensayos con la evolución del puntaje, tu mejor marca y cuánto subiste respecto del anterior.",
    accion: "Ver mi progreso",
    principal: false,
    icon: ChartIcon,
  },
  {
    href: "/arbol",
    titulo: "Árbol de Habilidades",
    descripcion:
      "El temario como nodos que se desbloquean a medida que dominas cada tema. Practica nodo por nodo.",
    accion: "Abrir el árbol",
    principal: false,
    icon: TreeIcon,
  },
  {
    href: "/analitica",
    titulo: "Analítica",
    descripcion:
      "Tiempo invertido y tasa de acierto en el tiempo, para saber dónde enfocar la próxima sesión.",
    accion: "Ver analítica",
    principal: false,
    icon: TargetIcon,
  },
] as const;

interface Props {
  user: AuthUserOut;
  attempts: ExamAttemptSummary[];
}

export function PanelInicio({ user, attempts }: Props) {
  const rendidos = attempts.filter((a) => a.status === "submitted");
  const puntajes = rendidos.map((a) => a.estimated_score ?? 0);
  const mejor = puntajes.length > 0 ? Math.max(...puntajes) : null;
  const ultimo = puntajes.length > 0 ? puntajes[0] : null;
  const enCurso = attempts.find((a) => a.status === "in_progress");
  const tiempoTotal = rendidos.reduce((acc, a) => acc + a.elapsed_seconds, 0);

  // Solo el nombre de pila: "Hola, Juan" se lee mejor que el nombre completo.
  const nombre = user.name.split(" ")[0];

  return (
    <main className="flex flex-1 flex-col">
      <section className="px-6 pt-16 pb-16 sm:pt-20">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-medium text-accent">
            Preparación PAES M1 · Admisión 2027
          </p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
            Hola, {nombre}
          </h1>
          <p className="mt-3 max-w-xl text-muted">
            {rendidos.length === 0
              ? "Todavía no rindes ningún ensayo. El primero te dará un puntaje estimado y te mostrará en qué ejes conviene reforzar."
              : "Este es tu panel. Retoma donde quedaste o arma un ensayo nuevo."}
          </p>

          {enCurso && (
            <div className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-accent/40 bg-accent/5 p-4">
              <p className="text-sm">
                Tienes un ensayo en curso sin finalizar. Al continuar retomas
                justo donde quedaste.
              </p>
              <Link
                href="/examen"
                className="btn-glow shrink-0 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground"
              >
                Continuar ensayo
              </Link>
            </div>
          )}

          {rendidos.length > 0 && (
            <dl className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Estadistica etiqueta="Mejor puntaje" valor={mejor} destacado />
              <Estadistica etiqueta="Último puntaje" valor={ultimo} />
              <Estadistica etiqueta="Ensayos rendidos" valor={rendidos.length} />
              <Estadistica
                etiqueta="Tiempo practicado"
                texto={formatearTiempo(tiempoTotal)}
              />
            </dl>
          )}
        </div>
      </section>

      {/* ── Todo lo que puedes hacer ────────────────────────────────── */}
      <section className="border-t border-border px-6 py-16">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-2xl font-semibold tracking-tight">
            Todo lo que puedes hacer
          </h2>

          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {SECCIONES.map((s) => (
              <Link
                key={s.href}
                href={s.href}
                className={
                  s.principal
                    ? "card-hover group flex flex-col rounded-xl border border-accent/50 bg-accent/5 p-6"
                    : "card-hover group flex flex-col rounded-xl border border-border bg-surface p-6"
                }
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-background text-accent">
                  <s.icon />
                </div>
                <h3 className="mt-4 font-semibold">{s.titulo}</h3>
                <p className="mt-1.5 flex-1 text-sm leading-relaxed text-muted">
                  {s.descripcion}
                </p>
                <span className="mt-4 text-sm font-medium text-accent group-hover:underline">
                  {s.accion} →
                </span>
              </Link>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap gap-3 text-sm">
            <Link
              href="/perfil"
              className="rounded-lg border border-border px-4 py-2 font-medium transition-colors hover:bg-surface-hover"
            >
              Mi perfil
            </Link>
            <Link
              href="#planes"
              className="rounded-lg border border-border px-4 py-2 font-medium transition-colors hover:bg-surface-hover"
            >
              Ver los planes
            </Link>
          </div>
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
        </div>
      </footer>
    </main>
  );
}

function Estadistica({
  etiqueta,
  valor,
  texto,
  destacado = false,
}: {
  etiqueta: string;
  valor?: number | null;
  texto?: string;
  destacado?: boolean;
}) {
  return (
    <div
      className={
        destacado
          ? "rounded-xl border border-accent/40 bg-accent/5 p-4"
          : "rounded-xl border border-border bg-surface p-4"
      }
    >
      <dt className="text-xs text-muted">{etiqueta}</dt>
      <dd className="mt-0.5 text-2xl font-bold tabular-nums">
        {texto ?? valor ?? "—"}
      </dd>
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
