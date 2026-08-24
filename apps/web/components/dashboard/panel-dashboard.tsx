import Link from "next/link";
import type {
  AnalyticsSummary,
  AuthUserOut,
  BreakdownItem,
  ExamAttemptSummary,
  Meta,
  MiPlan,
  Onboarding,
  SkillNode,
  Subject,
} from "@/lib/api";
import { formatearTiempo } from "@/lib/tiempo";
import { SiteFooter } from "@/components/site-footer";
import { ArbolModulo } from "@/components/dashboard/arbol-modulo";
import { AnuncioPremio } from "@/components/premio/anuncio-premio";
import { AnuncioPlanes } from "@/components/plan/anuncio-planes";
import { AnunciosDiarios } from "@/components/dashboard/anuncios-diarios";
import { Cuestionario } from "@/components/onboarding/cuestionario";
import { MetaModulo } from "@/components/dashboard/meta-modulo";
import { ProModulo } from "@/components/dashboard/pro-modulo";
import { ProgresoModulo } from "@/components/dashboard/progreso-modulo";
import { Insignias, Racha } from "@/components/gamificacion/logros";
import { NOMBRE_CORTO } from "@/lib/colores-prueba";
import { calcularLogros } from "@/lib/logros";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { Reveal } from "@/components/motion/reveal";

/**
 * Panel del estudiante autenticado.
 *
 * Es la pantalla de trabajo, no una portada: cada tarjeta responde una
 * pregunta concreta ("¿qué hago ahora?", "¿cómo voy?", "¿qué sigue?") y lleva
 * a la sección que la desarrolla.
 *
 * La grilla es tipo bento: bloques de distinto tamaño donde el tamaño indica
 * importancia. El bloque de bienvenida ocupa dos columnas porque contiene la
 * única acción que importa —empezar un ensayo—; los accesos secundarios ocupan
 * una y van al final.
 */

interface Props {
  user: AuthUserOut;
  attempts: ExamAttemptSummary[];
  nodos: SkillNode[];
  recomendado: SkillNode | null;
  porEje: BreakdownItem[];
  analytics: AnalyticsSummary | null;
  meta: Meta | null;
  onboarding: Onboarding | null;
  ejesDe: string | null;
  //: Plan del alumno, para decidir si corresponde ofrecerle Pro.
  plan?: MiPlan | null;
}

