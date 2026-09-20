"use client";

import { useState } from "react";
import { irAMicrosoft, microsoftDisponible } from "@/lib/microsoft";

/**
 * Botón "Continuar con Microsoft".
 *
 * Existe por los colegios: muchos entregan a sus alumnos una cuenta de Office
 * 365, y ese es el correo que el estudiante tiene a mano en la sala. También
 * es lo que hace vendible el producto a un colegio completo.
 *
 * Sin `NEXT_PUBLIC_MICROSOFT_CLIENT_ID` no se muestra nada, igual que el de
 * Google: la web sigue funcionando con correo y contraseña.
 *
 * El logo va escrito acá y no como imagen: son cuatro cuadrados de colores
 * fijos de Microsoft, y una imagen externa sería una petición más y un
 * recuadro vacío si el bloqueador la corta.
 */
export function MicrosoftButton({
  redirectTo = "/panel",
  onError,
}: {
  redirectTo?: string;
  onError?: (mensaje: string) => void;
}) {
  const [yendo, setYendo] = useState(false);

  if (!microsoftDisponible) return null;

  async function entrar() {
    setYendo(true);
    try {
      await irAMicrosoft(redirectTo);
      // No se vuelve de acá: la pestaña navega a Microsoft.
    } catch {
      setYendo(false);
      onError?.("No se pudo abrir el inicio de sesión de Microsoft.");
    }
  }

  return (
    <button
      type="button"
      onClick={entrar}
      disabled={yendo}
      // 280px y borde redondeado para quedar del mismo ancho y forma que el
      // botón que dibuja Google: dos botones de tamaños distintos uno sobre
      // otro se ven como un error.
      className="flex h-10 w-[280px] items-center justify-center gap-3 rounded-full border border-border bg-background text-sm font-medium transition-colors hover:bg-surface-hover disabled:opacity-60"
    >
      <LogoMicrosoft />
      {yendo ? "Entrando…" : "Continuar con Microsoft"}
    </button>
  );
}

function LogoMicrosoft() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden>
      <rect x="0" y="0" width="7" height="7" fill="#F25022" />
      <rect x="9" y="0" width="7" height="7" fill="#7FBA00" />
      <rect x="0" y="9" width="7" height="7" fill="#00A4EF" />
      <rect x="9" y="9" width="7" height="7" fill="#FFB900" />
    </svg>
  );
}
