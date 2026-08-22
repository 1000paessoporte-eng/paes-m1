"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { EnsayoProgramado, MiColegio } from "@/lib/api";
import { salirDelColegio } from "@/lib/api";
import { actualizarUsuarioLocal, getClientToken } from "@/lib/auth";
import { AgendaEnsayos } from "@/components/colegio/agenda-ensayos";

/**
 * El curso, visto por un alumno.
 *
 * Es deliberadamente corto. Lo único que esta pantalla tiene que responder es
 * "¿qué me toca rendir y para cuándo?"; el resto de su avance ya vive en el
 * panel y en la analítica, y repetirlo acá sería una segunda versión de los
 * mismos números.
 *
 * No muestra a los compañeros ni sus puntajes. Un ranking de curso convierte
 * una herramienta de estudio en una lista pública de quién va último, y eso lo
 * decide un profesor en su sala, no nosotros por defecto.
 */
export function VistaAlumno({
  colegio,
  ensayos,
}: {
  colegio: NonNullable<MiColegio>;
  ensayos: EnsayoProgramado[];
}) {
  const router = useRouter();
  const [saliendo, setSaliendo] = useState(false);
  const pendientes = ensayos.filter((e) => e.lo_rendi === false).length;

  async function salir() {
    if (!confirm("Vas a salir del curso. Tu progreso y tus ensayos siguen siendo tuyos. ¿Seguro?"))
      return;
    setSaliendo(true);
    try {
      await salirDelColegio(getClientToken() ?? undefined);
      actualizarUsuarioLocal({ tiene_colegio: false });
      router.refresh();
    } catch {
      setSaliendo(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <p className="text-xs font-medium tracking-wide text-muted uppercase">
          Mi curso
        </p>
        <h1 className="mt-1 text-2xl font-semibold">{colegio.nombre}</h1>
        <p className="mt-1 text-sm text-muted">
          {pendientes === 0
            ? "No tienes ensayos pendientes del curso."
            : `Tienes ${pendientes} ${pendientes === 1 ? "ensayo pendiente" : "ensayos pendientes"}.`}
        </p>
      </div>

      <AgendaEnsayos ensayos={ensayos} puedeAgendar={false} />

      <div className="border-t border-border pt-6">
        <button
          type="button"
          onClick={salir}
          disabled={saliendo}
          className="text-sm text-muted underline decoration-border underline-offset-4 hover:text-danger"
        >
          Salir del curso
        </button>
      </div>
    </div>
  );
}
