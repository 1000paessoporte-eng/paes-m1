"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

/**
 * El anuncio del premio al puntaje nacional, al entrar al panel.
 *
 * Tres decisiones que hacen la diferencia entre un anuncio y una molestia:
 *
 * 1. **Se muestra una sola vez.** Un modal en cada inicio de sesión se cierra
 *    sin leer a la segunda vez y deja al estudiante peleado con la aplicación.
 *    La versión va en la clave guardada, así que se puede lanzar otro anuncio
 *    más adelante sin volver a mostrar este.
 *
 * 2. **Aparece después de un instante**, no encima de la pantalla en blanco:
 *    quien entra apurado a rendir un ensayo alcanza a ver dónde está parado
 *    antes de que algo lo interrumpa.
 *
 * 3. **Muestra el progreso real del estudiante**, no solo la promesa. Ver
 *    "llevas 19 de 30 ensayos" convierte un aviso publicitario en algo suyo, y
 *    el que va en 0 ve exactamente qué tendría que hacer.
 */

const CLAVE = "anuncio-premio-v1";
const ESPERA_MS = 900;

export interface ProgresoPremio {
  /** Ensayos terminados de 34 preguntas o más. */
  ensayosCompletos: number;
  /** Días distintos con práctica registrada. */
  diasPracticados: number;
}

const META_ENSAYOS = 30;
const META_DIAS = 90;

export function AnuncioPremio({ progreso }: { progreso: ProgresoPremio }) {
  const [abierto, setAbierto] = useState(false);
  const quieto = useReducedMotion();
  const cerrarRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (localStorage.getItem(CLAVE)) return;
    const id = setTimeout(() => setAbierto(true), ESPERA_MS);
    return () => clearTimeout(id);
  }, []);

  useEffect(() => {
    if (!abierto) return;
    // El foco entra al diálogo para que se pueda cerrar con el teclado sin
    // recorrer toda la página detrás.
    cerrarRef.current?.focus();
    function alPresionar(e: KeyboardEvent) {
      if (e.key === "Escape") cerrar();
    }
    document.addEventListener("keydown", alPresionar);
    return () => document.removeEventListener("keydown", alPresionar);
  }, [abierto]);

  function cerrar() {
    localStorage.setItem(CLAVE, new Date().toISOString());
    setAbierto(false);
  }

  const faltanEnsayos = Math.max(0, META_ENSAYOS - progreso.ensayosCompletos);
  const faltanDias = Math.max(0, META_DIAS - progreso.diasPracticados);

  return (
    <AnimatePresence>
      {abierto && (
        <motion.div
          className="fixed inset-0 z-50 flex items-end justify-center bg-foreground/40 p-4 backdrop-blur-sm sm:items-center"
          initial={quieto ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={cerrar}
        >
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="titulo-premio"
            onClick={(e) => e.stopPropagation()}
            initial={quieto ? false : { opacity: 0, y: 24, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="card-panel relative w-full max-w-lg overflow-hidden p-6 sm:p-7"
          >
            <button
              ref={cerrarRef}
              type="button"
              onClick={cerrar}
              aria-label="Cerrar el anuncio"
              className="absolute top-3 right-3 flex h-8 w-8 items-center justify-center rounded-full text-muted transition-colors hover:bg-surface-hover hover:text-foreground"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                aria-hidden
              >
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>

            <span className="inline-block rounded-full bg-accent-warm/15 px-2.5 py-1 text-[11px] font-semibold text-accent-warm-strong">
              Nuevo · para estudiantes con plan Pro
            </span>

            <h2
              id="titulo-premio"
              className="mt-3 text-2xl font-bold tracking-tight sm:text-3xl"
            >
              $500.000 si sacas puntaje nacional
            </h2>

            <p className="mt-2 text-sm leading-relaxed text-muted">
              Si obtienes 1.000 puntos en cualquiera de las cinco pruebas PAES y
              preparaste esa prueba acá, te entregamos medio millón de pesos. No
              es un sorteo: se gana rindiendo.
            </p>

            {/* Lo que lo vuelve suyo: dónde va con los requisitos que ya
                puede empezar a cumplir hoy. */}
            <div className="mt-5 rounded-xl border border-border bg-surface p-4">
              <p className="text-xs font-medium text-muted">Tu avance hasta ahora</p>
              <div className="mt-3 flex flex-col gap-3">
                <Requisito
                  hecho={progreso.ensayosCompletos}
                  meta={META_ENSAYOS}
                  etiqueta="ensayos completos"
                  falta={
                    faltanEnsayos === 0
                      ? "Requisito cumplido"
                      : `Te faltan ${faltanEnsayos}`
                  }
                />
                <Requisito
                  hecho={progreso.diasPracticados}
                  meta={META_DIAS}
                  etiqueta="días con práctica"
                  falta={
                    faltanDias === 0 ? "Requisito cumplido" : `Te faltan ${faltanDias}`
                  }
                />
              </div>
              <p className="mt-3 text-xs leading-relaxed text-muted">
                Falta además tener plan Pro por 6 meses, que empieza a contar
                cuando los planes estén disponibles.
              </p>
            </div>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href="/premio"
                onClick={cerrar}
                className="btn-warm rounded-lg px-5 py-2.5 text-sm font-semibold text-on-fill"
              >
                Ver las bases →
              </Link>
              <button
                type="button"
                onClick={cerrar}
                className="rounded-lg border border-border px-4 py-2.5 text-sm font-medium transition-colors hover:bg-surface-hover"
              >
                Ahora no
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Requisito({
  hecho,
  meta,
  etiqueta,
  falta,
}: {
  hecho: number;
  meta: number;
  etiqueta: string;
  falta: string;
}) {
  const pct = Math.min(100, (hecho / meta) * 100);
  const listo = hecho >= meta;

  return (
    <div>
      <div className="flex items-baseline justify-between gap-3 text-sm">
        <span className="tabular-nums">
          <strong>{hecho}</strong>
          <span className="text-muted"> de {meta} </span>
          <span className="text-muted">{etiqueta}</span>
        </span>
        <span
          className={
            "shrink-0 text-xs font-medium " + (listo ? "text-success" : "text-muted")
          }
        >
          {falta}
        </span>
      </div>
      <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-surface-hover">
        <div
          className="h-full rounded-full transition-[width] duration-700"
          style={{
            width: `${pct}%`,
            background: listo ? "var(--success)" : "var(--accent)",
          }}
        />
      </div>
    </div>
  );
}
