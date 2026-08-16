import { ImageResponse } from "next/og";

export const alt = "1000paes — Prepara tu PAES";
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
          backgroundImage:
            "radial-gradient(circle at 22% 20%, rgba(124,58,237,0.18), transparent 55%), radial-gradient(circle at 78% 75%, rgba(34,211,238,0.16), transparent 55%)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 20,
            padding: "10px 24px",
            borderRadius: 999,
            border: "2px solid #e4e5ee",
            fontSize: 28,
            color: "#7c3aed",
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
            backgroundImage: "linear-gradient(135deg, #7c3aed, #0e7490)",
            backgroundClip: "text",
            color: "transparent",
          }}
        >
          1000paes
        </div>
        <div style={{ display: "flex", marginTop: 20, fontSize: 34, color: "#576076" }}>
          Ensayos con tiempo real, puntaje estimado y resolución paso a paso
        </div>
      </div>
    ),
    { ...size }
  );
}
