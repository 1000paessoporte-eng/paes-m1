"use client";

import Link from "next/link";
import { BotonComprar } from "@/components/plan/boton-comprar";

/**
 * Lo que ve un alumno del plan Gratis cuando agota sus ensayos del mes.
 *
 * Antes esto era un mensaje de error técnico —"Verifica que la API esté
 * disponible"— que hacía parecer que el sitio estaba roto. Un tope alcanzado y
 * una caída del servidor son cosas distintas y no pueden verse igual.
 *
 * Es además el ÚNICO momento del producto en que alguien ya demostró que
 * quiere más: llegó al tope porque estuvo usándolo. Por eso acá está todo lo
 * que hace falta para decidir, sin un clic de por medio: qué cuesta, qué se
 * gana y cuándo se renueva si prefiere esperar. Antes decía "Ver el plan Pro"
 * y había que navegar a otra página para enterarse del precio.
 *
 * Tres decisiones sobre el tono. Se explica el motivo con el número exacto, se
 * ofrece una salida que no cuesta dinero —seguir aprendiendo, que en el plan
 * Gratis está completo— y recién después se ofrece pagar. Un muro que solo
 * dice "paga" convierte peor que uno que reconoce lo que la persona ya estaba
 * haciendo.
 */

/** Lo que Pro entrega de verdad. Los mismos dos puntos que la página de
 *  planes: si acá dijera más, sería el mismo problema que ya se arregló allá. */
const LO_QUE_SUMA = [
  "Ensayos sin límite, todos los que quieras rendir",
  "Hasta 10 carreras en Mi meta, comparadas entre sí",
] as const;

/** Cuándo vuelve a haber ensayos: el tope es por mes de calendario. */
function reinicio(ahora: Date = new Date()): string {
  const primero = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 1);
  return primero.toLocaleDateString("es-CL", { day: "numeric", month: "long" });
}

export function LimiteAlcanzado({
  motivo,
  onVolver,
}: {
  motivo: string;
  onVolver: () => void;
}) {
  return (
    <div className="mx-auto max-w-lg py-12">
      <div className="card-panel p-8">
        <div className="text-center">
          <span aria-hidden className="text-4xl text-accent-warm">
            ✦
          </span>

          <h1 className="mt-4 text-2xl font-semibold tracking-tight">
            Llegaste al tope de este mes
          </h1>

          <p className="mt-3 text-sm leading-relaxed text-muted">{motivo}</p>

          {/* La fecha exacta, no "el mes que viene": con ella, esperar es una
              decisión informada. Si faltan tres días quizá espere, y si faltan
              veinticinco sabe que la espera es real. */}
          <p className="mt-2 text-sm leading-relaxed text-muted">
            Tus 4 ensayos se renuevan el{" "}
            <strong className="text-foreground">{reinicio()}</strong>.
          </p>
        </div>

        <div className="mt-6 rounded-xl border border-accent/40 bg-accent/5 p-5">
          <div className="flex items-baseline justify-between gap-3">
            <h2 className="font-semibold">Seguir hoy con Pro</h2>
            <span className="text-lg font-bold tracking-tight">
              $9.990<span className="text-xs font-medium text-muted"> al mes</span>
            </span>
          </div>
          <ul className="mt-3 flex flex-col gap-1.5 text-sm text-muted">
            {LO_QUE_SUMA.map((linea) => (
              <li key={linea} className="flex gap-2">
                <span aria-hidden className="text-accent">
                  ✓
                </span>
                {linea}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-muted">
            Sin permanencia: cancelas cuando quieras. O el año completo por
            $89.900, que son nueve meses y no doce.
          </p>
          <div className="mt-4">
            <BotonComprar producto="pro_mensual" etiqueta="Contratar Pro por un mes" />
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3 text-center">
          <p className="text-sm leading-relaxed text-muted">
            Y si prefieres esperar, el árbol y las lecciones siguen completos:
            puedes seguir estudiando sin costo.
          </p>
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
