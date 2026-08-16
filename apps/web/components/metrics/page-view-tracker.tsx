"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { trackPageView } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * Avisa a la API cada vez que cambia la ruta, para el panel de administración.
 *
 * El identificador de visitante es un número aleatorio guardado en el propio
 * navegador: sirve para no contar diez veces a quien abre diez páginas, y no
 * dice nada de quién es la persona. No se manda IP ni user agent.
 *
 * Sí se manda `document.referrer`, de donde el servidor se queda ÚNICAMENTE
 * con el dominio. Es la diferencia entre saber que alguien llegó y saber por
 * dónde: sin ese dato no hay forma de distinguir el canal que trae usuarios
 * del que no trae ninguno, que es la decisión más cara de tomar a ciegas.
 *
 * Convive con Vercel Analytics sin reemplazarlo: aquel mide rendimiento y
 * tráfico, este alimenta las tablas que el panel cruza con registros y ensayos.
 */

const STORAGE_KEY = "paes_visitor_id";

function obtenerVisitorId(): string | null {
  try {
    const guardado = localStorage.getItem(STORAGE_KEY);
    if (guardado) return guardado;
    const nuevo = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEY, nuevo);
    return nuevo;
  } catch {
    // Modo incógnito con almacenamiento bloqueado: se prefiere no medir antes
    // que romper la página.
    return null;
  }
}

export function PageViewTracker() {
  const pathname = usePathname();
  // Evita mandar dos veces la misma ruta cuando React vuelve a montar el
  // componente (Strict Mode en desarrollo lo hace siempre).
  const ultimaRuta = useRef<string | null>(null);

  useEffect(() => {
    if (!pathname || ultimaRuta.current === pathname) return;
    // Se guarda si es la primera vista ANTES de marcar la ruta: después de
    // asignarla ya no hay cómo distinguir la entrada de una navegación.
    const esPrimeraVista = ultimaRuta.current === null;
    ultimaRuta.current = pathname;

    const visitorId = obtenerVisitorId();
    if (!visitorId) return;

    // Solo en la primera vista: en las navegaciones internas el referrer es el
    // propio sitio y no aporta nada.
    const origen = esPrimeraVista ? document.referrer : "";
    trackPageView(pathname, visitorId, getClientToken() ?? undefined, origen || undefined);
  }, [pathname]);

  return null;
}
