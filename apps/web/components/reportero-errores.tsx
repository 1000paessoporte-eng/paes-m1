"use client";

import { useEffect } from "react";
import { escucharErroresGlobales } from "@/lib/reportar-error";

/**
 * Deja escuchando los errores del navegador durante toda la sesión.
 *
 * Va en el layout raíz y no renderiza nada. Los `error.tsx` de Next solo
 * atrapan lo que revienta durante el render de un componente; un fallo en un
 * `fetch` o una promesa sin `catch` no llega ahí y hasta ahora no dejaba
 * rastro en ninguna parte.
 */
export function ReporteroErrores() {
  useEffect(() => escucharErroresGlobales(), []);
  return null;
}
