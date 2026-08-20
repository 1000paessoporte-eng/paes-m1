import { ImageResponse } from "next/og";
import { getCarrera } from "@/lib/api";
import { codigoDesdeSlug, nombreLegible } from "@/lib/carreras";

export const alt = "Ponderaciones PAES de la carrera";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/**
 * La imagen que se ve al compartir una ficha de carrera.
 *
 * Estas 1.855 fichas son lo que más se pasa por WhatsApp entre compañeros
 * ("mira cuánto piden acá"), y todas compartían la tarjeta genérica de la
 * portada. Lleva el dato que hace que alguien abra el enlace: la carrera, la
 * universidad y el ponderado mínimo.
 *
 * Cuando el DEMRE no publica el ponderado mínimo se dice eso mismo, no un
 * guion ni un cero: 1.153 de las 1.855 carreras no lo traen, y un cero ahí se
 * leería como "no piden puntaje".
 */
export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const codigo = codigoDesdeSlug(slug);

  const carrera = codigo ? await getCarrera(codigo).catch(() => null) : null;
  if (!carrera) {
    return new ImageResponse(<Tarjeta titulo="Carreras y ponderaciones PAES" />, { ...size });
  }

  return new ImageResponse(
    (
      <Tarjeta
        titulo={nombreLegible(carrera.nombre)}
        universidad={nombreLegible(carrera.universidad)}
        minimo={carrera.ponderado_min}
        proceso={carrera.proceso}
      />
    ),
    { ...size }
  );
}

function Tarjeta({
  titulo,
  universidad,
  minimo,
  proceso,
}: {
  titulo: string;
  universidad?: string;
  minimo?: number | null;
  proceso?: number;
}) {
  return (
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
        {proceso ? `Ponderaciones oficiales DEMRE · Admisión ${proceso}` : "Ponderaciones oficiales DEMRE"}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <div
          style={{
            display: "flex",
            fontSize: titulo.length > 38 ? 62 : 78,
            fontWeight: 800,
            letterSpacing: -2,
            lineHeight: 1.1,
            color: "#12141c",
          }}
        >
          {titulo}
        </div>
        {universidad && (
          <div style={{ display: "flex", fontSize: 34, color: "#576076" }}>{universidad}</div>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: 20 }}>
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
          {minimo != null
            ? `Ponderado mínimo de postulación: ${minimo} puntos`
            : "El DEMRE no publicó ponderado mínimo para esta carrera"}
        </span>
      </div>
    </div>
  );
}
