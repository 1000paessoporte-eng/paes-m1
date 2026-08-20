import { cn } from "@paes-m1/utils";

/**
 * Cuánto llevas en esta pregunta, contra cuánto deberías.
 *
 * En la PAES mucha gente no falla por no saber: falla porque se quedó pegada
 * quince minutos en un ejercicio y dejó ocho sin responder. El cronómetro
 * general no ayuda con eso --dice cuánto queda en total, no si esta pregunta
 * en particular ya salió cara--.
 *
 * El presupuesto sale de la duración del intento dividida por sus preguntas,
 * así que respeta el ritmo que el alumno eligió: en modo exigente el número es
 * más chico, y eso es exactamente lo que pidió entrenar.
 *
 * NO es una alarma. Es un ejercicio de estudio, y un contador que grita cada
 * vez que alguien piensa de más enseña a apurarse, no a administrarse. Por eso
 * el aviso llega recién al doble del presupuesto, y llega como color y texto,
 * nunca como algo que interrumpa.
 */
export function RelojPregunta({
  msGastados,
  msPresupuesto,
}: {
  msGastados: number;
  msPresupuesto: number;
}) {
  if (msPresupuesto <= 0) return null;

  const excedido = msGastados > msPresupuesto;
  // El doble del presupuesto: a partir de ahí la pregunta ya le está costando
  // el tiempo de otra, que es cuando de verdad conviene saltarla y volver.
  const muyExcedido = msGastados > msPresupuesto * 2;

  return (
    <div
      className={cn(
        "flex items-baseline gap-1.5 rounded-lg px-2.5 py-1 text-sm tabular-nums leading-7 transition-colors duration-700",
        muyExcedido
          ? "bg-accent-warm/10 text-accent-warm-strong"
          : excedido
            ? "bg-warning/10 text-warning"
            : "text-muted"
      )}
      // No es aria-live: anunciar cada segundo sería insoportable con lector
      // de pantalla. El dato está en la etiqueta cuando se consulta.
      aria-label={`Llevas ${Math.round(msGastados / 1000)} segundos en esta pregunta, de ${Math.round(msPresupuesto / 1000)} recomendados`}
    >
      <span className="font-semibold">{reloj(msGastados)}</span>
      <span className="opacity-60">/ {reloj(msPresupuesto)}</span>
    </div>
  );
}

function reloj(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}
