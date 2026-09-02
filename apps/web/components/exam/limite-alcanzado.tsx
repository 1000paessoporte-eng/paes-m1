"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BotonComprar } from "@/components/plan/boton-comprar";
import { BotonTrial } from "@/components/plan/boton-trial";
import { getMiPlan, type MiPlan } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

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
 *
 * Si a esta persona todavía le corresponde la prueba gratis, es ACÁ donde más
 * sentido tiene ofrecérsela: ya demostró que quiere seguir y el muro es el
 * único punto del producto donde eso es un hecho y no una suposición. Pedirle
 * $9.990 en ese momento, cuando existe una forma de seguir hoy sin pagar, es
 * cobrar por la puerta en vez de por el producto.
 *
 * El plan se consulta acá dentro y no llega por prop: este muro aparece en un
 * estado poco frecuente, y hacer que todo el flujo del ensayo cargue el plan
 * para un caso que casi nunca ocurre sería pagar en cada ensayo por algo que
 * se usa una vez al mes. Mientras la consulta no vuelve se muestra el camino
 * de pago de siempre, que es correcto para cualquiera.
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
  const [plan, setPlan] = useState<MiPlan | null>(null);

  useEffect(() => {
    let vigente = true;
    // Si la consulta falla, el muro se dibuja igual con el camino de pago: un
    // tope alcanzado no puede convertirse en una pantalla rota.
    getMiPlan(getClientToken() ?? undefined)
      .then((p) => {
        if (vigente) setPlan(p);
      })
      .catch(() => {});
    return () => {
      vigente = false;
    };
  }, []);

  const ofrecerTrial = Boolean(plan?.trial_disponible);

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
              {ofrecerTrial ? (
                <>
                  Gratis
                  <span className="text-xs font-medium text-muted">
                    {" "}
                    {plan!.trial_dias} días
                  </span>
                </>
              ) : (
                <>
                  $9.990
                  <span className="text-xs font-medium text-muted"> al mes</span>
                </>
              )}
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
          {ofrecerTrial ? (
            <>
              {/* Las condiciones del cobro viajan dentro de BotonTrial: la
                  fecha del primer cobro, el monto y que se pide tarjeta. No se
                  repiten acá para no decirlas dos veces y distinto. */}
              <BotonTrial dias={plan!.trial_dias} monto={plan!.trial_monto} />
              <p className="mt-3 text-center text-xs text-muted">
                ¿Prefieres pagar de una vez?{" "}
                <Link href="/planes" className="text-accent hover:underline">
                  Ver los planes
                </Link>
              </p>
            </>
          ) : (
            <>
              <p className="mt-3 text-xs text-muted">
                Sin permanencia: cancelas cuando quieras. O el año completo por
                $89.900, que son nueve meses y no doce.
              </p>
              <div className="mt-4">
                <BotonComprar
                  producto="pro_mensual"
                  etiqueta="Contratar Pro por un mes"
                />
              </div>
            </>
          )}
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