export function PanelDashboard({
  user,
  attempts,
  nodos,
  recomendado,
  porEje,
  analytics,
  meta,
  onboarding,
  ejesDe,
  plan,
}: Props) {
  const rendidos = attempts.filter((a) => a.status === "submitted");

  // El puntaje que encabeza el panel es el del último ensayo, sea de la prueba
  // que sea. Va CON el nombre de su prueba: un 406 no significa lo mismo en
  // Historia que en M1, y sin decir de cuál es, el número no se puede leer.
  const ultimoIntento = rendidos[0] ?? null;
  const ultimo = ultimoIntento?.estimated_score ?? null;

  // Y se compara contra el ensayo anterior DE LA MISMA PRUEBA. Antes tomaba
  // el anterior a secas: con un 406 de Historia después de un 378 de M2, el
  // panel anunciaba "▲ +28 vs. anterior" comparando dos pruebas distintas,
  // con temarios y tablas de transformación del DEMRE distintas. Esa subida
  // no le pasó a nadie.
  const anteriorMismaPrueba =
    ultimoIntento != null
      ? (rendidos
          .slice(1)
          .find(
            (a) =>
              a.subject === ultimoIntento.subject && a.estimated_score != null
          )?.estimated_score ?? null)
      : null;
  const variacion =
    ultimo != null && anteriorMismaPrueba != null ? ultimo - anteriorMismaPrueba : null;

  // El mejor puntaje también viaja con su prueba, por la misma razón.
  const mejorIntento = rendidos.reduce<(typeof rendidos)[number] | null>(
    (mejorHasta, a) =>
      (a.estimated_score ?? -1) > (mejorHasta?.estimated_score ?? -1) ? a : mejorHasta,
    null
  );
  const mejor = mejorIntento?.estimated_score ?? null;
  const enCurso = attempts.find((a) => a.status === "in_progress");
  // El tiempo practicado sale de analítica, que suma lo que el estudiante tardó
  // en cada pregunta. Sumar `elapsed_seconds` de los intentos, en cambio, cuenta
  // el reloj corriendo de los ensayos abandonados: un intento dejado a medias
  // suma sus dos horas completas y el panel llegaba a decir "7 horas
  // practicadas" cuando eran 6 minutos reales.
  const tiempoTotalSegundos = Math.round(
    (analytics?.total_minutes_practiced ?? 0) * 60
  );

  const racha = analytics?.current_streak_days ?? 0;

  // Progreso hacia los requisitos del premio que ya se pueden cumplir hoy. Un
  // ensayo "completo" son 34 preguntas o más, igual que en las bases: si el
  // anuncio contara distinto que el reglamento, el reclamo llegaría después.
  const ensayosCompletos = rendidos.filter((a) => a.total_questions >= 34).length;
  const precision = analytics?.overall_accuracy ?? null;

  // Los logros se derivan de lo que el estudiante hizo de verdad; ninguno se
  // regala. Ver el comentario de cabecera de `lib/logros.ts`.
  const logros = calcularLogros({
    ensayos: rendidos.length,
    racha,
    precision,
    nodosDominados: nodos.filter((n) => n.status === "mastered").length,
    mejorPuntaje: mejor,
  });

  // Solo el nombre de pila: "Hola, Juan" se lee mejor que el nombre completo.
  const nombre = user.name.split(" ")[0];

  // El gris del panel va translúcido para que la hoja de cuaderno del fondo se
  // vea a través; las tarjetas sí son opacas y tapan la cuadrícula, que es lo
  // que mantiene legibles los números.
  return (
    <main className="min-h-[calc(100vh-3.5rem)] flex-1 bg-surface/70">
      {/* El cuestionario tiene prioridad sobre cualquier otro aviso: es lo
          primero que ve alguien que acaba de entrar, y con sus respuestas se
          configura el resto.

          Y si todavía no ha rendido nada, no ve ningún aviso. Su primera
          sesión es para probar la plataforma, no para recibir ofertas: el
          premio exige plan Pro y seis meses de constancia, así que a alguien
          con cero ensayos solo le dice que esto no es para él todavía. Además
          cubre el caso en que no sabemos si respondió el cuestionario (la
          llamada se degrada a null en panel/page.tsx): antes, no saberlo
          significaba mostrarle la promo del premio a un recién llegado. */}
      {onboarding && !onboarding.respondido ? (
        <Cuestionario nombre={nombre} />
      ) : rendidos.length === 0 ? null : (
        <AnunciosDiarios
          ofrecerPro={plan != null && plan.plan === "gratis"}
          premio={
            <AnuncioPremio
              progreso={{
                ensayosCompletos,
                diasPracticados: analytics?.active_days ?? 0,
                mejorRachaEnsayos: analytics?.best_exam_streak_days ?? 0,
              }}
            />
          }
          planes={
            plan ? (
              <AnuncioPlanes
                usados={plan.ensayos_usados}
                limite={plan.ensayos_limite}
                precio="$9.990 al mes"
              />
            ) : null
          }
        />
      )}
      <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
          {/* Bienvenida + acción principal */}
          <div className="lg:col-span-2">
            <Bienvenida
              nombre={nombre}
              enCurso={enCurso != null}
              ensayos={rendidos.length}
              mejor={mejor}
              mejorPrueba={mejorIntento?.subject ?? null}
              racha={racha}
              rachaEnsayos={analytics?.exam_streak_days ?? 0}
              precision={precision}
              tiempoTotal={tiempoTotalSegundos}
            />
          </div>

          {/* Progreso y analítica */}
          <Reveal delay={0.05}>
            <ProgresoModulo
              puntaje={ultimo}
              prueba={ultimoIntento?.subject ?? null}
              variacion={variacion}
              porEje={porEje}
              ejesDe={ejesDe}
            />
          </Reveal>

          {/* Árbol de habilidades */}
          <Reveal delay={0.1} className="lg:col-span-2">
            <ArbolModulo nodos={nodos} recomendado={recomendado} />
          </Reveal>

          {/* La meta: cuánto falta para la carrera que quiere */}
          <Reveal delay={0.15}>
            <MetaModulo meta={meta} />
          </Reveal>

          {/* Logros */}
          <Reveal delay={0.2}>
            <Insignias logros={logros} />
          </Reveal>

          {/* El plan Pro, solo para quien está en Gratis. A quien ya lo tiene
              no se le ofrece lo que ya compró. */}
          {plan?.plan === "gratis" && (
            <Reveal delay={0.22}>
              <ProModulo
                usados={plan.ensayos_usados}
                limite={plan.ensayos_limite}
              />
            </Reveal>
          )}

          {/* Accesos secundarios */}
          <Reveal delay={0.25} className="lg:col-span-2">
            <AccesosRapidos />
          </Reveal>
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
  mejorPrueba,
  racha,
  rachaEnsayos,
  precision,
  tiempoTotal,
}: {
  nombre: string;
  enCurso: boolean;
  ensayos: number;
  mejor: number | null;
  mejorPrueba: Subject | null;
  racha: number;
  rachaEnsayos: number;
  precision: number | null;
  tiempoTotal: number;
}) {
  // Sin trama interna: el fondo del sitio ya es una hoja de cuaderno, y dos
  // patrones distintos superpuestos se leen como ruido.
  return (
    <section className="card-panel relative overflow-hidden p-6 sm:p-8">
      <div className="relative">
        <div className="flex flex-wrap items-center gap-2">
          <p className="inline-block rounded-full border border-accent/30 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
            Preparación PAES · Admisión 2027
          </p>
          {/* La racha va arriba, junto al saludo: es lo que se viene a mirar
              todos los días, y abajo del todo se perdía. */}
          <Racha dias={racha} />
          {/* La racha de ENSAYOS es la que cuenta para el premio, así que se
              muestra aparte de la de práctica: son cosas distintas y mezclarlas
              haría que alguien creyera que califica cuando no. */}
          {rachaEnsayos > 0 && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-accent/30 bg-accent/5 px-3 py-1.5 text-sm font-semibold text-accent">
              📝 {rachaEnsayos} {rachaEnsayos === 1 ? "día" : "días"} con ensayo
            </span>
          )}
        </div>

        <h1 className="mt-3 text-2xl font-bold tracking-tight sm:text-3xl">
          Hola, <span className="font-display">{nombre}</span>
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
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
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
            <Metrica etiqueta="Ensayos rendidos" valor={ensayos} />
            <Metrica
              etiqueta={
                mejorPrueba ? `Mejor puntaje · ${NOMBRE_CORTO[mejorPrueba]}` : "Mejor puntaje"
              }
              valor={mejor}
            />
            <Metrica
              etiqueta="Precisión global"
              valor={precision != null ? Math.round(precision * 100) : null}
              sufijo="%"
            />
            <Metrica etiqueta="Tiempo practicado" texto={formatearTiempo(tiempoTotal)} />
          </dl>
        )}
      </div>
    </section>
  );
}

function Metrica({
  etiqueta,
  valor,
  texto,
  sufijo = "",
}: {
  etiqueta: string;
  valor?: number | null;
  texto?: string;
  sufijo?: string;
}) {
  return (
    <div>
      <dt className="text-xs text-muted">{etiqueta}</dt>
      <dd className="mt-0.5 text-xl font-bold tabular-nums tracking-tight">
        {texto != null ? (
          texto
        ) : valor != null ? (
          <NumeroAnimado valor={valor} sufijo={sufijo} duracion={0.8} />
        ) : (
          "—"
        )}
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
      {/* En una fila completa los accesos van en grilla, no en lista: en móvil
          quedan de a uno, y desde tablet aprovechan el ancho. */}
      <ul className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {ACCESOS.map((a) => (
          <li key={a.href}>
            <Link
              href={a.href}
              className="card-hover group flex items-center justify-between gap-3 rounded-xl border border-border p-3"
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
