import { ImageResponse } from "next/og";
import { CONTORNO_A_MANO } from "@/components/ui/marca";

/**
 * El icono que iOS pone en la pantalla de inicio.
 *
 * Sin este archivo, un estudiante que guarda 1000paes en su iPhone --lo normal
 * en un producto que se usa desde el teléfono-- se queda con una miniatura
 * borrosa de la página en vez de un logo. Android e iOS lo piden en formatos
 * distintos y ninguno de los dos usa el favicon.
 *
 * El dibujo es LA BURBUJA del cartón de respuestas, que es la firma de la
 * marca: grafito macizo sobre papel. Es el mismo cero relleno del logotipo,
 * extraído. No lleva color de ninguna de las cinco pruebas a propósito -- el
 * color significa "qué prueba es", y la marca es acromática justamente para no
 * pisar ese significado.
 *
 * A 180 px el borde irregular se ve, así que acá sí se usa el contorno hecho a
 * mano. El contorno viaja como PATH y no como filtro SVG porque Satori --el
 * motor de `ImageResponse`-- no implementa `feTurbulence` ni
 * `feDisplacementMap`: un filtro se habría visto en el navegador y habría
 * salido un círculo liso justo acá.
 */
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

const PAPEL = "#ffffff";
const GRAFITO = "#2b2b33";

export default function AppleIcon() {
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
        <svg width="136" height="136" viewBox="0 0 120 120">
          {/* El anillo impreso del cartón. */}
          <circle
            cx="60"
            cy="60"
            r="46"
            fill="none"
            stroke={GRAFITO}
            strokeWidth="5"
            opacity="0.34"
          />
          {/* El grafito, que se pasa del anillo como cualquier marca a lápiz. */}
          <path d={CONTORNO_A_MANO} fill={GRAFITO} />
        </svg>
      </div>
    ),
    { ...size }
  );
}
