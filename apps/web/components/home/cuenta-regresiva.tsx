"use client";

import { useEffect, useState } from "react";
import { FECHA_PAES } from "@/lib/paes-fecha";

/**
 * Los días, horas y minutos que faltan para la PAES, descontando en vivo.
 *
 * El número de días ya estaba en la página, quieto. Verlo moverse es lo que
 * convierte "faltan 102 días" en algo que se siente: la PAES tiene fecha y esa
 * fecha se acerca mientras miras la pantalla.
 *
 * El servidor pinta solo los días. Las horas y los minutos aparecen recién en
 * el navegador, y por una razón concreta: si el servidor los escribiera, el
 * HTML llegaría con una hora ya vencida y React marcaría diferencia al
 * hidratar. Los días son iguales en los dos lados, así que quien no tenga
 * JavaScript ve el dato importante igual.
 */
function faltan(hasta: Date, ahora: Date) {
  const ms = hasta.getTime() - ahora.getTime();
  if (ms <= 0) return null;
  return {
    dias: Math.floor(ms / 86400000),
    horas: Math.floor((ms % 86400000) / 3600000),
    minutos: Math.floor((ms % 3600000) / 60000),
    segundos: Math.floor((ms % 60000) / 1000),
  };
}

export function CuentaRegresiva() {
  const [restante, setRestante] = useState<ReturnType<typeof faltan>>(null);

  useEffect(() => {
    const tick = () => setRestante(faltan(FECHA_PAES, new Date()));
    tick();
    // Cada segundo: es un reloj, y un reloj que salta de minuto en minuto se
    // ve roto. El costo es un setState por segundo sobre cuatro números.
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  if (!restante) return null;

  return (
    <span className="tabular-nums">
      {restante.dias}
      <span className="text-muted"> d </span>
      {String(restante.horas).padStart(2, "0")}
      <span className="text-muted"> h </span>
      {String(restante.minutos).padStart(2, "0")}
      <span className="text-muted"> m </span>
      {String(restante.segundos).padStart(2, "0")}
      <span className="text-muted"> s</span>
    </span>
  );
}
