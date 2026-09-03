"use client";

import Link from "next/link";
import { useState, useSyncExternalStore } from "react";
import type { MiPlan } from "@/lib/api";
import { BotonTrial } from "@/components/plan/boton-trial";

/**
 * La franja de Pro en el panel del alumno del plan Gratis.
 *
 * Existe porque el aviso que había —`AnuncioPlanes`— es una ventana modal que
 * sale como máximo UNA vez al día y además alterna con el aviso del premio.
 * En la práctica eso significaba que alguien del plan Gratis veía la oferta
 * día por medio, y solo si ya había rendido un ensayo; el resto del tiempo el
 * producto no le decía en ninguna parte que existiera un plan de pago. Se
 * podía usar la plataforma semanas enteras sin enterarse.
 *
 * Esta franja resuelve eso sin volver a la ventana modal, que es el formato
 * que la gente aprende a cerrar sin leer. Va en el flujo de la página, ocupa
 * poco, y se puede cerrar: cerrada, vuelve al día siguiente. La diferencia con
 * el modal no es la frecuencia, es que no interrumpe.
 *
 * Se dibuja SOLO para el plan Gratis. A quien ya paga no se le ofrece lo que
 * ya tiene.
 */

const CLAVE = "franja-pro-cerrada";

function hoy(): string {
  const d = new Date();
  const mes = String(d.getMonth() + 1).padStart(2, "0");
  const dia = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mes}-${dia}`;
}

function leerCerrada(): string | null {
  try {
    return localStorage.getItem(CLAVE);
  } catch {
    // Modo privado o almacenamiento lleno. Una franja no vale romper el panel.
    return null;
  }
}

export function FranjaPro({ plan }: { plan: MiPlan }) {
  // useSyncExternalStore y no useEffect: localStorage no existe en el
  // servidor, y esta es la forma que ofrece React para leer estado externo sin
  // provocar un desajuste de hidratación. En el servidor devuelve null y la
  // franja aparece recién cuando el navegador resuelve si tocaba o no.
  const cerradaEl = useSyncExternalStore(
    () => () => {},
    () => leerCerrada(),
    () => null,
  );
  const [cerradaAhora, setCerradaAhora] = useState(false);

  if (plan.plan !== "gratis") return null;
  if (cerradaAhora || cerradaEl === hoy()) return null;

  function cerrar() {
    try {
      localStorage.setItem(CLAVE, hoy());
    } catch {
      // Si no se puede escribir, vuelve a salir al recargar. Molesto pero
      // inofensivo.
    }
    setCerradaAhora(true);
  }

  const usados = plan.ensayos_usados;
  const limite = plan.ensayos_limite;
  const restantes = limite != null ? Math.max(0, limite - usados) : null;

  return (
    <div className="border-b border-accent/30 bg-accent/5">
      <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center gap-x-6 gap-y-3 px-4 py-3 sm:px-6">
        <div className="min-w-[15rem] flex-1">
          <p className="text-sm font-semibold tracking-tight">
            {plan.trial_disponible
              ? `Prueba el plan Pro ${plan.trial_dias} días gratis`
              : "Ensayos sin límite con el plan Pro"}
          </p>
          {/* Antes que la oferta, dónde va parado. Un aviso que parte por el
              precio es publicidad; uno que parte por el consumo real es
              información, y solo después ofrece la salida. */}
          <p className="mt-0.5 text-xs leading-relaxed text-muted">
            {restantes === 0
              ? "Llegaste al tope de ensayos de este mes."
              : restantes != null
                ? `Llevas ${usados} de ${limite} ensayos de este mes.`
                : "Ensayos sin límite de las cinco pruebas."}{" "}
            Pro los deja sin tope y abre las 10 carreras en Mi meta.
          </p>
        </div>

        <div className="flex min-w-[13rem] shrink-0 items-center gap-3">
          <div className="flex-1">
            {plan.trial_disponible ? (
              <BotonTrial
                dias={plan.trial_dias}
                monto={plan.trial_monto}
                compacto
              />
            ) : (
              <Link
                href="/planes"
                className="btn-glow block rounded-lg px-3 py-2 text-center text-xs font-semibold text-accent-foreground"
              >
                Ver el plan Pro
              </Link>
            )}
          </div>
          <button
            type="button"
            onClick={cerrar}
            aria-label="Cerrar este aviso por hoy"
            className="flex h-7 w-7 shrink-0 items-center justify-center self-start rounded-full text-muted transition-colors hover:bg-surface-hover hover:text-foreground"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.4"
              strokeLinecap="round"
              aria-hidden
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
