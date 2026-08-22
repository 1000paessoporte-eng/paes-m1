/**
 * Contar que algo se rompió en el navegador del estudiante.
 *
 * Hasta ahora no había forma de enterarse: la página quedaba en blanco en un
 * teléfono cualquiera y nosotros nos enterábamos solo si esa persona se
 * molestaba en escribirnos. Con tres alumnos activos eso todavía puede pasar;
 * con trescientos, no.
 *
 * Reglas de esta función:
 *
 * - **Nunca lanza.** Reportar que algo falló no puede ser lo segundo que
 *   falla. Todo va dentro de un `catch` vacío a propósito.
 * - **No espera respuesta.** Se manda y se sigue; al usuario no le importa.
 * - **No manda el query string.** Puede traer datos de la persona, y para
 *   agrupar errores no sirve de nada. Igual lo recorta el servidor, pero se
 *   recorta acá también para no mandarlo por la red.
 * - **Manda el token si hay sesión.** El endpoint es público --la mayoría de
 *   los errores revienta antes de que haya cuenta-- pero cuando la hay, saber
 *   a cuántas cuentas distintas les pasa es lo que separa un caso raro de algo
 *   que hay que soltar todo y mirar.
 */

import { getClientToken } from "@/lib/auth";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

/** Cuántos errores manda una pestaña antes de callarse.
 *
 * Un bucle de render dispara un error por cuadro. El servidor los agrupa, pero
 * igual serían sesenta peticiones por segundo desde un teléfono con datos
 * móviles. */
const TOPE_POR_SESION = 8;

let enviados = 0;

export function reportarError(error: unknown, rutaExplicita?: string): void {
  if (typeof window === "undefined") return;
  if (enviados >= TOPE_POR_SESION) return;
  enviados += 1;

  const mensaje =
    error instanceof Error
      ? error.message || error.name
      : typeof error === "string"
        ? error
        : "Error sin mensaje";

  const cuerpo = JSON.stringify({
    mensaje: mensaje.slice(0, 500),
    ruta: rutaExplicita ?? window.location.pathname,
    pila: error instanceof Error ? error.stack?.slice(0, 4000) : undefined,
  });

  try {
    // `keepalive` para que el envío sobreviva a la navegación: muchos errores
    // ocurren justo cuando la persona se va de la página.
    const token = getClientToken();
    void fetch(`${BASE}/api/errores`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: cuerpo,
      keepalive: true,
    }).catch(() => {});
  } catch {
    // Si ni siquiera se puede llamar a fetch, no hay nada más que hacer.
  }
}

/**
 * Engancha los errores que NO pasan por un `error.tsx`: los de código
 * asíncrono y las promesas sin `catch`. Son la mayoría, y eran justamente los
 * invisibles.
 */
export function escucharErroresGlobales(): () => void {
  const alError = (e: ErrorEvent) => reportarError(e.error ?? e.message);
  const alRechazo = (e: PromiseRejectionEvent) => reportarError(e.reason);

  window.addEventListener("error", alError);
  window.addEventListener("unhandledrejection", alRechazo);
  return () => {
    window.removeEventListener("error", alError);
    window.removeEventListener("unhandledrejection", alRechazo);
  };
}
