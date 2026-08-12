export default function DashboardAnaliticoPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Analítica</h1>
      <p className="mt-1 text-sm text-muted">
        Tiempo invertido vs. tasa de acierto, y rachas de práctica diaria.
      </p>
      {/* TODO: gráficos (recharts/visx) consumiendo GET /api/analytics/summary */}
    </div>
  );
}
