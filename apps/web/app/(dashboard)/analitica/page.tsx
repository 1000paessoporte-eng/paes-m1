import { ComingSoon } from "@/components/coming-soon";

export default function DashboardAnaliticoPage() {
  return (
    <ComingSoon
      title="Dashboard Analítico"
      description="Tiempo invertido vs. tasa de acierto, y rachas de práctica diaria, para saber exactamente dónde enfocar tu próxima sesión de estudio."
      icon={
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 20V10M12 20V4M20 20v-7" />
        </svg>
      }
    />
  );
}
