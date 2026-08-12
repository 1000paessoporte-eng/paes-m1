export default function ArbolHabilidadesPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Árbol de Habilidades</h1>
      <p className="mt-1 text-sm text-muted">
        Números, Álgebra, Geometría y Probabilidad como nodos desbloqueables.
      </p>
      {/* TODO: render del árbol (React Flow / SVG custom) consumiendo
          GET /api/skill-tree del backend */}
    </div>
  );
}
