import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getRecommendedNode, getSkillTree } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { SkillTreeView } from "@/components/skill-tree/skill-tree-view";

export default async function ArbolHabilidadesPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let nodes;
  let recommended;
  try {
    [nodes, recommended] = await Promise.all([
      getSkillTree(token),
      getRecommendedNode(token),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login");
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

  return (
    <div>
      <h1 className="text-2xl font-semibold">Árbol de Habilidades</h1>
      <p className="mt-1 text-sm text-muted">
        Números, Álgebra, Geometría y Probabilidad como nodos desbloqueables.
      </p>

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
            href={`/practicar/${recommended.code}`}
            className="btn-glow shrink-0 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground"
          >
            Practicar
          </Link>
        </div>
      )}

      <div className="mt-8">
        <SkillTreeView nodes={nodes} />
      </div>
    </div>
  );
}
