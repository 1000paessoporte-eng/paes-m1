"use client";

import { motion, useReducedMotion } from "framer-motion";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { BarraProgreso } from "@/components/ui/barra-progreso";

/**
 * La vista previa del resultado, animada al cargar la portada.
 *
 * Es la pieza que más peso carga en la página: no es un adorno del hero, es
 * LA pantalla que el estudiante viene a conseguir. Estaba dibujada y quieta,
 * así que se leía como una captura de pantalla.
 *
 * Se anima una sola cosa y de forma orquestada: el anillo se dibuja, el
 * puntaje sube y los cuatro ejes se llenan en cascada, en ese orden. Es la
 * secuencia real de terminar un ensayo —primero el número, después el
 * desglose— así que el movimiento explica el producto en vez de decorarlo. Por
 * eso está acá y no repartido por toda la portada: un momento orquestado se
 * recuerda, cinco efectos sueltos se ignoran.
 *
 * Nada de esto es necesario para entender la tarjeta: sin JavaScript o con
 * movimiento reducido, el anillo, el número y las barras salen ya en su valor
 * final. La animación ocurre encima de algo que ya está correcto.
 */

const EJES = [
  { nombre: "Números", valor: 82, color: "var(--accent)" },
  { nombre: "Álgebra y funciones", valor: 74, color: "var(--accent-2)" },
  { nombre: "Geometría", valor: 65, color: "var(--success)" },
  { nombre: "Probabilidad", valor: 58, color: "var(--warning)" },
] as const;

const PUNTAJE = 780;
const LOGRO = 0.78;

export function PuntajeMockup() {
  const quieto = useReducedMotion();
  const radio = 46;
  const circunferencia = 2 * Math.PI * radio;
  const destino = circunferencia * (1 - LOGRO);

  return (
    <div className="relative">
      <div className="float-chip absolute -top-4 -right-3 z-10 flex items-center gap-1.5 rounded-full border border-success/30 bg-background px-3 py-1.5 text-xs font-semibold text-success shadow-lg shadow-foreground/5 sm:-right-6">
        <UpIcon />
        +38 pts vs. tu último ensayo
      </div>

      <div className="rounded-2xl border border-border bg-surface p-6 shadow-xl shadow-foreground/5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted">Resultado de ejemplo</span>
          <span className="rounded-full bg-surface-hover px-2 py-0.5 text-[11px] text-muted">
            Ensayo #4
          </span>
        </div>

        <div className="mt-5 flex items-center gap-5">
          <svg
            width="104"
            height="104"
            viewBox="0 0 104 104"
            className="shrink-0 -rotate-90"
            aria-hidden
          >
            <circle cx="52" cy="52" r={radio} fill="none" stroke="var(--border)" strokeWidth="8" />
            <motion.circle
              cx="52"
              cy="52"
              r={radio}
              fill="none"
              stroke="var(--accent)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circunferencia}
              // Sin animación arranca —y se queda— en el valor final.
              initial={{ strokeDashoffset: quieto ? destino : circunferencia }}
              animate={{ strokeDashoffset: destino }}
              transition={
                quieto ? { duration: 0 } : { duration: 1.1, ease: [0.16, 1, 0.3, 1] }
              }
            />
          </svg>
          <div>
            <p className="text-3xl font-bold tracking-tight text-foreground">
              <NumeroAnimado valor={PUNTAJE} duracion={1.1} />
              <span className="text-base font-medium text-muted">/1000</span>
            </p>
            <p className="text-xs text-muted">Puntaje estimado</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3">
          {EJES.map((eje, i) => (
            <div key={eje.nombre}>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-foreground">{eje.nombre}</span>
                <span className="text-muted tabular-nums">{eje.valor}%</span>
              </div>
              {/* En cascada y DESPUÉS del anillo: primero el puntaje, después
                  el desglose, que es el orden en que se lee un resultado. */}
              <BarraProgreso
                porcentaje={eje.valor}
                color={eje.color}
                etiqueta={`${eje.nombre}: ${eje.valor}%`}
                alto="h-1.5"
                delay={0.75 + i * 0.12}
                alCargar
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function UpIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M6 15l6-6 6 6" />
    </svg>
  );
}
