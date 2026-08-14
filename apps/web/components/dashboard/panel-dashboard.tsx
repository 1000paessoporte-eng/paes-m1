import Link from "next/link";
import type {
  AnalyticsSummary,
  AuthUserOut,
  BreakdownItem,
  ExamAttemptSummary,
  SkillNode,
} from "@/lib/api";
import { formatearTiempo } from "@/lib/tiempo";
import { SiteFooter } from "@/components/site-footer";
import { ArbolModulo } from "@/components/dashboard/arbol-modulo";
import { ProgresoModulo } from "@/components/dashboard/progreso-modulo";

/**
 * Panel del estudiante autenticado.
 *
 * Es la pantalla de trabajo, no una portada: cada tarjeta responde una
 * pregunta concreta ("¿qué hago ahora?", "¿cómo voy?", "¿qué sigue?") y lleva
 * a la sección que la desarrolla.
 */

interface Props {
  user: AuthUserOut;
  attempts: ExamAttemptSummary[];
  nodos: SkillNode[];
  recomendado: SkillNode | null;
  porEje: BreakdownItem[];
  analytics: AnalyticsSummary | null;
}

export function PanelDashboard({
  user,
  attempts,
  nodos,
  recomendado,
  porEje,
  analytics,
}: Props) {
  const rendidos = attempts.filter((a) => a.status === "submitted");
  const puntajes = rendidos.map((a) => a.estimated_score ?? 0);
  const ultimo = puntajes.length > 0 ? puntajes[0] : null;
  const anterior = puntajes.length > 1 ? puntajes[1] : null;
  const mejor = puntajes.length > 0 ? Math.max(...puntajes) : null;
  const variacion = ultimo != null && anterior != null ? ultimo - anterior : null;
  const enCurso = attempts.find((a) => a.status === "in_progress");
  // El tiempo practicado sale de analítica, que suma lo que el estudiante tardó
  // en cada pregunta. Sumar `elapsed_seconds` de los intentos, en cambio, cuenta
  // el reloj corriendo de los ensayos abandonados: un intento dejado a medias
  // suma sus dos horas completas y el panel llegaba a decir "7 horas
  // practicadas" cuando eran 6 minutos reales.
  const tiempoTotalSegundos = Math.round(
    (analytics?.total_minutes_practiced ?? 0) * 60
  );

  // Solo el nombre de pila: "Hola, Juan" se lee mejor que el nombre completo.
  const nombre = user.name.split(" ")[0];

  // El gris del panel va translúcido para que la hoja de cuaderno del fondo se
  // vea a través; las tarjetas sí son opacas y tapan la cuadrícula, que es lo
  // que mantiene legibles los números.
  return (
    <main className="min-h-[calc(100vh-3.5rem)] flex-1 bg-surface/70">
      <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
          {/* Bienvenida + acción principal */}
          <div className="lg:col-span-2">
            <Bienvenida
              nombre={nombre}
              enCurso={enCurso != null}
              ensayos={rendidos.length}
              mejor={mejor}
              racha={analytics?.current_streak_days ?? 0}
              precision={analytics?.overall_accuracy ?? null}
              tiempoTotal={tiempoTotalSegundos}
            />
          </div>

          {/* Progreso y analítica */}
          <ProgresoModulo puntaje={ultimo} variacion={variacion} porEje={porEje} />

          {/* Árbol de habilidades */}
          <div className="lg:col-span-2">
            <ArbolModulo nodos={nodos} recomendado={recomendado} />
          </div>

          {/* Accesos secundarios */}
          <AccesosRapidos />
        </div>
      </div>

      <SiteFooter />
    </main>
  );
}

