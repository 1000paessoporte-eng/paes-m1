import { ImageResponse } from "next/og";
import { ApiError, getLesson } from "@/lib/api";

export const alt = "Lección del temario PAES";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/**
 * La imagen que se ve al compartir una lección por WhatsApp.
 *
 * Hasta ahora todas las páginas del sitio compartían la misma tarjeta genérica
 * de la portada, así que mandarle "Función cuadrática" a un compañero se veía
 * igual que mandarle la home: el enlace no decía de qué era.
 *
 * Lleva el nombre del tema porque es lo único que decide si alguien abre el
 * enlace. No lleva la intro completa: a 1200x630 el texto largo se ve como una
 * mancha gris en la previsualización de WhatsApp.
 */
export default async function Image({ params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;

  let nombre = "Lección del temario PAES";
  try {
    nombre = (await getLesson(code)).node_name;
  } catch (err) {
    // Un nodo sin lección todavía no justifica romper la imagen: se comparte
    // la tarjeta genérica y la página se encarga del 404.
    if (!(err instanceof ApiError)) throw err;
  }

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 72,
          background: "#ffffff",
          backgroundImage:
            "radial-gradient(circle at 18% 12%, rgba(124,58,237,0.18), transparent 55%), radial-gradient(circle at 85% 88%, rgba(34,211,238,0.16), transparent 55%)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignSelf: "flex-start",
            padding: "10px 24px",
            borderRadius: 999,
            border: "2px solid #e4e5ee",
            fontSize: 26,
            color: "#7c3aed",
            fontWeight: 600,
          }}
        >
          Lección · Temario PAES
        </div>

        <div
          style={{
            display: "flex",
            fontSize: nombre.length > 42 ? 68 : 88,
            fontWeight: 800,
            letterSpacing: -2,
            lineHeight: 1.1,
            color: "#12141c",
          }}
        >
          {nombre}
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: 16 }}>
          <span
            style={{
              fontSize: 40,
              fontWeight: 800,
              backgroundImage: "linear-gradient(135deg, #7c3aed, #0e7490)",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            1000paes
          </span>
          <span style={{ fontSize: 28, color: "#576076" }}>
            Teoría, ejercicio resuelto y el error más común
          </span>
        </div>
      </div>
    ),
    { ...size }
  );
}
