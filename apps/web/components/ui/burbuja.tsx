import { cn } from "@paes-m1/utils";

/**
 * La burbuja del cartón de respuestas: A, B, C, D.
 *
 * Es el elemento de marca de 1000paes. El cartón con burbujas rellenadas a
 * lápiz es el artefacto que reconoce cualquiera que haya rendido la PAES, y
 * coincide con la acción central del producto, así que la identidad vive en el
 * mismo gesto que el estudiante repite cientos de veces.
 *
 * Deliberadamente NO se usa fuera del momento de responder. Una marca que
 * aparece en todas partes deja de significar algo; esta gana su fuerza de
 * salir siempre en el mismo lugar.
 *
 * El color nunca es la única señal de que está marcada: la letra cambia de
 * peso y el contenedor lleva `aria-pressed`.
 */
export function Burbuja({
  letra,
  marcada,
  tamano = "normal",
  className,
}: {
  letra: string;
  marcada: boolean;
  tamano?: "normal" | "chica";
  className?: string;
}) {
  return (
    <span
      aria-hidden
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full",
        tamano === "chica" ? "h-6 w-6 text-xs" : "h-7 w-7 text-sm",
        marcada ? "burbuja burbuja-marcada font-bold text-on-fill" : "burbuja font-medium text-muted",
        className
      )}
    >
      {letra}
    </span>
  );
}
