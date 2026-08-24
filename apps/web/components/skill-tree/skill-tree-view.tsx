"use client";

import { motion, useReducedMotion } from "framer-motion";
import { COLOR_PRUEBA } from "@/lib/colores-prueba";
import { BarraProgreso } from "@/components/ui/barra-progreso";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import type { Subject } from "@/lib/api";
import Link from "next/link";
import { useCallback, useLayoutEffect, useRef, useState, type ReactElement } from "react";
import { cn } from "@paes-m1/utils";
import type { SkillNode } from "@/lib/api";

type AxisMeta = {
  label: string;
  iconBg: string;
  iconColor: string;
  border: string;
  bar: string;
  icon: () => ReactElement;
};

const AXIS_META: Record<SkillNode["axis"], AxisMeta> = {
  // Competencia Lectora: el "eje" es la habilidad que evalúa el temario.
  localizar: {
    label: "Localizar",
    iconBg: "bg-sky-500/10",
    iconColor: "text-sky-400",
    border: "hover:border-sky-500/50",
    bar: "bg-sky-400",
    icon: NumbersIcon,
  },
  interpretar: {
    label: "Interpretar",
    iconBg: "bg-violet-500/10",
    iconColor: "text-violet-400",
    border: "hover:border-violet-500/50",
    bar: "bg-violet-400",
    icon: AlgebraIcon,
  },
  evaluar: {
    label: "Evaluar",
    iconBg: "bg-emerald-500/10",
    iconColor: "text-emerald-400",
    border: "hover:border-emerald-500/50",
    bar: "bg-emerald-400",
    icon: GeometryIcon,
  },
  // Historia y Ciencias Sociales.
  historia: {
    label: "Historia",
    iconBg: "bg-amber-500/10",
    iconColor: "text-amber-400",
    border: "hover:border-amber-500/50",
    bar: "bg-amber-400",
    icon: GeometryIcon,
  },
  ciudadania: {
    label: "Formación ciudadana",
    iconBg: "bg-violet-500/10",
    iconColor: "text-violet-400",
    border: "hover:border-violet-500/50",
    bar: "bg-violet-400",
    icon: AlgebraIcon,
  },
  economia: {
    label: "Economía y sociedad",
    iconBg: "bg-sky-500/10",
    iconColor: "text-sky-400",
    border: "hover:border-sky-500/50",
    bar: "bg-sky-400",
    icon: NumbersIcon,
  },
  // Ciencias: el eje es la disciplina.
  biologia: {
    label: "Biología",
    iconBg: "bg-emerald-500/10",
    iconColor: "text-emerald-400",
    border: "hover:border-emerald-500/50",
    bar: "bg-emerald-400",
    icon: GeometryIcon,
  },
  fisica: {
    label: "Física",
    iconBg: "bg-sky-500/10",
    iconColor: "text-sky-400",
    border: "hover:border-sky-500/50",
    bar: "bg-sky-400",
    icon: NumbersIcon,
  },
  quimica: {
    label: "Química",
    iconBg: "bg-amber-500/10",
    iconColor: "text-amber-400",
    border: "hover:border-amber-500/50",
    bar: "bg-amber-400",
    icon: AlgebraIcon,
  },
  numeros: {
    label: "Números",
    iconBg: "bg-sky-500/10",
    iconColor: "text-sky-400",
    border: "hover:border-sky-500/50",
    bar: "bg-sky-400",
    icon: NumbersIcon,
  },
  algebra: {
    label: "Álgebra",
    iconBg: "bg-violet-500/10",
    iconColor: "text-violet-400",
    border: "hover:border-violet-500/50",
    bar: "bg-violet-400",
    icon: AlgebraIcon,
  },
  geometria: {
    label: "Geometría",
    iconBg: "bg-emerald-500/10",
    iconColor: "text-emerald-400",
    border: "hover:border-emerald-500/50",
    bar: "bg-emerald-400",
    icon: GeometryIcon,
  },
  probabilidad: {
    label: "Probabilidad",
    iconBg: "bg-amber-500/10",
    iconColor: "text-amber-400",
    border: "hover:border-amber-500/50",
    bar: "bg-amber-400",
    icon: DiceIcon,
  },
};

