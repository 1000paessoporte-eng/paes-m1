import { ImageResponse } from "next/og";

/**
 * El favicon.
 *
 * Antes acá había un `favicon.ico` con un círculo negro y un triángulo blanco
 * que no aparecía en ninguna otra parte del producto y que nunca fue
 * modificado desde que entró al repositorio: arte de plantilla. Y es el peor
 * lugar posible para dejarlo, porque el favicon es la impresión de marca MÁS
 * frecuente que existe -- sale en cada pestaña, cada marcador y al lado de
 * cada resultado de búsqueda.
 *
 * Ahora es la misma burbuja del logotipo y del icono de iOS.
 *
 * A 32 px el contorno hecho a mano se lee como suciedad, no como lápiz, así
 * que acá la burbuja es un círculo limpio y el anillo va más grueso para que
 * no se pierda al reducir. Esa es la regla del sistema: el dibujo cambia según
 * el tamaño (ver `components/ui/marca.tsx`).
 */
export const size = { width: 32, height: 32 };
export const contentType = "image/png";

const PAPEL = "#ffffff";
const GRAFITO = "#2b2b33";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: PAPEL,
        }}
      >
        <svg width="30" height="30" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r="46"
            fill="none"
            stroke={GRAFITO}
            strokeWidth="10"
            opacity="0.34"
          />
          <circle cx="60" cy="60" r="42" fill={GRAFITO} />
        </svg>
      </div>
    ),
    { ...size }
  );
}