function Bienvenida({
  nombre,
  enCurso,
  ensayos,
  mejor,
  racha,
  precision,
  tiempoTotal,
}: {
  nombre: string;
  enCurso: boolean;
  ensayos: number;
  mejor: number | null;
  racha: number;
  precision: number | null;
  tiempoTotal: number;
}) {
  // Sin trama interna: el fondo del sitio ya es una hoja de cuaderno, y dos
  // patrones distintos superpuestos se leen como ruido.
  return (
    <section className="card-panel relative overflow-hidden p-6 sm:p-8">
      <div className="relative">
        <p className="inline-block rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
          Preparación PAES · Admisión 2027
        </p>

        <h1 className="mt-3 text-2xl font-bold tracking-tight sm:text-3xl">
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

        <p className="mt-2 max-w-lg text-sm leading-relaxed text-muted">
          {/* El ensayo en curso manda sobre el resto: si hay uno a medias, el
              texto tiene que explicar el botón "Reanudar", aunque todavía no
              haya ningún ensayo terminado. */}
          {enCurso
            ? "Tienes un ensayo sin terminar. Al continuar retomas justo donde quedaste, con el tiempo que te quedaba."
            : ensayos === 0
              ? "Tu primer ensayo define el punto de partida: te da un puntaje estimado y muestra en qué ejes conviene reforzar."
              : "Cada ensayo actualiza tu puntaje estimado y desbloquea temas nuevos en el árbol."}
        </p>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Link
            href="/examen"
            className="btn-warm rounded-lg px-5 py-2.5 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5"
          >
            {enCurso
              ? "Reanudar ensayo"
              : ensayos === 0
                ? "Comenzar mi primer ensayo"
                : "Comenzar nuevo ensayo"}{" "}
            →
          </Link>
          {ensayos > 0 && (
            <Link
              href="/historial"
              className="rounded-lg border border-border bg-background px-4 py-2.5 text-sm font-medium transition-colors hover:bg-surface-hover"
            >
              Ver mis ensayos
            </Link>
          )}
        </div>

        {ensayos > 0 && (
          <dl className="mt-7 grid grid-cols-2 gap-x-6 gap-y-4 border-t border-border pt-5 sm:grid-cols-4">
            <Metrica etiqueta="Ensayos rendidos" valor={String(ensayos)} />
            <Metrica
              etiqueta="Mejor puntaje"
              valor={mejor != null ? String(mejor) : "—"}
            />
            <Metrica
              etiqueta="Precisión global"
              valor={precision != null ? `${Math.round(precision * 100)}%` : "—"}
            />
            <Metrica
              etiqueta="Tiempo practicado"
              valor={formatearTiempo(tiempoTotal)}
            />
          </dl>
        )}

        {racha > 0 && (
          <p className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-accent-warm/10 px-3 py-1 text-xs font-semibold text-accent-warm-strong">
            🔥 {racha} {racha === 1 ? "día seguido" : "días seguidos"} practicando
          </p>
        )}
      </div>
    </section>
  );
}

function Metrica({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <div>
      <dt className="text-xs text-muted">{etiqueta}</dt>
      <dd className="mt-0.5 text-xl font-bold tabular-nums tracking-tight">
        {valor}
      </dd>
    </div>
  );
}

const ACCESOS = [
  { href: "/analitica", titulo: "Analítica", texto: "Tiempo y acierto en el tiempo" },
  { href: "/historial", titulo: "Mi progreso", texto: "Evolución de tus puntajes" },
  { href: "/perfil", titulo: "Mi perfil", texto: "Nombre y contraseña" },
  { href: "/planes", titulo: "Planes", texto: "Qué incluye cada uno" },
] as const;

function AccesosRapidos() {
  return (
    <section className="card-panel p-6" aria-labelledby="h-accesos">
      <h2 id="h-accesos" className="font-semibold tracking-tight">
        Accesos
      </h2>
      <ul className="mt-4 flex flex-col divide-y divide-border">
        {ACCESOS.map((a) => (
          <li key={a.href}>
            <Link
              href={a.href}
              className="group flex items-center justify-between gap-3 py-3 transition-colors"
            >
              <span className="min-w-0">
                <span className="block text-sm font-medium group-hover:text-accent">
                  {a.titulo}
                </span>
                <span className="block truncate text-xs text-muted">{a.texto}</span>
              </span>
              <span className="shrink-0 text-muted transition-transform group-hover:translate-x-0.5 group-hover:text-accent">
                →
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
