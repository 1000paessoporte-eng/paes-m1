"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, confirmarTarjeta, type MiPlan } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

type Estado = "confirmando" | "listo" | "error";

/**
 * A donde Flow devuelve al usuario cuando termina de registrar su tarjeta.
 *
 * A diferencia del pago puntual —que lo activa un webhook—, el registro de
 * tarjeta no tiene aviso de servidor a servidor: Flow devuelve al usuario acá y
 * este paso confirma con la API, que le pregunta a Flow si la tarjeta quedó.
 * Es idempotente, así que recargar no crea dos suscripciones.
 */
export function ConfirmarTarjeta() {
  const [estado, setEstado] = useState<Estado>("confirmando");
  const [plan, setPlan] = useState<MiPlan | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let vigente = true;
    confirmarTarjeta(getClientToken() ?? undefined)
      .then((p) => {
        if (!vigente) return;
        setPlan(p);
        setEstado("listo");
      })
      .catch((err) => {
        if (!vigente) return;
        setError(
          err instanceof ApiError && err.detail
            ? err.detail
            : "No pudimos confirmar tu tarjeta."
        );
        setEstado("error");
      });
    return () => {
      vigente = false;
    };
  }, []);

  if (estado === "confirmando") {
    return (
      <div className="card-panel p-8 text-center">
        <span aria-hidden className="text-4xl text-accent">
          ⏳
        </span>
        <h1 className="mt-4 text-2xl font-semibold tracking-tight">
          Activando tu prueba…
        </h1>
        <p className="mt-3 text-sm text-muted">Esto toma un segundo.</p>
      </div>
    );
  }

  if (estado === "error") {
    return (
      <div className="card-panel p-8 text-center">
        <span aria-hidden className="text-4xl text-danger">
          ✕
        </span>
        <h1 className="mt-4 text-2xl font-semibold tracking-tight">
          No pudimos activar tu prueba
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">{error}</p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link
            href="/planes"
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
          >
            Intentar de nuevo
          </Link>
        </div>
      </div>
    );
  }

  const vence = plan?.vence_el
    ? new Date(plan.vence_el).toLocaleDateString("es-CL", {
        day: "numeric",
        month: "long",
      })
    : null;

  return (
    <div className="card-panel p-8 text-center">
      <span aria-hidden className="text-4xl text-success">
        ✓
      </span>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">
        ¡Listo! Empezó tu prueba
      </h1>
      <p className="mt-3 text-sm leading-relaxed text-muted">
        Tienes Pro sin límites
        {vence && (
          <>
            {" "}hasta el <strong className="text-foreground">{vence}</strong>
          </>
        )}
        . Cuando termine la prueba se cobra el primer mes; puedes cancelar antes
        desde tu perfil sin que te cobren.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <Link
          href="/examen"
          className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
        >
          Rendir un ensayo
        </Link>
        <Link
          href="/perfil"
          className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium transition-colors hover:bg-surface-hover"
        >
          Ver mi plan
        </Link>
      </div>
    </div>
  );
}
