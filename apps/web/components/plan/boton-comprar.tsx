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
  compacto = false,
}: {
  producto: string;
  etiqueta: string;
  //: Dentro de una lista de opciones el aviso de Flow se repetiría por cada
  //: una. Se muestra una sola vez fuera de la lista.
  compacto?: boolean;
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
    <div className={compacto ? "mt-2" : "mt-6"}>
      <button
        type="button"
        onClick={comprar}
        disabled={cargando}
        className={
          "w-full rounded-lg font-semibold disabled:opacity-60 " +
          (compacto
            ? "border border-border px-3 py-1.5 text-xs transition-colors hover:bg-surface-hover"
            : "btn-warm px-4 py-2.5 text-sm text-on-fill")
        }
      >
        {cargando ? "Llevándote a Flow…" : etiqueta}
      </button>
      {error && <p className="mt-2 text-xs text-danger">{error}</p>}
      {!compacto && (
        <p className="mt-2 text-center text-xs text-muted">
          Pago seguro con Flow. No guardamos los datos de tu tarjeta.
        </p>
      )}
    </div>
  );
}
