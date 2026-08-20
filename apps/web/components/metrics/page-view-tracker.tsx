"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { trackPageView, type Utm } from "@/lib/api";
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
 * Y con el referrer no basta para publicidad pagada: el navegador interno de
 * Instagram muchas veces no manda ninguno, así que esas visitas quedaban
 * indistinguibles de un amigo pasando el link; y aunque llegue
 * "instagram.com", todos los anuncios caen en el mismo balde. Por eso se
 * mandan también los UTM de la URL de entrada, que son etiquetas que escribe
 * quien arma el anuncio, no datos de la persona.
 *
 * Convive con Vercel Analytics sin reemplazarlo: aquel mide rendimiento y
 * tráfico, este alimenta las tablas que el panel cruza con registros y ensayos.
 */

const STORAGE_KEY = "paes_visitor_id";

const CLAVES_UTM = ["utm_source", "utm_medium", "utm_campaign", "utm_content"] as const;

/**
 * Los UTM de la URL actual, si los hay.
 *
 * Se leen de `window.location` y no con `useSearchParams` porque ese hook
 * obliga a envolver el componente en un Suspense y a renderizarlo en el
 * cliente; acá ya estamos dentro de un efecto, que solo corre en el navegador.
 *
 * Se recortan antes de mandarlos: el servidor los vuelve a acotar, pero no
 * tiene sentido enviar un kilobyte por la red para que lo trunquen al llegar.
 */
function utmDeLaUrl(): Utm | undefined {
  try {
    const params = new URLSearchParams(window.location.search);
    const utm: Utm = {};
    for (const clave of CLAVES_UTM) {
      const valor = params.get(clave)?.trim();
      if (valor) utm[clave] = valor.slice(0, 300);
    }
    return Object.keys(utm).length > 0 ? utm : undefined;
  } catch {
    return undefined;
  }
}

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
    // propio sitio y no aporta nada, y los UTM ya no están en la URL.
    const origen = esPrimeraVista ? document.referrer : "";
    const utm = esPrimeraVista ? utmDeLaUrl() : undefined;
    trackPageView(
      pathname,
      visitorId,
      getClientToken() ?? undefined,
      origen || undefined,
      utm
    );
  }, [pathname]);

  return null;
}
