"use client";

import Link from "next/link";
import { useState } from "react";
import type { MiPlan, Productos } from "@/lib/api";
import { ApiError, cancelarPlan, canjearCodigo, iniciarPago } from "@/lib/api";
import { getClientToken } from "@/lib/auth";
import { BarraProgreso } from "@/components/ui/barra-progreso";
import { BotonTrial } from "@/components/plan/boton-trial";

/**
 * El plan del estudiante y lo que le queda de él.
 *
 * Muestra el consumo aunque el límite todavía no bloquee: ver "2 de 4 ensayos
 * este mes" enseña que el plan tiene un tope mucho antes de chocar con él, y
 * quien choca sin aviso previo no compra, se enoja.
 */

const NOMBRE: Record<string, string> = {
  gratis: "Plan Gratis",
  pro: "Plan Pro",
  colegios: "Plan Colegios",
};

export function MiPlanPanel({
  inicial,
  productos,
}: {
  inicial: MiPlan;
  productos?: Productos;
}) {
  const [plan, setPlan] = useState(inicial);
  const [pagando, setPagando] = useState<string | null>(null);
  const [errorPago, setErrorPago] = useState<string | null>(null);
  const [codigo, setCodigo] = useState("");
  const [cancelando, setCancelando] = useState(false);
  const [errorCancelar, setErrorCancelar] = useState<string | null>(null);
  const [canjeando, setCanjeando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);

  const limite = plan.ensayos_limite;
  const usados = plan.ensayos_usados;
  const restantes = limite != null ? Math.max(0, limite - usados) : null;

  async function canjear(e: React.FormEvent) {
    e.preventDefault();
    if (codigo.trim().length < 3) return;
    setCanjeando(true);
    setError(null);
    setExito(false);
    try {
      setPlan(await canjearCodigo(codigo.trim(), getClientToken() ?? undefined));
      setCodigo("");
      setExito(true);
    } catch (err) {
      // El motivo se muestra tal cual lo da la API: "ya venció" y "ya se agotó"
      // son cosas distintas, y esconderlas tras un error genérico solo genera
      // correos a soporte.
      setError(
        err instanceof ApiError && err.detail
          ? err.detail
          : "No se pudo canjear ese código."
      );
    } finally {
      setCanjeando(false);
    }
  }

  function enTexto(iso: string): string {
    return new Date(iso).toLocaleDateString("es-CL", {
      day: "numeric",
      month: "long",
    });
  }

  async function cancelar() {
    setCancelando(true);
    setErrorCancelar(null);
    try {
      setPlan(await cancelarPlan(getClientToken() ?? undefined));
    } catch (err) {
      setErrorCancelar(
        err instanceof ApiError && err.detail
          ? err.detail
          : "No se pudo cancelar. Inténtalo de nuevo."
      );
    } finally {
      setCancelando(false);
    }
  }

  async function comprar(producto: string) {
    setPagando(producto);
    setErrorPago(null);
    try {
      const { url } = await iniciarPago(producto, getClientToken() ?? undefined);
      // Se sale del sitio hacia Flow. No se limpia el estado a propósito: el
      // botón queda deshabilitado hasta que el navegador cambie de página, de
      // modo que un doble clic no genere dos órdenes.
      // assign() y no `location.href = ...`: asignar sobre el objeto global
      // es una mutación que el linter de React marca como error.
      window.location.assign(url);
    } catch (err) {
      setErrorPago(
        err instanceof ApiError && err.detail
          ? err.detail
          : "No se pudo iniciar el pago. Inténtalo de nuevo."
      );
      setPagando(null);
    }
  }

  const comprables =
    productos?.pago_disponible && plan.plan === "gratis"
      ? productos.productos
      : [];

  return (
    <section className="card-panel p-6" aria-labelledby="h-plan">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h2 id="h-plan" className="font-semibold tracking-tight">
          {NOMBRE[plan.plan] ?? plan.plan}
        </h2>
        {plan.plan === "gratis" ? (
          <Link href="/planes" className="text-xs font-medium text-accent hover:underline">
            Ver los planes
          </Link>
        ) : (
          plan.vence_el && (
            <span className="text-xs text-muted">
              {/* "Tu plan vence el 5" y "se te cobra el 5" son cosas
                  distintas, y quien está en la prueba necesita leer la
                  segunda. Confundirlas es cobrar por sorpresa. */}
              {plan.en_trial
                ? `Primer cobro el ${enTexto(plan.vence_el)}`
                : plan.cancelada_al_terminar
                  ? `Acceso hasta el ${enTexto(plan.vence_el)}`
                  : `Se renueva el ${enTexto(plan.vence_el)}`}
            </span>
          )
        )}
      </div>

      {limite != null ? (
        <div className="mt-4">
          <div className="flex items-baseline justify-between gap-3 text-sm">
            <span>
              <strong className="tabular-nums">{usados}</strong>
              <span className="text-muted"> de {limite} ensayos este mes</span>
            </span>
            <span className="text-xs text-muted">
              {restantes === 0
                ? plan.limites_activos
                  ? "Sin ensayos disponibles"
                  : "Sobre el tope, pero sin bloquear todavía"
                : `Te quedan ${restantes}`}
            </span>
          </div>
          <div className="mt-2">
            <BarraProgreso
              porcentaje={(usados / limite) * 100}
              color={restantes === 0 ? "var(--accent-warm)" : "var(--accent)"}
              etiqueta={`${usados} de ${limite} ensayos usados este mes`}
              alto="h-1.5"
            />
          </div>
          {!plan.limites_activos && (
            <p className="mt-2 text-xs leading-relaxed text-muted">
              El tope todavía no se aplica: mientras el plan Pro no se pueda
              contratar, puedes seguir rindiendo sin límite.
            </p>
          )}
        </div>
      ) : (
        <p className="mt-3 text-sm text-muted">
          Ensayos sin límite, hasta 10 preferencias en tu meta y el análisis
          completo de tus errores.
        </p>
      )}

      {/* La prueba gratis, para quien todavía puede tomarla. Va ANTES de los
          precios sueltos: es la puerta de entrada barata y competir consigo
          misma en la misma tarjeta solo obliga a decidir dos cosas a la vez. */}
      {plan.plan === "gratis" && plan.trial_disponible && (
        <div className="mt-5 border-t border-border pt-4">
          <p className="text-sm font-semibold tracking-tight">
            Prueba el plan Pro {plan.trial_dias} días gratis
          </p>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            Ensayos sin límite desde hoy y hasta 10 carreras en Mi meta.
          </p>
          <BotonTrial dias={plan.trial_dias} monto={plan.trial_monto} compacto />
        </div>
      )}

      {/* Estado de la prueba en curso. Lo primero que dice es cuándo se cobra:
          quien entró con tarjeta necesita ver esa fecha sin buscarla, y
          esconderla es lo que convierte un trial en un cobro por sorpresa. */}
      {plan.en_trial && plan.vence_el && (
        <div className="mt-5 rounded-xl border border-accent/40 bg-accent/5 p-4">
          <p className="text-sm font-medium">
            Estás en tu prueba gratis de {plan.trial_dias} días
          </p>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            {plan.cancelada_al_terminar ? (
              <>
                Ya la cancelaste: <strong className="font-medium text-foreground">
                no se te va a cobrar nada</strong>. Sigues con Pro hasta el{" "}
                {enTexto(plan.vence_el)}.
              </>
            ) : (
              <>
                El {enTexto(plan.vence_el)} se cobran $
                {plan.trial_monto.toLocaleString("es-CL")}
                {plan.tarjeta ? ` a tu ${plan.tarjeta}` : ""}. Si cancelas antes
                de esa fecha, no se te cobra.
              </>
            )}
          </p>
        </div>
      )}

      {/* Cancelar. Estaba solo como "escríbenos a hola@": pedir un correo para
          dejar de pagar, cuando pagar son dos clics, es fricción puesta a
          propósito. */}
      {plan.plan !== "gratis" && !plan.cancelada_al_terminar && plan.vence_el && (
        <div className="mt-4">
          <button
            type="button"
            onClick={cancelar}
            disabled={cancelando}
            className="text-xs font-medium text-muted underline underline-offset-2 transition-colors hover:text-foreground disabled:opacity-50"
          >
            {cancelando
              ? "Cancelando…"
              : plan.en_trial
                ? "Cancelar antes del cobro"
                : "Cancelar la renovación"}
          </button>
          <p className="mt-1 text-xs text-muted">
            Conservas el acceso hasta el {enTexto(plan.vence_el)}.
          </p>
          {errorCancelar && (
            <p className="mt-2 text-sm text-danger">{errorCancelar}</p>
          )}
        </div>
      )}

      {plan.plan !== "gratis" && plan.cancelada_al_terminar && !plan.en_trial && plan.vence_el && (
        <p className="mt-4 text-xs leading-relaxed text-muted">
          Tu plan no se va a renovar. Sigues con Pro hasta el{" "}
          {enTexto(plan.vence_el)}, y después vuelves al plan Gratis.
        </p>
      )}

      {comprables.length > 0 && (
        <div className="mt-5 border-t border-border pt-4">
          <p className="text-xs font-medium text-muted">
            {plan.trial_disponible ? "O contrata directamente" : "Pasar a Pro"}
          </p>
          <div className="mt-3 flex flex-col gap-2">
            {comprables.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => comprar(p.id)}
                disabled={pagando !== null}
                className="flex items-center justify-between gap-3 rounded-xl border border-border p-3 text-left transition hover:border-border-strong disabled:opacity-50"
              >
                <span className="min-w-0">
                  <span className="block text-sm font-medium">{p.asunto}</span>
                  <span className="block text-xs text-muted">
                    {p.dias} días de acceso
                  </span>
                </span>
                <span className="shrink-0 text-sm font-semibold tabular-nums">
                  ${p.monto.toLocaleString("es-CL")}
                </span>
              </button>
            ))}
          </div>
          <p className="mt-2 text-xs leading-relaxed text-muted">
            {pagando
              ? "Te estamos llevando a Flow para completar el pago…"
              : "El pago se procesa en Flow. No guardamos los datos de tu tarjeta."}
          </p>
          {errorPago && <p className="mt-2 text-sm text-danger">{errorPago}</p>}
        </div>
      )}

      {/* Canje de código: sigue disponible junto al pago, porque es la vía de
          los colegios piloto y de cualquier convenio. */}
      <form onSubmit={canjear} className="mt-5 border-t border-border pt-4">
        <label
          htmlFor="codigo-plan"
          className="block text-xs font-medium text-muted"
        >
          ¿Tienes un código?
        </label>
        <div className="mt-2 flex gap-2">
          <input
            id="codigo-plan"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value.toUpperCase())}
            placeholder="SALA-4B"
            className="min-w-0 flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm uppercase placeholder:text-muted/60"
          />
          <button
            type="submit"
            disabled={canjeando || codigo.trim().length < 3}
            className="shrink-0 rounded-lg border border-border px-4 py-2 text-sm font-medium transition-colors hover:bg-surface-hover disabled:opacity-50"
          >
            {canjeando ? "Canjeando…" : "Canjear"}
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-danger">{error}</p>}
        {exito && (
          <p className="mt-2 text-sm text-success">
            Listo. Tu plan quedó activo.
          </p>
        )}
      </form>
    </section>
  );
}
