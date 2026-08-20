"use client";

import { useRef, useState } from "react";
import type { BreakdownItem } from "@/lib/api";
import { ALTO, ANCHO, dibujar } from "@/lib/tarjeta-resultado";

type Estado = "quieto" | "generando" | "compartido" | "descargado" | "error";

/**
 * Convierte el resultado del ensayo en una imagen para compartir.
 *
 * Por qué existe: el momento en que alguien termina un ensayo y ve su puntaje
 * es el único del producto que da ganas de mostrarle a otro, y hasta ahora
 * moría en la pantalla. Es también el canal más barato que tiene el proyecto,
 * que hoy no tiene ninguno.
 *
 * Se dibuja en el NAVEGADOR, no en el servidor. El resultado de un ensayo es
 * un dato privado del estudiante: generarlo en el servidor obligaría a exponer
 * una URL con su puntaje, y una URL así se indexa, se filtra y se adivina.
 * Acá la imagen nace y muere en su teléfono salvo que él decida mandarla.
 *
 * La imagen dice "PUNTAJE ESTIMADO" en grande y nombra la fuente de la tabla.
 * No es un adorno legal: una tarjeta que se pueda confundir con un resultado
 * oficial del DEMRE es exactamente el tipo de dato inventado que este proyecto
 * no publica, y acá el número viaja fuera del sitio sin nuestro contexto.
 */
export function CompartirResultado({
  puntaje,
  prueba,
  correctas,
  total,
  ejes,
}: {
  puntaje: number;
  prueba: string;
  correctas: number;
  total: number;
  ejes: BreakdownItem[];
}) {
  const [estado, setEstado] = useState<Estado>("quieto");
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  async function generar(): Promise<File | null> {
    const canvas = canvasRef.current ?? document.createElement("canvas");
    canvasRef.current = canvas;
    canvas.width = ANCHO;
    canvas.height = ALTO;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    dibujar(ctx, { puntaje, prueba, correctas, total, ejes });

    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob(resolve, "image/png")
    );
    if (!blob) return null;
    return new File([blob], `mi-ensayo-1000paes.png`, { type: "image/png" });
  }

  async function compartir() {
    setEstado("generando");
    try {
      const archivo = await generar();
      if (!archivo) {
        setEstado("error");
        return;
      }

      // En el teléfono, la hoja nativa de compartir. `canShare` con el archivo
      // es la única comprobación fiable: hay navegadores que traen `share`
      // pero no aceptan archivos, y ahí la llamada falla en silencio.
      if (navigator.canShare?.({ files: [archivo] })) {
        await navigator.share({
          files: [archivo],
          text: `Saqué ${puntaje} puntos estimados en un ensayo de ${prueba} en 1000paes.cl`,
        });
        setEstado("compartido");
        return;
      }

      descargar(archivo);
      setEstado("descargado");
    } catch (err) {
      // Cancelar la hoja de compartir lanza AbortError: no es un fallo, es que
      // la persona se arrepintió. Mostrarle un error por eso sería mentirle.
      if (err instanceof DOMException && err.name === "AbortError") {
        setEstado("quieto");
        return;
      }
      setEstado("error");
    }
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        type="button"
        onClick={compartir}
        disabled={estado === "generando"}
        className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover disabled:opacity-50"
      >
        {estado === "generando" ? "Generando…" : "Compartir mi resultado"}
      </button>

      {estado === "descargado" && (
        <p className="text-xs text-muted">
          Imagen descargada. Ya puedes subirla o mandarla por donde quieras.
        </p>
      )}
      {estado === "error" && (
        <p className="text-xs text-danger">No se pudo generar la imagen.</p>
      )}
    </div>
  );
}

function descargar(archivo: File) {
  const url = URL.createObjectURL(archivo);
  const a = document.createElement("a");
  a.href = url;
  a.download = archivo.name;
  a.click();
  URL.revokeObjectURL(url);
}
