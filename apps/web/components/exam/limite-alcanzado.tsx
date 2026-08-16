"use client";

import Link from "next/link";

/**
 * Lo que ve un alumno del plan Gratis cuando agota sus ensayos del mes.
 *
 * Antes esto era un mensaje de error técnico —"Verifica que la API esté
 * disponible"— que hacía parecer que el sitio estaba roto. Un tope alcanzado y
 * una caída del servidor son cosas distintas y no pueden verse igual: la
 * primera es una invitación a comprar, la segunda hace que la persona se vaya
 * pensando que el producto falla.
 *
 * Tres decisiones sobre el tono. Se explica el motivo con el número exacto, se
 * ofrece una salida que no cuesta dinero —seguir aprendiendo, que en el plan
 * Gratis está completo— y recién después se ofrece pagar. Un muro que solo
 * dice "paga" convierte peor que uno que reconoce lo que la persona ya estaba
 * haciendo.
 */
export function LimiteAlcanzado({
  motivo,
  onVolver,
}: {
  motivo: string;
  onVolver: () => void;
}) {
  return (
    <div className="mx-auto max-w-lg py-12">
      <div className="card-panel p-8 text-center">
        <span aria-hidden className="text-4xl text-accent-warm">
          ✦
        </span>

        <h1 className="mt-4 text-2xl font-semibold tracking-tight">
          Llegaste al tope de este mes
        </h1>

        <p className="mt-3 text-sm leading-relaxed text-muted">{motivo}</p>

        <p className="mt-4 text-sm leading-relaxed text-muted">
          Mientras tanto, el árbol de habilidades y las lecciones siguen
          completos: puedes seguir estudiando sin costo y volver el mes que
          viene con tus ensayos renovados.
        </p>

        <div className="mt-6 flex flex-col gap-3">
          <Link
            href="/planes"
            className="btn-warm rounded-lg px-5 py-3 text-sm font-semibold text-on-fill"
          >
            Ver el plan Pro
          </Link>
          <Link
            href="/arbol"
            className="rounded-lg border border-border px-5 py-3 text-sm font-medium transition-colors hover:bg-surface-hover"
          >
            Seguir aprendiendo gratis
          </Link>
          <button
            type="button"
            onClick={onVolver}
            className="text-sm text-muted underline-offset-4 hover:text-foreground hover:underline"
          >
            Volver
          </button>
        </div>
      </div>
    </div>
  );
}
