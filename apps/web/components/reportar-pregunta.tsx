"use client";

import { useEffect, useId, useRef, useState } from "react";
import { cn } from "@paes-m1/utils";
import { IconoExclamacion } from "@/components/ui/iconos";
import { getClientToken } from "@/lib/auth";
import { reportarPregunta, type ContextoReporte, type MotivoReporte } from "@/lib/api";

/**
 * El botón para avisar que una pregunta está mal.
 *
 * El banco lo escribimos nosotros y tiene miles de preguntas.
 * `verificar_banco.py` recalcula la aritmética y comprueba la estructura, pero
 * no puede ver que un enunciado sea ambiguo, que dos alternativas sean
 * defendibles o que la clave quedó apuntando a la que no es. Eso lo ve quien
 * está respondiendo, y hasta ahora no tenía dónde decirlo: el único camino era
 * escribir un correo en medio del ensayo, que es lo mismo que no tener camino.
 *
 * Por eso es **chico y callado**: un icono que hereda el color del texto
 * apagado, del tamaño de la etiqueta que tiene al lado. No compite con las
 * alternativas ni invita a apretarlo por curiosidad; el que lo busca es porque
 * ya sospecha algo. Y se responde con un toque —los motivos son botones y el
 * comentario es opcional— porque en el minuto 80 de un ensayo nadie va a
 * redactar un párrafo.
 */

const MOTIVOS: { valor: MotivoReporte; etiqueta: string }[] = [
  { valor: "respuesta_incorrecta", etiqueta: "La respuesta correcta está mal" },
  { valor: "varias_correctas", etiqueta: "Hay más de una alternativa correcta" },
  { valor: "enunciado_confuso", etiqueta: "El enunciado no se entiende" },
  { valor: "datos_erroneos", etiqueta: "Faltan datos o los datos no calzan" },
  { valor: "otro", etiqueta: "Otra cosa" },
];

/** Durante el ensayo todavía no sabe cuál era la correcta, así que ese motivo
 *  no se ofrece: elegirlo ahí sería adivinar, y nos llegaría ruido en vez de
 *  avisos. */
const MOTIVOS_EN_ENSAYO = MOTIVOS.filter((m) => m.valor !== "respuesta_incorrecta");

/** Las preguntas que ya se reportaron en esta carga de la página.
 *
 * Vive a nivel de módulo porque la misma pregunta aparece dos veces en el
 * mismo recorrido —al rendir y al revisar— y el botón tiene que acordarse: sin
 * esto, la segunda vez se ofrece como si nada, el alumno reporta de nuevo y el
 * servidor descarta el aviso repetido sin que él se entere. */
const reportadas = new Set<number>();

type Estado = "cerrado" | "abierto" | "enviando" | "listo" | "error";

