import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getOnboarding, getRecommendedNode, getSkillTree } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { SkillTreeView } from "@/components/skill-tree/skill-tree-view";
import { COLOR_PRUEBA } from "@/lib/colores-prueba";

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
  // guardar el enlace de "el árbol de Ciencias" y volver ahí directo. Sin
  // parámetro se abre la que dijo que va a rendir en el cuestionario de
  // bienvenida, no M1 por defecto: preguntarle y después ignorarlo sería peor
  // que no preguntar.
  const preferida = await getOnboarding(token)
    .then((o) => o.pruebas_objetivo?.[0])
    .catch(() => undefined);
  const pedida =
    typeof params.prueba === "string" ? params.prueba : (preferida ?? "m1");
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
  // El color de la prueba que se está mirando: el mismo del árbol, del
  // selector de ensayo y del titular de la portada.
  const colorPrueba = COLOR_PRUEBA[prueba as keyof typeof COLOR_PRUEBA];

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
            Estos temas se construyen sobre otros
          </p>
          <p className="mt-2 text-sm leading-relaxed text-foreground">
            {prerrequisitos.length > 0
              ? "Cada tema de acá se apoya en su equivalente de Competencia Matemática M1. Lo recomendable es dominar M1 primero —al 75% de acierto— y estos se abren solos. Pero si vas a rendir esta prueba y quieres entrar ya, cada tarjeta tiene un «Practicar igual»."
              : "Cada tema de esta prueba se apoya en el que viene más abajo en el árbol. Puedes practicarlos igual desde cada tarjeta, aunque conviene seguir el orden."}
          </p>
          <Link
            href="/arbol?prueba=m1"
            className="btn-glow mt-4 inline-block rounded-lg px-4 py-2 text-sm font-semibold text-accent-foreground"
          >
            Ir al árbol de M1 →
          </Link>
        </div>
      )}

      {/* LO QUE HAY QUE HACER AHORA.
          Era una barra gris del mismo peso que todo lo demás. Es la única
          decisión que la pantalla toma POR el alumno --entre quince temas,
          cuál conviene ahora-- y es lo que evita el "no sé por dónde empezar"
          que hace que la gente cierre la pestaña. Ahora manda: nombre grande,
          el porqué en una línea, y la acción al lado. */}
      {recommended && (
        <div
          className="mt-6 overflow-hidden rounded-2xl border-2 bg-surface"
          style={{ borderColor: `color-mix(in srgb, ${colorPrueba} 45%, transparent)` }}
        >
          <div className="flex flex-wrap items-end justify-between gap-5 p-5 sm:p-6">
            <div className="min-w-0">
              <p
                className="text-xs font-semibold tracking-wide uppercase"
                style={{ color: colorPrueba }}
              >
                Empieza por acá
              </p>
              <p className="font-display mt-1.5 text-2xl leading-tight font-bold text-balance sm:text-3xl">
                {recommended.name}
              </p>
              <p className="mt-2 max-w-xl text-sm text-muted">
                {recommended.attempts === 0
                  ? "Todavía no lo practicas, y es el que abre más temas del árbol."
                  : `Es tu punto más débil ahora: ${Math.round(recommended.accuracy * 100)}% de acierto en ${recommended.attempts} ${recommended.attempts === 1 ? "respuesta" : "respuestas"}.`}
              </p>
            </div>
            <div className="flex shrink-0 flex-wrap gap-2">
              <Link
                href={`/practicar/${recommended.code}`}
                className="rounded-lg px-5 py-2.5 text-sm font-semibold text-on-fill transition hover:opacity-90"
                style={{ backgroundColor: colorPrueba }}
              >
                Practicar ahora
              </Link>
              {recommended.has_lesson && (
                <Link
                  href={`/aprender/${recommended.code}`}
                  className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium transition hover:bg-surface-hover"
                >
                  Leer la teoría
                </Link>
              )}
            </div>
          </div>
        </div>
      )}

      {/* HISTORIA ENTRENA HABILIDADES, NO CONTENIDO. Y hay que decirlo.
          Comparado con el temario oficial de Admisión 2027, el árbol de
          Historia cubre las tres habilidades que evalúa la prueba —análisis
          de fuentes, pensamiento temporal, pensamiento crítico— y ninguno de
          sus temas: Estado-nación del siglo XIX, totalitarismos, Guerra Fría,
          dictaduras y violación de DD.HH. Medido sobre las 195 preguntas del
          banco: cero mencionan "siglo XIX", "Guerra Fría" o "totalitarismo".

          Es una decisión tomada, no un olvido: ningún script puede verificar
          que una afirmación histórica sea cierta, y el banco se verifica
          entero antes de publicarse. Pero un alumno que abre este árbol
          asume que está viendo el temario, y llega a la prueba sin haber
          estudiado la mitad que sí entra. Decírselo le cuesta un párrafo y le
          ahorra esa sorpresa. */}
      {prueba === "historia" && (
        <p className="mt-5 rounded-lg border border-warning/40 bg-warning/10 px-4 py-3 text-sm leading-relaxed">
          <strong className="font-semibold">
            Acá entrenas las habilidades, no los contenidos.
          </strong>{" "}
          La PAES de Historia evalúa análisis de fuentes, pensamiento temporal
          y pensamiento crítico, y eso es lo que practicas en este árbol. Los
          contenidos del temario —el siglo XIX, la Guerra Fría, las dictaduras
          y los Derechos Humanos— no están en nuestro banco todavía: esos los
          tienes que estudiar aparte.
        </p>
      )}

      <div className="mt-8">
        <SkillTreeView nodes={nodes} />
      </div>
    </div>
  );
}
