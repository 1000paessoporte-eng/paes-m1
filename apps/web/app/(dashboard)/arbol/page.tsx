import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getRecommendedNode, getSkillTree } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { SkillTreeView } from "@/components/skill-tree/skill-tree-view";

export const metadata = {
  title: "Árbol de Habilidades",
  description:
    "El temario de cada prueba como nodos: primero se estudia la teoría y después se practica.",
};

/** Las cinco pruebas. Cada una tiene su propio árbol, con sus ejes. */
const PRUEBAS = [
  { id: "lectora", label: "Competencia Lectora" },
  { id: "m1", label: "Matemática M1" },
  { id: "m2", label: "Matemática M2" },
  { id: "ciencias", label: "Ciencias" },
  { id: "historia", label: "Historia" },
] as const;

const PRUEBAS_VALIDAS = PRUEBAS.map((p) => p.id) as readonly string[];

export default async function ArbolHabilidadesPage({
  searchParams,
}: PageProps<"/arbol">) {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  const params = await searchParams;

  // La prueba viaja en la URL y no en estado local: así el estudiante puede
  // guardar el enlace de "el árbol de Ciencias" y volver ahí directo.
  const pedida = typeof params.prueba === "string" ? params.prueba : "m1";
  const prueba = PRUEBAS_VALIDAS.includes(pedida) ? pedida : "m1";

  let nodes;
  let recommended;
  try {
    [nodes, recommended] = await Promise.all([
      getSkillTree(token, prueba),
      getRecommendedNode(token),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/arbol");
    return (
      <div>
        <h1 className="text-2xl font-semibold">Árbol de Habilidades</h1>
        <p className="mt-4 rounded-lg border border-danger/40 bg-danger/10 p-4 text-sm text-danger">
          No se pudo conectar con la API. Verifica que apps/api esté
          corriendo en {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}.
        </p>
      </div>
    );
  }

  const conLeccion = nodes.filter((n) => n.has_lesson).length;

  // Una prueba sin ningún nodo practicable es un callejón sin salida: el
  // estudiante ve una pantalla de tarjetas grises y ninguna explicación. Pasa
  // en M2, cuyos once nodos dependen todos de temas de M1 — que es correcto
  // pedagógicamente, pero hay que decirlo y mostrar por dónde empezar.
  const practicables = nodes.filter((n) => n.status !== "locked");
  const prerrequisitos = [
    ...new Set(nodes.flatMap((n) => n.prerequisite_codes)),
  ].filter((code) => !nodes.some((n) => n.code === code));

  return (
    <div>
      <h1 className="text-2xl font-semibold">Árbol de Habilidades</h1>
      <p className="mt-1 text-sm text-muted">
        Cada tema trae primero la teoría con un ejemplo resuelto, y después las
        preguntas para practicarlo.
      </p>

      {/* ── Prueba ──────────────────────────────────────────────────── */}
      <nav className="mt-5 flex flex-wrap gap-2" aria-label="Prueba">
        {PRUEBAS.map((p) => {
          const activa = p.id === prueba;
          return (
            <Link
              key={p.id}
              href={`/arbol?prueba=${p.id}`}
              aria-current={activa ? "page" : undefined}
              className={
                "rounded-full border px-4 py-1.5 text-sm font-medium transition-colors " +
                (activa
                  ? "border-accent bg-accent/10 text-accent"
                  : "border-border text-muted hover:bg-surface-hover hover:text-foreground")
              }
            >
              {p.label}
            </Link>
          );
        })}
      </nav>

      {/* Decirlo es más honesto que dejar que lo descubra clic a clic: hoy
          solo M1 tiene la teoría escrita. */}
      {conLeccion === 0 && (
        <p className="mt-4 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-muted">
          Los temas de esta prueba todavía no tienen la teoría escrita: por
          ahora llevan directo a practicar. Matemática M1 sí la tiene completa.
        </p>
      )}

      {nodes.length > 0 && practicables.length === 0 && (
        <div className="mt-5 rounded-xl border border-warning/40 bg-warning/10 p-5">
          <p className="text-sm font-semibold text-warning">
            Todavía no puedes practicar estos temas
          </p>
          <p className="mt-2 text-sm leading-relaxed text-foreground">
            {prerrequisitos.length > 0
              ? "Esta prueba se construye sobre otra: cada tema de acá exige dominar antes su equivalente en Competencia Matemática M1. Practica M1 hasta llegar al 75% de acierto en esos temas y estos se abren solos."
              : "Cada tema de esta prueba exige dominar antes el que viene más abajo en el árbol."}
          </p>
          <Link
            href="/arbol?prueba=m1"
            className="btn-warm mt-4 inline-block rounded-lg px-4 py-2 text-sm font-semibold text-on-fill"
          >
            Ir al árbol de M1 →
          </Link>
        </div>
      )}

      {recommended && (
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-accent/40 bg-accent/10 px-5 py-4">
          <div>
            <p className="text-xs font-medium text-accent">Recomendado para ti</p>
            <p className="mt-1 text-sm text-foreground">
              {recommended.attempts === 0
                ? `Aún no has practicado "${recommended.name}". Es un buen próximo paso.`
                : `Tu punto más débil ahora es "${recommended.name}" (${Math.round(recommended.accuracy * 100)}% de acierto).`}
            </p>
          </div>
          <Link
            href={
              recommended.has_lesson
                ? `/aprender/${recommended.code}`
                : `/practicar/${recommended.code}`
            }
            className="btn-glow shrink-0 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground"
          >
            {recommended.has_lesson ? "Estudiar este tema" : "Practicar"}
          </Link>
        </div>
      )}

      <div className="mt-8">
        <SkillTreeView nodes={nodes} />
      </div>
    </div>
  );
}