/**
 * Orden canónico de los ejes, con los trece de las cinco pruebas.
 *
 * Las columnas NO se toman de esta lista sino de los ejes que traen los nodos
 * recibidos: el árbol de Competencia Lectora no tiene "Números", y fijar las
 * columnas dejaba cuatro columnas de matemática vacías al cambiar de prueba.
 * Esta lista solo dice en qué orden se muestran las que sí existen.
 */
const AXIS_ORDER: SkillNode["axis"][] = [
  // Matemática
  "numeros",
  "algebra",
  "geometria",
  "probabilidad",
  // Competencia Lectora
  "localizar",
  "interpretar",
  "evaluar",
  // Ciencias
  "biologia",
  "fisica",
  "quimica",
  // Historia y Ciencias Sociales
  "historia",
  "ciudadania",
  "economia",
];


interface SkillTreeViewProps {
  nodes: SkillNode[];
}

export function SkillTreeView({ nodes }: SkillTreeViewProps) {
  const nameByCode = new Map(nodes.map((n) => [n.code, n.name]));

  // El grafo al revés: qué abre cada nodo. Las aristas ya existen --son las
  // que dibujan los conectores-- pero solo se leían en un sentido, así que la
  // tarjeta podía decir qué la abre a ella y nunca qué abre ella.
  const abreByCode = new Map<string, string[]>();
  for (const n of nodes) {
    for (const prereq of n.prerequisite_codes) {
      abreByCode.set(prereq, [...(abreByCode.get(prereq) ?? []), n.name]);
    }
  }
  const quieto = useReducedMotion();

  // El color sale de los propios nodos, no de una prop: el árbol de una prueba
  // solo trae nodos de esa prueba, y así ninguna pantalla puede pasarle un
  // color que no le corresponda.
  const colorPrueba = nodes.length
    ? COLOR_PRUEBA[nodes[0].subject as Subject]
    : "var(--accent)";

  const ejesPresentes = AXIS_ORDER.filter((axis) =>
    nodes.some((n) => n.axis === axis)
  );

  const columns = ejesPresentes.map((axis) => ({
    axis,
    nodes: nodes
      .filter((n) => n.axis === axis)
      .sort((a, b) => a.tier - b.tier || a.display_order - b.display_order),
  }));

  const dominados = nodes.filter((n) => n.status === "mastered").length;
  const disponibles = nodes.filter(
    (n) => n.status !== "locked" && n.status !== "mastered"
  ).length;

  // ── Los conectores ──────────────────────────────────────────────────
  // Se miden sobre el CONTENEDOR COMPLETO y no columna por columna. Las
  // dependencias reales cruzan ejes --el Teorema de Pitágoras necesita
  // "Potencias y raíces" (Números) Y "Perímetros y áreas" (Geometría)-- y
  // dibujando dentro de cada columna esas líneas no existían: el árbol
  // mostraba cuatro caminos paralelos cuando en realidad es una sola red.
  const contenedorRef = useRef<HTMLDivElement>(null);
  const puntos = useRef<Map<string, HTMLSpanElement>>(new Map());
  const [aristas, setAristas] = useState<Arista[]>([]);
  const [resaltado, setResaltado] = useState<string | null>(null);

  const registrarPunto = useCallback((code: string, el: HTMLSpanElement | null) => {
    if (el) puntos.current.set(code, el);
    else puntos.current.delete(code);
  }, []);

  const medir = useCallback(() => {
    const caja = contenedorRef.current;
    if (!caja) return;
    const base = caja.getBoundingClientRect();
    const siguientes: Arista[] = [];

    for (const node of nodes) {
      for (const prereq of node.prerequisite_codes) {
        const desde = puntos.current.get(prereq);
        const hasta = puntos.current.get(node.code);
        // Los prerrequisitos de M2 son nodos de M1 y no están en este árbol:
        // sin punto que medir, no hay línea que dibujar.
        if (!desde || !hasta) continue;

        const a = desde.getBoundingClientRect();
        const b = hasta.getBoundingClientRect();
        const x1 = a.left + a.width / 2 - base.left;
        const y1 = a.top + a.height / 2 - base.top;
        const x2 = b.left + b.width / 2 - base.left;
        const y2 = b.top + b.height / 2 - base.top;

        siguientes.push({
          id: `${prereq}->${node.code}`,
          origen: prereq,
          destino: node.code,
          activa: node.status !== "locked",
          cruzada: Math.abs(x2 - x1) > 4,
          d: trazar(x1, y1, x2, y2),
        });
      }
    }
    setAristas(siguientes);
  }, [nodes]);

  useLayoutEffect(() => {
    medir();
    const caja = contenedorRef.current;
    // ResizeObserver y no solo `resize`: las columnas cambian de alto cuando
    // el texto se reacomoda, y ahí la ventana no dispara nada.
    const observador = new ResizeObserver(medir);
    if (caja) observador.observe(caja);
    window.addEventListener("resize", medir);
    return () => {
      observador.disconnect();
      window.removeEventListener("resize", medir);
    };
  }, [medir]);

  return (
    <>
      {/* CUÁNTO LLEVAS DEL ÁRBOL ENTERO. */}
      <div className="mb-8 rounded-2xl border border-border bg-surface p-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <p className="font-display text-3xl leading-none font-bold">
            <NumeroAnimado valor={dominados} duracion={0.9} />
            <span className="text-lg font-semibold text-muted">/{nodes.length}</span>
            <span className="ml-2 align-middle text-sm font-medium text-muted">
              temas dominados
            </span>
          </p>
          {disponibles > 0 && (
            <p className="text-sm text-muted">
              <strong className="text-foreground tabular-nums">{disponibles}</strong>{" "}
              {disponibles === 1 ? "disponible ahora" : "disponibles ahora"}
            </p>
          )}
        </div>
        <div className="mt-3">
          <BarraProgreso
            porcentaje={nodes.length ? (dominados / nodes.length) * 100 : 0}
            color={colorPrueba}
            etiqueta={`${dominados} de ${nodes.length} temas dominados`}
            alCargar
          />
        </div>
      </div>

      <div ref={contenedorRef} className="relative">
        {/* El lienzo va DETRÁS de las tarjetas. Las tarjetas son opacas, así
            que una línea que las cruza se ve solo en los huecos entre
            columnas: queda como un plano de metro, con las estaciones tapando
            el trazado y el recorrido visible entre medio. */}
        <svg
          className="pointer-events-none absolute inset-0 z-0 h-full w-full overflow-visible"
          aria-hidden="true"
        >
          {aristas.map((e, i) => {
            const enfocada = resaltado === e.origen || resaltado === e.destino;
            const apagada = resaltado !== null && !enfocada;
            return (
              <motion.path
                key={e.id}
                d={e.d}
                fill="none"
                stroke={e.activa || enfocada ? colorPrueba : "var(--border-strong)"}
                strokeWidth={enfocada ? 3 : 2}
                strokeDasharray={e.activa ? undefined : "4 5"}
                strokeLinecap="round"
                initial={quieto ? false : { pathLength: 0, opacity: 0 }}
                animate={{
                  pathLength: 1,
                  // Al pasar por encima de un tema se apaga todo lo que no
                  // sale de él: así se ve QUÉ ABRE, que es la pregunta que un
                  // árbol de habilidades tiene que poder contestar de un
                  // vistazo y que hasta ahora había que deducir leyendo doce
                  // recuadros de requisitos.
                  // Lo enfocado va entero aunque el destino esté bloqueado:
                  // el punto del resaltado es JUSTAMENTE mostrar el camino que
                  // todavía no se abre.
                  opacity: apagada ? 0.12 : enfocada ? 1 : e.activa ? 0.9 : 0.45,
                }}
                transition={
                  quieto
                    ? { duration: 0 }
                    : {
                        pathLength: { delay: 0.2 + i * 0.05, duration: 0.5, ease: "easeOut" },
                        opacity: { duration: 0.2 },
                      }
                }
              />
            );
          })}
        </svg>

        <div
          className={cn(
            "relative z-10 grid grid-cols-1 gap-8 sm:grid-cols-2",
            columns.length === 3 ? "xl:grid-cols-3" : "xl:grid-cols-4"
          )}
        >
          {columns.map((column) => (
            <TreeColumn
              key={column.axis}
              axis={column.axis}
              nodes={column.nodes}
              nameByCode={nameByCode}
              abreByCode={abreByCode}
              colorPrueba={colorPrueba}
              registrarPunto={registrarPunto}
              resaltado={resaltado}
              onResaltar={setResaltado}
            />
          ))}
        </div>
      </div>
    </>
  );
}

