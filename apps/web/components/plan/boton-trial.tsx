"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError, iniciarTrial } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * El botón que empieza la prueba gratis.
 *
 * Manda al usuario a Flow a registrar su tarjeta. No se le cobra ahora: son
 * tres días de Pro y recién al cuarto Flow cobra el primer mes. Se le dice
 * antes de mandarlo, porque pedir una tarjeta sin explicar por qué es la forma
 * más rápida de que cierre la pestaña.
 *
 * Quien no tiene sesión va a registrarse y vuelve: el trial necesita una cuenta
 * a la cual atarlo.
 */
export function BotonTrial({
  etiqueta = "Comenzar 3 días gratis",
}: {
  etiqueta?: string;
}) {
  const router = useRouter();
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function empezar() {
    const token = getClientToken();
    if (!token) {
      router.push("/registro?next=/planes");
      return;
    }
    setCargando(true);
    setError(null);
    try {
      const { url } = await iniciarTrial(token);
      // Se abandona el sitio hacia Flow. No se limpia `cargando`: el botón queda
      // inhabilitado hasta que cambie la página, para que un doble clic no abra
      // dos registros.
      window.location.assign(url);
    } catch (err) {
      setError(
        err instanceof ApiError && err.detail
          ? err.detail
          : "No se pudo empezar la prueba. Inténtalo de nuevo."
      );
      setCargando(false);
    }
  }

  return (
    <div className="mt-6">
      <button
        type="button"
        onClick={empezar}
        disabled={cargando}
        className="btn-glow w-full rounded-lg px-4 py-2.5 text-sm font-semibold text-accent-foreground disabled:opacity-60"
      >
        {cargando ? "Llevándote a Flow…" : etiqueta}
      </button>
      {error && <p className="mt-2 text-xs text-danger">{error}</p>}
      <p className="mt-2 text-center text-xs text-muted">
        3 días gratis, luego $9.990 al mes. Cancela cuando quieras. Registro
        seguro con Flow: no guardamos los datos de tu tarjeta.
      </p>
    </div>
  );
}
