"use client";

import Link from "next/link";
import { useState } from "react";
import type { MiPlan, Productos } from "@/lib/api";
import { ApiError, canjearCodigo, iniciarPago } from "@/lib/api";
import { getClientToken } from "@/lib/auth";
import { BarraProgreso } from "@/components/ui/barra-progreso";

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

  async function comprar(producto: string) {
    setPagando(producto);
    setErrorPago(null);
    try {
      const { url } = await iniciarPago(producto, getClientToken() ?? undefined);
      // Se sale del sitio hacia Flow. No se limpia el estado a propósito: el
      // botón queda deshabilitado hasta que el navegador cambie de página, de
      // modo que un doble clic no genere dos órdenes.
      window.location.href = url;
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
              Hasta el{" "}
              {new Date(plan.vence_el).toLocaleDateString("es-CL", {
                day: "numeric",
                month: "long",
              })}
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

      {comprables.length > 0 && (
        <div className="mt-5 border-t border-border pt-4">
          <p className="text-xs font-medium text-muted">Pasar a Pro</p>
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
