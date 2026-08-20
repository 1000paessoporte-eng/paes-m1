/**
 * La tarjeta de resultado que se comparte, dibujada en un canvas.
 *
 * Vive fuera del componente porque es una función pura: recibe números y pinta
 * píxeles, sin React de por medio. Así se puede mirar y ajustar sin montar la
 * pantalla de resultados completa, que exige una cuenta y un ensayo rendido.
 */
import type { BreakdownItem } from "@/lib/api";

/** Formato vertical 4:5, que es el que menos recorta Instagram y WhatsApp. */
export const ANCHO = 1080;
export const ALTO = 1350;

export type DatosTarjeta = {
  puntaje: number;
  prueba: string;
  correctas: number;
  total: number;
  ejes: BreakdownItem[];
};

/** Dibuja la tarjeta. Todo en colores fijos: la imagen viaja sola, sin el
 *  tema claro/oscuro del sitio que la generó. */
export function dibujar(
  ctx: CanvasRenderingContext2D,
  datos: DatosTarjeta
) {
  const { puntaje, prueba, correctas, total, ejes } = datos;

  ctx.fillStyle = "#0f1016";
  ctx.fillRect(0, 0, ANCHO, ALTO);

  const brillo = ctx.createRadialGradient(200, 180, 0, 200, 180, 900);
  brillo.addColorStop(0, "rgba(124,58,237,0.35)");
  brillo.addColorStop(1, "rgba(124,58,237,0)");
  ctx.fillStyle = brillo;
  ctx.fillRect(0, 0, ANCHO, ALTO);

  const sans = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
  const margen = 96;

  ctx.textAlign = "left";
  ctx.fillStyle = "#a78bfa";
  ctx.font = `600 34px ${sans}`;
  ctx.fillText(prueba.toUpperCase(), margen, 170);

  ctx.fillStyle = "#8b93a7";
  ctx.font = `500 34px ${sans}`;
  ctx.fillText("PUNTAJE ESTIMADO", margen, 300);

  ctx.fillStyle = "#ffffff";
  ctx.font = `800 260px ${sans}`;
  ctx.fillText(String(puntaje), margen, 520);

  const anchoPuntaje = ctx.measureText(String(puntaje)).width;
  ctx.fillStyle = "#8b93a7";
  ctx.font = `600 56px ${sans}`;
  ctx.fillText("/1000", margen + anchoPuntaje + 18, 520);

  ctx.fillStyle = "#c9cede";
  ctx.font = `500 38px ${sans}`;
  ctx.fillText(`${correctas} de ${total} respuestas correctas`, margen, 600);

  // Los ejes, hasta cuatro: más barras entran pero no se leen en un teléfono.
  let y = 720;
  ctx.font = `600 34px ${sans}`;
  for (const eje of ejes.slice(0, 4)) {
    ctx.fillStyle = "#e6e8f0";
    ctx.fillText(eje.name, margen, y);

    ctx.fillStyle = "#8b93a7";
    ctx.textAlign = "right";
    ctx.fillText(`${Math.round(eje.percentage)}%`, ANCHO - margen, y);
    ctx.textAlign = "left";

    ctx.fillStyle = "#23252f";
    ctx.fillRect(margen, y + 22, ANCHO - margen * 2, 16);
    ctx.fillStyle = eje.percentage >= 60 ? "#34d399" : "#fb923c";
    ctx.fillRect(margen, y + 22, ((ANCHO - margen * 2) * eje.percentage) / 100, 16);

    y += 108;
  }

  ctx.fillStyle = "#ffffff";
  ctx.font = `800 54px ${sans}`;
  ctx.fillText("1000paes.cl", margen, ALTO - 150);

  // La letra chica que impide que esto pase por un resultado oficial.
  ctx.fillStyle = "#6f7689";
  ctx.font = `400 26px ${sans}`;
  ctx.fillText(
    "Estimación con las tablas de transformación del DEMRE.",
    margen,
    ALTO - 96
  );
  ctx.fillText("No es un resultado oficial.", margen, ALTO - 60);
}
