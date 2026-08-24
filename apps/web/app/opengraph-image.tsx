import { ImageResponse } from "next/og";

/**
 * La imagen que se ve al compartir el enlace en WhatsApp, Instagram o X.
 *
 * Estaba con la paleta ANTERIOR --violeta #7c3aed y cian, con degradado en el
 * título-- y ese violeta se retiró en el rediseño justo porque era casi el
 * mismo color de identidad de Matemática M2: la marca y una de las cinco
 * pruebas eran el mismo color. Compartir el sitio mostraba una identidad que
 * ya no existe en ninguna otra pantalla del producto.
 *
 * Ahora es papel y grafito, como el resto: el color queda reservado para decir
 * qué prueba es y para corregir.
 */
export const alt = "1000paes — Ensayos PAES con puntaje oficial";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#ffffff",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 20,
            padding: "10px 24px",
            borderRadius: 999,
            border: "2px solid #e4e2dc",
            fontSize: 28,
            color: "#5b5b66",
            fontWeight: 600,
          }}
        >
          PAES · Las cinco pruebas · Admisión 2027
        </div>
        <div
          style={{
            display: "flex",
            marginTop: 36,
            fontSize: 160,
            fontWeight: 800,
            letterSpacing: -4,
            color: "#2b2b33",
          }}
        >
          1000paes
        </div>
        <div style={{ display: "flex", marginTop: 20, fontSize: 34, color: "#5b5b66" }}>
          Ensayos con tiempo real, puntaje estimado y resolución paso a paso
        </div>
      </div>
    ),
    { ...size }
  );
}
