"use client";

import { motion, useReducedMotion } from "framer-motion";
import { COLOR_PRUEBA } from "@/lib/colores-prueba";
import { BarraProgreso } from "@/components/ui/barra-progreso";
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

const GUTTER_X = 12; // centro del gutter de conectores, en px

interface SkillTreeViewProps {
  nodes: SkillNode[];
}

export function SkillTreeView({ nodes }: SkillTreeViewProps) {
  const nameByCode = new Map(nodes.map((n) => [n.code, n.name]));

  // El color sale de los propios nodos, no de una prop: el árbol de una prueba
  // solo trae nodos de esa prueba, y así ninguna pantalla puede pasarle un
  // color que no le corresponda. Es el MISMO color que el selector de ensayo,
  // que es lo que permite reconocer dónde se está sin leer el título.
  const colorPrueba = nodes.length
    ? COLOR_PRUEBA[nodes[0].subject as Subject]
    : "var(--accent)";

  // Solo los ejes que existen en esta prueba, en el orden canónico.
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

  return (
    <>
      {/* CUÁNTO LLEVAS DEL ÁRBOL ENTERO.
          La página no lo decía en ninguna parte: había que contar tarjetas
          verdes a ojo entre cuatro columnas. Un árbol de habilidades sin un
          marcador de avance es un menú, y lo que engancha de estos árboles es
          justamente ver la barra subir. */}
      <div className="mb-8 rounded-2xl border border-border bg-surface p-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <p className="font-display text-3xl leading-none font-bold">
            {dominados}
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

      <div
        className={cn(
          "grid grid-cols-1 gap-8 sm:grid-cols-2",
        // Tres ejes (Lectora, Ciencias, Historia) o cuatro (matemática): la
        // grilla se ajusta para que no queden columnas huérfanas.
        columns.length === 3 ? "xl:grid-cols-3" : "xl:grid-cols-4"
      )}
    >
        {columns.map((column) => (
          <TreeColumn
            key={column.axis}
            axis={column.axis}
            nodes={column.nodes}
            nameByCode={nameByCode}
            colorPrueba={colorPrueba}
          />
        ))}
      </div>
    </>
  );
}

interface Edge {
  id: string;
  y1: number;
  y2: number;
  active: boolean;
}

function TreeColumn({
  axis,
  nodes,
  nameByCode,
  colorPrueba,
}: {
  axis: SkillNode["axis"];
  nodes: SkillNode[];
  nameByCode: Map<string, string>;
  /** El color de la prueba a la que pertenece este árbol. */
  colorPrueba: string;
}) {
  const meta = AXIS_META[axis];
  const quieto = useReducedMotion();
  const listRef = useRef<HTMLOListElement>(null);
  const dotRefs = useRef<Map<string, HTMLSpanElement>>(new Map());
  const [edges, setEdges] = useState<Edge[]>([]);

  const measure = useCallback(() => {
    const list = listRef.current;
    if (!list) return;
    const listRect = list.getBoundingClientRect();
    const codesInColumn = new Set(nodes.map((n) => n.code));

    const nextEdges: Edge[] = [];
    for (const node of nodes) {
      for (const prereqCode of node.prerequisite_codes) {
        if (!codesInColumn.has(prereqCode)) continue; // conector solo dentro del mismo eje
        const fromDot = dotRefs.current.get(prereqCode);
        const toDot = dotRefs.current.get(node.code);
        if (!fromDot || !toDot) continue;
        const fromRect = fromDot.getBoundingClientRect();
        const toRect = toDot.getBoundingClientRect();
        nextEdges.push({
          id: `${prereqCode}->${node.code}`,
          y1: fromRect.top + fromRect.height / 2 - listRect.top,
          y2: toRect.top + toRect.height / 2 - listRect.top,
          active: node.status !== "locked",
        });
      }
    }
    setEdges(nextEdges);
  }, [nodes]);

  useLayoutEffect(() => {
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [measure]);

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

      <ol ref={listRef} className="relative flex flex-col gap-3">
        <svg className="pointer-events-none absolute inset-0 h-full w-full" aria-hidden="true">
          {/* Los conectores se DIBUJAN de arriba abajo, en el mismo orden en
              que se desbloquean los nodos. Es el único lugar del árbol donde
              el movimiento explica algo: muestra que hay un camino y hacia
              dónde va, que es justo lo que una lista de tarjetas no dice. */}
          {edges.map((e, i) => (
            <motion.line
              key={e.id}
              x1={GUTTER_X}
              y1={e.y1}
              x2={GUTTER_X}
              y2={e.y2}
              stroke={e.active ? colorPrueba : "var(--border-strong)"}
              strokeWidth={2}
              strokeDasharray={e.active ? undefined : "4 4"}
              strokeLinecap="round"
              initial={quieto ? false : { pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={
                quieto
                  ? { duration: 0 }
                  : { delay: 0.15 + i * 0.08, duration: 0.4, ease: "easeOut" }
              }
            />
          ))}
        </svg>

        {nodes.map((node, i) => {
          const locked = node.status === "locked";
          const mastered = node.status === "mastered";
          const pct = Math.round(node.accuracy * 100);
          // "Dominado" usa el color de la prueba porque es identidad --este
          // árbol--, mientras que "Desbloqueado" conserva el verde, que ahí
          // sí es estado. Es la regla de no mezclar identidad con estado.
          return (
            <motion.li
              key={node.code}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06, duration: 0.35, ease: "easeOut" }}
              style={{ "--color-prueba": colorPrueba } as React.CSSProperties}
              className="flex gap-3"
            >
              <div className="flex w-6 shrink-0 justify-center pt-4">
                <span
                  ref={(el) => {
                    if (el) dotRefs.current.set(node.code, el);
                    else dotRefs.current.delete(node.code);
                  }}
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
                      {node.has_lesson && (
                        <Link
                          href={`/aprender/${node.code}`}
                          className="mt-1.5 inline-block text-xs font-medium text-accent"
                        >
                          Leer la teoría igual
                        </Link>
                      )}
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
