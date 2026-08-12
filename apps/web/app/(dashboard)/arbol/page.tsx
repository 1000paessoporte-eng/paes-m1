import { getSkillTree } from "@/lib/api";
import { SkillTreeView } from "@/components/skill-tree/skill-tree-view";

export default async function ArbolHabilidadesPage() {
  let nodes;
  try {
    nodes = await getSkillTree();
  } catch {
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
      <div className="mt-8">
        <SkillTreeView nodes={nodes} />
      </div>
    </div>
  );
}
