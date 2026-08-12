import { ComingSoon } from "@/components/coming-soon";

export default function ModoExamenPage() {
  return (
    <ComingSoon
      title="Modo Examen Focus"
      description="SPA de alto rendimiento, atajos de teclado y temporizador exacto de 2h 20m, con tracking silencioso en milisegundos por pregunta."
      icon={
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="13" r="8" />
          <path d="M12 9v4l3 2M9 2h6M12 2v2" />
        </svg>
      }
    />
  );
}
