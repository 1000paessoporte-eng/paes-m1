"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError, iniciarTrial } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * El botón de "probar Pro gratis" y, pegada a él, la letra que NO puede ser
 * chica.
 *
 * Esta prueba pide tarjeta y se convierte en un cobro automático al cuarto
 * día. Eso obliga a decir tres cosas antes del clic, no después: que hay que
 * dejar una tarjeta, cuánto se va a cobrar, y qué día exacto. La Ley 19.496
 * exige que las condiciones de una oferta estén a la vista, y una suscripción
 * que se activa sola sin que la persona haya entendido que iba a pasar es
 * justamente lo que termina en reclamo al SERNAC y en devolución.
 *
 * Por eso la fecha de cobro se calcula y se muestra: "no se te cobra hasta el
 * 5 de septiembre" es una frase que alguien puede verificar. "Cancela cuando
 * quieras" en abstracto, no.
 */

function fechaDelCobro(dias: number): string {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  return d.toLocaleDateString("es-CL", { day: "numeric", month: "long" });
}

export function BotonTrial({
  dias,
  monto,
  destino = "/panel",
  compacto = false,
}: {
  dias: number;
  //: Lo que se cobra al terminar la prueba, en pesos.
  monto: number;
  //: A dónde volver después de registrarse, si todavía no tiene sesión.
  destino?: string;
  compacto?: boolean;
}) {
  const router = useRouter();
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function empezar() {
    const token = getClientToken();
    if (!token) {
      router.push(`/registro?next=${encodeURIComponent(destino)}`);
      return;
    }
    setCargando(true);
    setError(null);
    try {
      const { url } = await iniciarTrial(token);
      // Se abandona el sitio hacia Flow. No se limpia `cargando` a propósito:
      // el botón queda inhabilitado hasta que cambie la página, de modo que un
      // doble clic no genere dos inscripciones.
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

  const precio = `$${monto.toLocaleString("es-CL")}`;

  return (
    <div className={compacto ? "mt-3" : "mt-6"}>
      <button
        type="button"
        onClick={empezar}
        disabled={cargando}
        className={
          "w-full rounded-lg font-semibold disabled:opacity-60 " +
          (compacto
            ? "btn-glow px-3 py-2 text-xs text-accent-foreground"
            : "btn-glow px-4 py-2.5 text-sm text-accent-foreground")
        }
      >
        {cargando ? "Llevándote a Flow…" : `Probar Pro ${dias} días gratis`}
      </button>

      {/* Las condiciones van ACÁ, no en una página de términos que nadie abre.
          Quien hace clic en el botón ya leyó lo que va a pasar. */}
      <p className="mt-2 text-xs leading-relaxed text-muted">
        Se pide tu tarjeta, pero <strong className="font-medium text-foreground">
        no se cobra nada hasta el {fechaDelCobro(dias)}</strong>. Desde ahí son{" "}
        {precio} al mes. Cancelas cuando quieras desde tu perfil, en un clic; si
        cancelas antes de esa fecha, no se te cobra.
      </p>
      {error && <p className="mt-2 text-xs text-danger">{error}</p>}
    </div>
  );
}
