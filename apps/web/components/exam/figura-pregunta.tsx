import { cn } from "@paes-m1/utils";

import { DESCRIPCION_FIGURA } from "@/lib/figuras";

/**
 * La figura de una pregunta: el gráfico, el esquema o el diagrama del que
 * habla el enunciado.
 *
 * En Ciencias buena parte de la prueba oficial se apoya en una imagen —un
 * corte de célula, un pedigrí, una curva de población— y la pregunta no se
 * puede contestar sin mirarla. Las nuestras son propias: las de la PAES tienen
 * derechos de la Universidad de Chile, igual que sus enunciados.
 *
 * Va SIEMPRE sobre fondo claro, también cuando el sitio está en modo oscuro.
 * Son dibujos de línea negra sobre transparente: en oscuro desaparecerían.
 * Invertirlos tampoco sirve, porque el color acá significa algo (el relleno de
 * un individuo afectado en un pedigrí, el rojo de la capacidad de carga), y una
 * inversión lo cambiaría. Es la misma decisión que toma la prueba real: la
 * lámina es blanca.
 */
export function FiguraPregunta({
  src,
  className,
}: {
  src: string;
  className?: string;
}) {
  return (
    <figure
      className={cn(
        "mt-4 overflow-x-auto rounded-xl border border-border bg-white p-3",
        className
      )}
    >
      {/* next/image no aporta nada acá: son SVG del propio sitio, ya pesan
          poco y no hay nada que optimizar ni redimensionar. */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={DESCRIPCION_FIGURA[src] ?? "Figura de la pregunta"}
        className="mx-auto block h-auto w-full max-w-xl"
      />
    </figure>
  );
}
