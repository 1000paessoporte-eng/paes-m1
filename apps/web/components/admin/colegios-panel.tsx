"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { fijarPlanColegio, type ColegioAdmin } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * Los cursos creados y hasta cuándo tienen el plan pagado.
 *
 * El plan Colegios se vende conversando: un establecimiento compra con orden
 * de compra y factura, no con tarjeta, así que la página de planes dice
 * "Escríbenos" y no tiene botón de pago. Esta tabla es lo que convierte esa
 * conversación en acceso real: se escribe la fecha hasta la que quedó pagado y
 * desde ese momento cada alumno del curso tiene los límites del plan Pro.
 */

const FECHA = new Intl.DateTimeFormat("es-CL", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

function comoFechaLocal(iso: string): Date {
  const [a, m, d] = iso.split("-").map(Number);
  return new Date(a, m - 1, d);
}

export function ColegiosPanel({ colegios }: { colegios: ColegioAdmin[] }) {
  const router = useRouter();
  const [editando, setEditando] = useState<number | null>(null);
  const [fecha, setFecha] = useState("");
  const [guardando, setGuardando] = useState(false);
  // Ver el comentario equivalente en agenda-ensayos.tsx.
  const [hoy] = useState(() => new Date().toISOString().slice(0, 10));

  if (colegios.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-border p-5 text-sm text-muted">
        Todavía no hay ningún curso creado.
      </p>
    );
  }

  async function guardar(id: number, valor: string | null) {
    setGuardando(true);
    try {
      await fijarPlanColegio(id, valor, getClientToken() ?? undefined);
      setEditando(null);
      router.refresh();
    } finally {
      setGuardando(false);
    }
  }

  return (
    <ul className="divide-y divide-border rounded-xl border border-border bg-surface">
      {colegios.map((c) => {
        const alDia = c.plan_hasta != null && c.plan_hasta >= hoy;
        return (
          <li key={c.id} className="p-4">
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{c.nombre}</p>
                <p className="text-xs text-muted">
                  <span className="font-mono">{c.codigo}</span> · {c.alumnos}{" "}
                  {c.alumnos === 1 ? "alumno" : "alumnos"}
                </p>
              </div>

              <p className="shrink-0 text-xs">
                {c.plan_hasta == null ? (
                  <span className="text-muted">sin plan</span>
                ) : alDia ? (
                  <span className="text-success">
                    pagado hasta {FECHA.format(comoFechaLocal(c.plan_hasta))}
                  </span>
                ) : (
                  <span className="text-danger">
                    venció el {FECHA.format(comoFechaLocal(c.plan_hasta))}
                  </span>
                )}
              </p>
            </div>

            {editando === c.id ? (
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <input
                  type="date"
                  value={fecha}
                  onChange={(e) => setFecha(e.target.value)}
                  aria-label={`Plan de ${c.nombre} hasta`}
                  className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm"
                />
                <button
                  type="button"
                  disabled={!fecha || guardando}
                  onClick={() => guardar(c.id, fecha)}
                  className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium disabled:opacity-40"
                >
                  Guardar
                </button>
                <button
                  type="button"
                  disabled={guardando}
                  onClick={() => guardar(c.id, null)}
                  className="rounded-lg px-3 py-1.5 text-xs text-muted hover:text-danger"
                >
                  Cortar el plan
                </button>
                <button
                  type="button"
                  onClick={() => setEditando(null)}
                  className="rounded-lg px-3 py-1.5 text-xs text-muted"
                >
                  Cancelar
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => {
                  setEditando(c.id);
                  setFecha(c.plan_hasta ?? "");
                }}
                className="mt-2 text-xs text-muted underline decoration-border underline-offset-4 hover:text-foreground"
              >
                Cambiar el plan
              </button>
            )}
          </li>
        );
      })}
    </ul>
  );
}
