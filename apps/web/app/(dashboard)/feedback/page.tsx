import { ComingSoon } from "@/components/coming-soon";

export default function SmartFeedbackPage() {
  return (
    <ComingSoon
      title="Smart Feedback"
      description="Autopsia del error por sub-eje temático: cada distractor trae la justificación exacta del error conceptual, con rutas de nivelación a tus nodos más débiles."
      icon={
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="9" />
          <circle cx="12" cy="12" r="5" />
          <circle cx="12" cy="12" r="1" fill="currentColor" />
        </svg>
      }
    />
  );
}