/**
 * El camino entre dos nodos.
 *
 * Dentro de una misma columna es una recta vertical por la canaleta, que es
 * lo que ya se veía. Entre columnas es una curva con tiradores horizontales:
 * sale del nodo, se abre y entra al otro. Una recta diagonal cruzaría las
 * tarjetas en ángulo y se leería como un tachón.
 */
function trazar(x1: number, y1: number, x2: number, y2: number): string {
  if (Math.abs(x2 - x1) < 4) return `M ${x1} ${y1} L ${x2} ${y2}`;
  // Los tiradores van cada uno HACIA el otro extremo. Tirando los dos hacia el
  // mismo lado la curva se devuelve sobre sí misma y se sale del contenedor.
  const dx = x2 - x1;
  const tirador = Math.abs(dx) * 0.5;
  return `M ${x1} ${y1} C ${x1 + tirador} ${y1}, ${x2 - tirador} ${y2}, ${x2} ${y2}`;
}

interface Arista {
  id: string;
  origen: string;
  destino: string;
  activa: boolean;
  cruzada: boolean;
  d: string;
}

function TreeColumn({
  axis,
  nodes,
  nameByCode,
  abreByCode,
  colorPrueba,
  registrarPunto,
  resaltado,
  onResaltar,
}: {
  axis: SkillNode["axis"];
  nodes: SkillNode[];
  nameByCode: Map<string, string>;
  /** Qué temas abre cada nodo, derivado de las mismas aristas. */
  abreByCode: Map<string, string[]>;
  /** El color de la prueba a la que pertenece este árbol. */
  colorPrueba: string;
  /** La columna ya no mide: solo entrega sus puntos al árbol, que es quien
   *  tiene el sistema de coordenadas donde las líneas cruzan ejes. */
  registrarPunto: (code: string, el: HTMLSpanElement | null) => void;
  resaltado: string | null;
  onResaltar: (code: string | null) => void;
}) {
  const meta = AXIS_META[axis];

  return (
    <div className="flex flex-col gap-4">
      {/* El ícono va en el color de la PRUEBA, no en un color propio del eje.
          Los cuatro ejes llevaban turquesa, violeta, verde y ámbar quemados a
          mano, que son --literalmente-- los colores de identidad de Ciencias,
          M2 y Lectora: el árbol de Matemática M1 estaba pintado con los
          colores de las otras pruebas. Los ejes se distinguen por su ícono y
          su nombre, que es información; el color acá significa qué prueba. */}
      <div className="flex items-center gap-2.5">
        <span
          className="flex h-7 w-7 items-center justify-center rounded-md"
          style={{
            backgroundColor: `color-mix(in srgb, ${colorPrueba} 12%, transparent)`,
            color: colorPrueba,
          }}
        >
          <meta.icon />
        </span>
        <h2 className="text-sm font-semibold">{meta.label}</h2>
        <span className="ml-auto text-xs text-muted tabular-nums">
          {nodes.filter((n) => n.status === "mastered").length}/{nodes.length}
        </span>
      </div>

      <ol className="relative flex flex-col gap-3">
        {nodes.map((node, i) => {
          const locked = node.status === "locked";
          const mastered = node.status === "mastered";
          const pct = Math.round(node.accuracy * 100);
          const abre = abreByCode.get(node.code) ?? [];
          // "Dominado" usa el color de la prueba porque es identidad --este
          // árbol--, mientras que "Desbloqueado" conserva el verde, que ahí
          // sí es estado. Es la regla de no mezclar identidad con estado.
          return (
            <motion.li
              key={node.code}
              initial={{ opacity: 0, y: 8 }}
              animate={{
                opacity: resaltado !== null && resaltado !== node.code ? 0.5 : 1,
                y: 0,
              }}
              transition={{ delay: i * 0.06, duration: 0.35, ease: "easeOut" }}
              style={{ "--color-prueba": colorPrueba } as React.CSSProperties}
              className="flex gap-3"
              // Pasar por encima de un tema enciende lo que ese tema ABRE.
              // Es la pregunta que un árbol de habilidades tiene que poder
              // contestar de un vistazo, y hasta ahora había que deducirla
              // leyendo el recuadro de requisitos de los doce nodos.
              onMouseEnter={() => onResaltar(node.code)}
              onMouseLeave={() => onResaltar(null)}
              onFocus={() => onResaltar(node.code)}
              onBlur={() => onResaltar(null)}
            >
              <div className="flex w-6 shrink-0 justify-center pt-4">
                <span
                  ref={(el) => registrarPunto(node.code, el)}
                  className={cn(
                    "h-2.5 w-2.5 shrink-0 rounded-full border-2",
                    mastered
                      ? "border-accent bg-accent"
                      : locked
                        ? "border-border-strong bg-background"
                        : "border-success bg-success"
                  )}
                />
              </div>

              {/* LA TARJETA CAMBIA DE TAMAÑO SEGÚN EL ESTADO.
                  Antes las tres se veían igual: un nodo bloqueado pesaba lo
                  mismo que el que puedes hacer ahora, y con doce nodos por
                  columna eso es un muro parejo donde no se distingue nada. En
                  un árbol de habilidades lo que puedes hacer TIENE que mandar.

                  · Dominado: se encoge a una línea. Ya está, no necesita
                    espacio; solo la marca de que lo lograste.
                  · Disponible: la tarjeta completa, con el anillo de avance y
                    las dos acciones. Es a lo que viniste.
                  · Bloqueado: apagado y compacto, con el requisito en UNA
                    línea corta en vez del párrafo que había. */}
              {mastered ? (
                <div className="flex flex-1 items-center gap-2.5 rounded-xl border border-success/30 bg-success/5 px-3.5 py-2.5">
                  <svg
                    width="14" height="14" viewBox="0 0 24 24" fill="none"
                    stroke="var(--success)" strokeWidth="3" strokeLinecap="round"
                    strokeLinejoin="round" className="shrink-0" aria-hidden="true"
                  >
                    <path d="M20 6 9 17l-5-5" />
                  </svg>
                  <span className="min-w-0 flex-1 truncate text-sm font-medium">
                    {node.name}
                  </span>
                  <span className="shrink-0 text-xs font-semibold text-success tabular-nums">
                    {pct}%
                  </span>
                </div>
              ) : locked ? (
                <div className="flex-1 rounded-xl border border-dashed border-border bg-transparent px-3.5 py-3">
                  <div className="flex items-start gap-2">
                    <span className="mt-0.5 shrink-0 text-muted">
                      <LockIcon />
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-muted">{node.name}</p>
                      {node.prerequisite_codes.length > 0 && (
                        <p className="mt-0.5 text-xs leading-snug text-muted">
                          Se abre al dominar{" "}
                          <span className="font-medium">
                            {(node.prerequisite_names?.length
                              ? node.prerequisite_names
                              : node.prerequisite_codes.map(
                                  (code) => nameByCode.get(code) ?? code
                                )
                            ).join(" y ")}
                          </span>
                        </p>
                      )}
                      {/* El árbol RECOMIENDA un orden; no lo impone. Sin esta
                          salida, M2 era un callejón: sus dieciséis temas
                          cuelgan de M1, así que el alumno que iba a rendir M2
                          abría su árbol y no podía practicar ni una pregunta
                          —mientras Modo Ensayo sí le dejaba rendir un ensayo
                          de M2 entero. Practicar acá suma al progreso, pero no
                          salta la cadena: el nodo sigue bloqueado hasta que su
                          prerrequisito esté dominado. */}
                      <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1">
                        {node.has_lesson && (
                          <Link
                            href={`/aprender/${node.code}`}
                            className="inline-block text-xs font-medium text-accent"
                          >
                            Leer la teoría igual
                          </Link>
                        )}
                        <Link
                          href={`/practicar/${node.code}`}
                          className="inline-block text-xs font-medium text-muted underline decoration-border underline-offset-4 hover:text-foreground"
                        >
                          Practicar igual
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div
                  className="card-hover flex-1 overflow-hidden rounded-xl border-2 bg-surface transition-colors"
                  style={{ borderColor: `color-mix(in srgb, ${colorPrueba} 35%, transparent)` }}
                >
                  {/* El nombre ocupa el ancho COMPLETO y el anillo baja a la
                      fila de abajo. Con el anillo al lado, en una columna de
                      cuatro el título quedaba en una canaleta de 150 px y se
                      partía en tres líneas, y los dos botones se apilaban uno
                      sobre otro. */}
                  <div className="p-4">
                    <p className="text-sm leading-snug font-semibold text-balance">
                      {node.name}
                    </p>

                    {/* QUÉ ES EL TEMA, en la pantalla donde se elige qué
                        estudiar. Antes la tarjeta decía el nombre y el
                        porcentaje de acierto: "Transformaciones isométricas"
                        no le dice nada a alguien de tercero medio, así que
                        para saber de qué iba había que abrir la lección --o
                        sea, decidir antes de tener con qué decidir.

                        El texto ya estaba escrito en `lessons.intro`, que
                        existe justamente para responder "¿para qué me sirve
                        esto?", y no lo leía nadie. */}
                    {node.lesson_intro && (
                      <p className="mt-1.5 text-xs leading-relaxed text-muted">
                        {node.lesson_intro}
                      </p>
                    )}

                    {/* Y qué ABRE. La tarjeta bloqueada siempre dijo qué la
                        abre a ella; ninguna decía lo contrario, así que la
                        mitad del grafo que motiva --"esto te sirve para
                        cuatro temas más"-- era invisible. Sale de las mismas
                        aristas que ya dibujan los conectores. */}
                    {abre.length > 0 && (
                      <p className="mt-2 text-xs text-muted">
                        Abre{" "}
                        <span className="font-medium text-foreground">
                          {abre.length === 1 ? abre[0] : `${abre.length} temas`}
                        </span>
                      </p>
                    )}

                    <div className="mt-3 flex items-center gap-3">
                      {/* El anillo dice de un vistazo cuánto llevas en ESTE
                          tema. Una barra fina de 4 px no se veía; un anillo sí. */}
                      <AnilloAvance porcentaje={pct} color={colorPrueba} />
                      <p className="min-w-0 text-xs leading-snug text-muted">
                        {node.attempts > 0
                          ? `de acierto en ${node.attempts} ${node.attempts === 1 ? "respuesta" : "respuestas"}`
                          : "Todavía sin practicar"}
                      </p>
                    </div>

                    <div className="mt-3 flex items-center gap-2">
                      <Link
                        href={`/practicar/${node.code}`}
                        className="flex-1 rounded-lg px-3 py-2 text-center text-xs font-semibold text-on-fill transition hover:opacity-90"
                        style={{ backgroundColor: colorPrueba }}
                      >
                        Practicar
                      </Link>
                      {node.has_lesson && (
                        <Link
                          href={`/aprender/${node.code}`}
                          className="rounded-lg border border-border px-3 py-2 text-xs font-medium transition hover:bg-surface-hover"
                        >
                          Teoría
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </motion.li>
          );
        })}
      </ol>
    </div>
  );
}

/**
 * El avance de un tema, como anillo.
 *
 * Era una barra de 4 píxeles que se perdía dentro de la tarjeta. Un anillo
 * alrededor del porcentaje se lee de una pasada y aguanta estar repetido doce
 * veces en la misma pantalla sin volverse ruido, que es lo que le pasa a doce
 * barras horizontales apiladas.
 */
function AnilloAvance({ porcentaje, color }: { porcentaje: number; color: string }) {
  const r = 17;
  const circunferencia = 2 * Math.PI * r;
  const avance = circunferencia * (1 - Math.min(100, Math.max(0, porcentaje)) / 100);
  return (
    <span className="relative flex h-11 w-11 shrink-0 items-center justify-center">
      <svg viewBox="0 0 40 40" className="absolute inset-0 -rotate-90">
        <circle cx="20" cy="20" r={r} fill="none" stroke="var(--surface-hover)" strokeWidth="4" />
        <circle
          cx="20" cy="20" r={r} fill="none" stroke={color} strokeWidth="4"
          strokeLinecap="round" strokeDasharray={circunferencia}
          strokeDashoffset={avance}
        />
      </svg>
      <span className="relative text-[10px] font-bold tabular-nums">{porcentaje}%</span>
    </span>
  );
}

function NumbersIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M5 9h14M5 15h14M9 4L7 20M17 4l-2 16" />
    </svg>
  );
}

function AlgebraIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 6h4l4 12h4M4 18h4l1.5-4.5" />
    </svg>
  );
}

function GeometryIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round">
      <path d="M12 4l8 16H4z" />
      <circle cx="12" cy="14" r="2.2" />
    </svg>
  );
}

function DiceIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="3" />
      <circle cx="9" cy="9" r="1" fill="currentColor" stroke="none" />
      <circle cx="15" cy="9" r="1" fill="currentColor" stroke="none" />
      <circle cx="9" cy="15" r="1" fill="currentColor" stroke="none" />
      <circle cx="15" cy="15" r="1" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}
