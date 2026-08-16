import { cookies } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";
import { ApiError, getLesson, getSkillNode, type Lesson, type SkillNode } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { LeccionView } from "@/components/skill-tree/leccion-view";

/**
 * La teoría de un nodo del árbol: lo que se estudia antes de practicar.
 *
 * Un nodo puede no tener lección todavía. En ese caso no se muestra una página
 * vacía ni un error: se lleva directo a practicar, que es lo que el estudiante
 * venía a hacer.
 */
export default async function AprenderNodoPage({
  params,
}: PageProps<"/aprender/[code]">) {
  const { code } = await params;
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let leccion: Lesson | null = null;
  let nodo: SkillNode | null = null;
  let fallo: "sesion" | "sin-leccion" | "api" | null = null;

  try {
    [leccion, nodo] = await Promise.all([
      getLesson(code, token),
      getSkillNode(code, token).catch(() => null),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) fallo = "sesion";
    else if (err instanceof ApiError && err.status === 404) fallo = "sin-leccion";
    else fallo = "api";
  }

  // Los redirect van FUERA del catch: `redirect` funciona lanzando una
  // excepción, y llamarlo dentro del bloque que atrapa excepciones deja el
  // control de flujo a merced de quién capture primero.
  if (fallo === "sesion") redirect(`/login?next=/aprender/${code}`);
  if (fallo === "sin-leccion") redirect(`/practicar/${code}`);

  if (fallo === "api" || leccion === null) {
    return (
      <div className="mx-auto max-w-lg text-center">
        <h1 className="text-xl font-semibold">No se pudo cargar la lección</h1>
        <p className="mt-3 text-sm text-muted">
          Vuelve a intentarlo en unos segundos.
        </p>
        <Link
          href="/arbol"
          className="mt-6 inline-block text-sm text-accent underline-offset-4 hover:underline"
        >
          Volver al árbol
        </Link>
      </div>
    );
  }

  return <LeccionView leccion={leccion} yaPracticado={(nodo?.attempts ?? 0) > 0} />;
}
