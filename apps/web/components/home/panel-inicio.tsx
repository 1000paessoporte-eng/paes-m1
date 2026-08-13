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
    badgeClass: "bg-accent/10 text-accent",
  },
  {
    href: "/historial",
    titulo: "Mi progreso",
    descripcion:
      "Todos tus ensayos con la evolución del puntaje, tu mejor marca y cuánto subiste respecto del anterior.",
    accion: "Ver mi progreso",
    principal: false,
    icon: ChartIcon,
    badgeClass: "bg-accent-2/10 text-accent-2",
  },
  {
    href: "/arbol",
    titulo: "Árbol de Habilidades",
    descripcion:
      "El temario como nodos que se desbloquean a medida que dominas cada tema. Practica nodo por nodo.",
    accion: "Abrir el árbol",
    principal: false,
    icon: TreeIcon,
    badgeClass: "bg-warning/10 text-warning",
  },
  {
    href: "/analitica",
    titulo: "Analítica",
    descripcion:
      "Tiempo invertido y tasa de acierto en el tiempo, para saber dónde enfocar la próxima sesión.",
    accion: "Ver analítica",
    principal: false,
    icon: TargetIcon,
    badgeClass: "bg-success/10 text-success",
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
  const anterior = puntajes.length > 1 ? puntajes[1] : null;
  const variacion = ultimo != null && anterior != null ? ultimo - anterior : null;
  const enCurso = attempts.find((a) => a.status === "in_progress");
  const tiempoTotal = rendidos.reduce((acc, a) => acc + a.elapsed_seconds, 0);
  const tieneDatos = rendidos.length > 0 && mejor != null && ultimo != null;

  // Solo el nombre de pila: "Hola, Juan" se lee mejor que el nombre completo.
  const nombre = user.name.split(" ")[0];

  return (
    <main className="flex flex-1 flex-col">
      <section className="hero-glow relative overflow-hidden px-6 pt-16 pb-16 sm:pt-20">
        <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[24rem]" />

        <div className="relative mx-auto max-w-5xl">
          <div
            className={
              tieneDatos
                ? "grid grid-cols-1 items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]"
                : "max-w-xl"
            }
          >
            <div>
              <p className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent inline-block">
                Preparación PAES · Admisión 2027
              </p>
              <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
                Hola,{" "}
                <span
                  className="bg-clip-text text-transparent"
                  style={{
                    backgroundImage:
                      "linear-gradient(135deg, var(--accent), var(--accent-2))",
                  }}
                >
                  {nombre}
                </span>
              </h1>
              <p className="mt-3 max-w-xl text-muted">
                {tieneDatos
                  ? "Este es tu panel. Retoma donde quedaste o arma un ensayo nuevo."
                  : "Todavía no rindes ningún ensayo. El primero te dará un puntaje estimado y te mostrará en qué ejes conviene reforzar."}
              </p>

              {enCurso && (
                <div className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-accent/40 bg-accent/5 p-4">
                  <p className="text-sm">
                    Tienes un ensayo en curso sin finalizar. Al continuar
                    retomas justo donde quedaste.
                  </p>
                  <Link
                    href="/examen"
                    className="btn-glow shrink-0 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground"
                  >
                    Continuar ensayo
                  </Link>
                </div>
              )}

              <Link
                href="/examen"
                className="btn-glow mt-6 inline-flex rounded-lg px-6 py-3 text-sm font-medium text-accent-foreground transition-transform hover:-translate-y-0.5"
              >
                {tieneDatos ? "Rendir un nuevo ensayo" : "Rendir tu primer ensayo"} →
              </Link>
            </div>

            {tieneDatos && (
              <div className="relative mx-auto w-full max-w-sm lg:mx-0">
                <ProgresoCard
                  mejor={mejor}
                  ultimo={ultimo}
                  variacion={variacion}
                  ensayos={rendidos.length}
                  tiempoTotal={tiempoTotal}
                />
              </div>
            )}
          </div>
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
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-lg ${s.badgeClass}`}
                >
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
            1000paes no tiene relación con el DEMRE. El puntaje mostrado es una
            estimación referencial: el puntaje real depende de la forma rendida
            y del proceso de admisión.
          </p>
        </div>
      </footer>
    </main>
  );
}

/** Tarjeta con el progreso real del estudiante: mismo lenguaje visual que la
 * tarjeta de ejemplo de la landing pública, pero con sus datos reales. */
function ProgresoCard({
  mejor,
  ultimo,
  variacion,
  ensayos,
  tiempoTotal,
}: {
  mejor: number;
  ultimo: number;
  variacion: number | null;
  ensayos: number;
  tiempoTotal: number;
}) {
  const radio = 46;
  const circunferencia = 2 * Math.PI * radio;
  // Escala del anillo sobre el rango real de puntaje PAES (100-1000), no
  // sobre 0-1000: así un puntaje de 100 se ve vacío y 1000 se ve lleno.
  const progreso = Math.min(1, Math.max(0, (mejor - 100) / 900));

  return (
    <div className="relative">
      {variacion != null && variacion !== 0 && (
        <div
          className={`float-chip absolute -top-4 -right-3 z-10 flex items-center gap-1.5 rounded-full border bg-background px-3 py-1.5 text-xs font-semibold shadow-lg shadow-foreground/5 sm:-right-6 ${
            variacion > 0
              ? "border-success/30 text-success"
              : "border-danger/30 text-danger"
          }`}
        >
          {variacion > 0 ? <UpIcon /> : <DownIcon />}
          {variacion > 0 ? "+" : ""}
          {variacion} pts vs. tu ensayo anterior
        </div>
      )}

      <div className="rounded-2xl border border-border bg-surface p-6 shadow-xl shadow-foreground/5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted">Tu progreso</span>
          <span className="rounded-full bg-surface-hover px-2 py-0.5 text-[11px] text-muted">
            {ensayos} {ensayos === 1 ? "ensayo" : "ensayos"}
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
              {mejor}
              <span className="text-base font-medium text-muted">/1000</span>
            </p>
            <p className="text-xs text-muted">Tu mejor puntaje</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col divide-y divide-border border-t border-border">
          <div className="flex items-center justify-between py-2.5 text-sm">
            <span className="text-muted">Último puntaje</span>
            <span className="font-semibold tabular-nums">{ultimo}</span>
          </div>
          <div className="flex items-center justify-between py-2.5 text-sm">
            <span className="text-muted">Tiempo practicado</span>
            <span className="font-semibold tabular-nums">
              {formatearTiempo(tiempoTotal)}
            </span>
          </div>
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

function UpIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 15l6-6 6 6" />
    </svg>
  );
}

function DownIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}