export function ReportarPregunta({
  questionId,
  contexto,
  className,
}: {
  questionId: number;
  contexto: ContextoReporte;
  className?: string;
}) {
  const [estado, setEstado] = useState<Estado>(reportadas.has(questionId) ? "listo" : "cerrado");
  const [motivo, setMotivo] = useState<MotivoReporte | null>(null);
  const [comentario, setComentario] = useState("");
  const contenedor = useRef<HTMLDivElement>(null);
  const panelId = useId();

  const abierto = estado === "abierto" || estado === "enviando" || estado === "error";
  const yaReportada = estado === "listo";

  // Se cierra al tocar fuera y con Escape. En un ensayo esto se abre sin
  // querer con el pulgar, y quedarse abierto tapando una alternativa es peor
  // que no haber puesto el botón.
  useEffect(() => {
    if (!abierto) return;
    const alTocarFuera = (e: MouseEvent) => {
      if (!contenedor.current?.contains(e.target as Node)) setEstado("cerrado");
    };
    const alTeclear = (e: KeyboardEvent) => {
      if (e.key === "Escape") setEstado("cerrado");
    };
    document.addEventListener("mousedown", alTocarFuera);
    document.addEventListener("keydown", alTeclear);
    return () => {
      document.removeEventListener("mousedown", alTocarFuera);
      document.removeEventListener("keydown", alTeclear);
    };
  }, [abierto]);

  async function enviar(elegido: MotivoReporte) {
    setEstado("enviando");
    try {
      await reportarPregunta(
        {
          question_id: questionId,
          motivo: elegido,
          comentario: comentario.trim() || null,
          contexto,
        },
        getClientToken() ?? undefined
      );
      reportadas.add(questionId);
      setEstado("listo");
    } catch {
      // No se pierde lo escrito: el panel queda abierto con el mensaje y el
      // botón vuelve a estar disponible.
      setEstado("error");
    }
  }

  if (yaReportada) {
    return (
      <span
        className={cn(
          "inline-flex shrink-0 items-center gap-1 text-[11px] font-medium text-success",
          className
        )}
      >
        <IconoExclamacion tamano={13} />
        Reportada
      </span>
    );
  }

  const motivos = contexto === "ensayo" ? MOTIVOS_EN_ENSAYO : MOTIVOS;

  return (
    <div ref={contenedor} className={cn("relative shrink-0", className)}>
      <button
        type="button"
        onClick={() => setEstado(abierto ? "cerrado" : "abierto")}
        aria-expanded={abierto}
        aria-controls={abierto ? panelId : undefined}
        aria-label="Reportar un problema con esta pregunta"
        title="Reportar un problema con esta pregunta"
        className={cn(
          "flex h-7 w-7 items-center justify-center rounded-lg text-muted transition",
          "hover:bg-surface-hover hover:text-warning",
          abierto && "bg-surface-hover text-warning"
        )}
      >
        <IconoExclamacion tamano={15} />
      </button>

      {abierto && (
        <div
          id={panelId}
          role="dialog"
          aria-label="Reportar un problema con esta pregunta"
          // Anclado a la derecha porque el botón vive en el borde derecho de la
          // tarjeta: abrirlo hacia la izquierda es lo que lo mantiene dentro de
          // la pantalla en un teléfono.
          className="absolute right-0 z-30 mt-1.5 w-[17.5rem] rounded-xl border border-border bg-surface p-3 text-left shadow-lg"
        >
          <p className="text-[11px] font-semibold tracking-wide text-muted uppercase">
            ¿Qué está mal en esta pregunta?
          </p>

          <div className="mt-2 space-y-1">
            {motivos.map((m) => (
              <button
                key={m.valor}
                type="button"
                disabled={estado === "enviando"}
                onClick={() => {
                  setMotivo(m.valor);
                  void enviar(m.valor);
                }}
                className={cn(
                  "w-full rounded-lg border border-border px-2.5 py-2 text-left text-xs leading-snug transition",
                  "hover:border-warning/50 hover:bg-warning/5 disabled:opacity-60",
                  motivo === m.valor && "border-warning/50 bg-warning/10"
                )}
              >
                {m.etiqueta}
              </button>
            ))}
          </div>

          <textarea
            value={comentario}
            onChange={(e) => setComentario(e.target.value.slice(0, 500))}
            rows={2}
            disabled={estado === "enviando"}
            placeholder="Si quieres, cuéntanos más (opcional)"
            className="mt-2 w-full resize-none rounded-lg border border-border bg-background px-2.5 py-2 text-xs text-foreground placeholder:text-muted focus:border-accent/50 focus:outline-none"
          />

          <p className="mt-2 text-[11px] leading-snug text-muted">
            {estado === "enviando"
              ? "Enviando…"
              : estado === "error"
                ? "No se pudo enviar. Inténtalo de nuevo en un momento."
                : "Elige un motivo y el aviso se envía. Lo revisamos a mano."}
          </p>
        </div>
      )}
    </div>
  );
}
