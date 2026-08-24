import { ImageResponse } from "next/og";

/**
 * El icono que iOS pone en la pantalla de inicio.
 *
 * Sin este archivo, un estudiante que guarda 1000paes en su iPhone --lo normal
 * en un producto que se usa desde el teléfono-- se queda con una miniatura
 * borrosa de la página en vez de un logo. Android e iOS lo piden en formatos
 * distintos y ninguno de los dos usa el favicon.
 *
 * El dibujo es LA BURBUJA del cartón de respuestas, que es la firma de la
 * marca: grafito macizo sobre papel. No lleva color de ninguna de las cinco
 * pruebas a propósito -- el color significa "qué prueba es", y la marca es
 * acromática justamente para no pisar ese significado.
 */
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

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
          // Papel, el fondo del sistema visual en claro.
          background: "#ffffff",
        }}
      >
        <div
          style={{
            width: 132,
            height: 132,
            borderRadius: 999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            // Grafito macizo: la burbuja rellena.
            background: "#2b2b33",
            color: "#ffffff",
            fontSize: 52,
            fontWeight: 700,
            letterSpacing: -2,
          }}
        >
          1000
        </div>
      </div>
    ),
    { ...size }
  );
}
