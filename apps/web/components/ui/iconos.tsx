/**
 * Iconos de línea del producto.
 *
 * Existen porque la página estaba llena de emoji, y un emoji no es un icono:
 * lo dibuja el sistema operativo, no nosotros. El mismo 🔥 es naranja plano en
 * Android, tridimensional en Windows y otra cosa en iOS; ninguno hereda el
 * color del texto, ninguno se apaga cuando la insignia está bloqueada, y
 * todos empujan la línea base del renglón hacia arriba. En una plataforma que
 * cobra por preparar la PAES, además, leen a juguete.
 *
 * Todos comparten la misma geometría —lienzo de 24, trazo de 2, extremos
 * redondeados, `currentColor`— para que se puedan poner uno al lado del otro
 * sin que ninguno pese más que el vecino. Es el mismo dibujo que ya hacían a
 * mano los SVG sueltos repartidos por los componentes.
 *
 * `tamano` va en píxeles y por defecto sigue al texto (1em) cuando se omite.
 */

export interface PropsIcono {
  /** Lado del icono en píxeles. Si se omite, escala con el tamaño de fuente. */
  tamano?: number;
  className?: string;
}

function Base({
  tamano,
  className,
  relleno,
  children,
}: PropsIcono & { relleno?: boolean; children: React.ReactNode }) {
  return (
    <svg
      width={tamano ?? "1em"}
      height={tamano ?? "1em"}
      viewBox="0 0 24 24"
      fill={relleno ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
    >
      {children}
    </svg>
  );
}

/** Diana. Primer ensayo: dar en el blanco una vez. */
export function IconoDiana(props: PropsIcono) {
  return (
    <Base {...props}>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.5" />
    </Base>
  );
}

/** Libro cerrado. Constancia: cinco ensayos rendidos. */
export function IconoLibros(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      <path d="M9 7h7" />
    </Base>
  );
}

/** Llama. La racha de días seguidos. */
export function IconoLlama(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.4-.5-2-1-3-1.1-2.1-.2-4 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.2.4-2.3 1-3a2.5 2.5 0 0 0 2.5 2.5z" />
    </Base>
  );
}

/** Rayo. La racha larga: siete días seguidos. */
export function IconoRayo(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z" />
    </Base>
  );
}

/** Diana con acierto. Puntería: 70% de respuestas correctas. */
export function IconoPunteria(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M21 12a9 9 0 1 1-4.4-7.7" />
      <path d="M9 11.5l2.5 2.5L21 4.5" />
    </Base>
  );
}

/** Brote. Los primeros temas dominados del árbol. */
export function IconoBrote(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M7 20h10" />
      <path d="M10 20c5.5-2.5.8-6.4 3-10" />
      <path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z" />
      <path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z" />
    </Base>
  );
}

/** Cumbre. 700 puntos estimados. */
export function IconoCumbre(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="m8 3 4 8 5-5 5 15H2L8 3z" />
    </Base>
  );
}

/** Corona. 850 puntos estimados: el techo de la escala. */
export function IconoCorona(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M11.6 3.3a.5.5 0 0 1 .9 0l3 5.6a1 1 0 0 0 1.5.3l4.2-3.7a.5.5 0 0 1 .8.5l-2.8 10.3a1 1 0 0 1-1 .7H5.8a1 1 0 0 1-1-.7L2 6a.5.5 0 0 1 .8-.5L7 9.2a1 1 0 0 0 1.5-.3z" />
      <path d="M5 21h14" />
    </Base>
  );
}

/** Hoja escrita. La racha de ensayos, la que cuenta para el premio. */
export function IconoHojaEscrita(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8" />
      <path d="M9 8h4" />
      <path d="M9 12h3" />
      <path d="M17.5 2.5a2.1 2.1 0 0 1 3 3L15 11l-4 1 1-4z" />
    </Base>
  );
}

/** Triángulo de advertencia. Encabeza las pantallas de error. */
export function IconoAdvertencia(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M10.3 3.6 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </Base>
  );
}

/** Estrella. Marca una pregunta para volver a ella. Se rellena al marcarla. */
export function IconoEstrella({ marcada, ...props }: PropsIcono & { marcada?: boolean }) {
  return (
    <Base {...props} relleno={marcada}>
      <path d="m12 2.8 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.4l6.2-.9z" />
    </Base>
  );
}

/** Sol. Tema claro. */
export function IconoSol(props: PropsIcono) {
  return (
    <Base {...props}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </Base>
  );
}

/** Luna. Tema oscuro. */
export function IconoLuna(props: PropsIcono) {
  return (
    <Base {...props}>
      <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" />
    </Base>
  );
}

/** Círculo mitad y mitad. Tema automático: el que decide el teléfono. */
export function IconoAutomatico(props: PropsIcono) {
  return (
    <Base {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 3a9 9 0 0 0 0 18z" fill="currentColor" stroke="none" />
    </Base>
  );
}
