"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError, iniciarPago } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * El botón de contratar, en la página de precios.
 *
 * Existe además del que está en el perfil porque el momento de decidir es
 * este: mandar a alguien convencido a buscar dónde pagar es la forma más
 * eficaz de perderlo. Quien no tiene sesión va a registrarse y vuelve acá.
 */
export function BotonComprar({
  producto,
  etiqueta,
}: {
  producto: string;
  etiqueta: string;
}) {
  const router = useRouter();
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function comprar() {
    const token = getClientToken();
    if (!token) {
      router.push("/registro?next=/planes");
      return;
    }
    setCargando(true);
    setError(null);
    try {
      const { url } = await iniciarPago(producto, token);
      // Se abandona el sitio hacia Flow. No se limpia `cargando` a propósito:
      // el botón queda inhabilitado hasta que cambie la página, de modo que un
      // doble clic no genere dos órdenes.
      window.location.href = url;
    } catch (err) {
      setError(
        err instanceof ApiError && err.detail
          ? err.detail
          : "No se pudo iniciar el pago. Inténtalo de nuevo."
      );
      setCargando(false);
    }
  }

  return (
    <div className="mt-6">
      <button
        type="button"
        onClick={comprar}
        disabled={cargando}
        className="btn-warm w-full rounded-lg px-4 py-2.5 text-sm font-semibold text-on-fill disabled:opacity-60"
      >
        {cargando ? "Llevándote a Flow…" : etiqueta}
      </button>
      {error && <p className="mt-2 text-xs text-danger">{error}</p>}
      <p className="mt-2 text-center text-xs text-muted">
        Pago seguro con Flow. No guardamos los datos de tu tarjeta.
      </p>
    </div>
  );
}
