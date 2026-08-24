"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@paes-m1/utils";
import { Burbuja } from "@/components/ui/burbuja";
import { TextoRico } from "@/components/texto-rico";
import { COLOR_PRUEBA, NOMBRE_CORTO } from "@/lib/colores-prueba";
import type { Subject } from "@/lib/api";

/**
 * El hero de la portada ES el producto: una pregunta real, con el reloj
 * corriendo, que se puede responder sin cuenta.
 *
 * Antes acá había una tarjeta de puntaje inventada. Se veía bien y no probaba
 * nada: quien llegaba tenía que creernos. De cada 65 personas que llegaron a
 * la portada en un mes, 10 abrieron un ensayo; el resto se fue sin ver jamás
 * una pregunta, que es lo único que este producto tiene para mostrar.
 *
 * Todo lo que aparece acá es lo mismo que verá adentro: la burbuja del cartón
 * de respuestas, el reloj contra el tiempo oficial de la prueba, la corrección
 * con el desarrollo paso a paso. No es una maqueta del producto, es el
 * producto con una pregunta.
 *
 * Se carga en el NAVEGADOR y no en el servidor a propósito: la portada es
 * estática y cacheada, así que hornear la pregunta en el HTML le daría la
 * misma a todo el mundo durante horas. Y si la API no responde, el hero se
 * degrada a su titular y su botón en vez de caerse.
 */

/** Cuántos segundos concede la prueba oficial por pregunta, si la API no responde. */
const SEGUNDOS_POR_PREGUNTA_M1 = 129;

interface Alternativa {
  id: number;
  label: string;
  text: string;
}

interface Pregunta {
  id: number;
  stem: string;
  subject: Subject;
  node_name: string;
  axis_label: string;
  alternatives: Alternativa[];
}

interface Correccion {
  is_correct: boolean;
  correct_alternative_id: number;
  explanation: string | null;
  /** El error que lleva justo a la alternativa marcada. Null si acertó. */
  distractor_justification?: string | null;
}

function reloj(segundos: number): string {
  const m = Math.floor(segundos / 60);
  const s = Math.floor(segundos % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function HeroPregunta() {
  const quieto = useReducedMotion();
  const [pregunta, setPregunta] = useState<Pregunta | null>(null);
  const [fallo, setFallo] = useState(false);
  const [presupuesto, setPresupuesto] = useState(SEGUNDOS_POR_PREGUNTA_M1);
  const [elegida, setElegida] = useState<number | null>(null);
  const [correccion, setCorreccion] = useState<Correccion | null>(null);
  const [segundos, setSegundos] = useState(0);
  const corriendoRef = useRef(true);

  useEffect(() => {
    let vivo = true;
    (async () => {
      try {
        const [rp, ro] = await Promise.all([
          fetch("/api/demo/questions?subject=m1"),
          fetch("/api/exam/options?subject=m1"),
        ]);
        if (!rp.ok) throw new Error("sin preguntas");
        const preguntas: Pregunta[] = await rp.json();
        if (!vivo || preguntas.length === 0) return;
        setPregunta(preguntas[0]);
        if (ro.ok) {
          const opciones = await ro.json();
          if (opciones?.seconds_per_question) {
            setPresupuesto(Math.round(opciones.seconds_per_question));
          }
        }
      } catch {
        if (vivo) setFallo(true);
      }
    })();
    return () => {
      vivo = false;
    };
  }, []);

  // El reloj arranca cuando la pregunta está en pantalla y se detiene al
  // responder: contar tiempo de algo que no se está mirando no mide nada.
  useEffect(() => {
    if (!pregunta || correccion) return;
    const id = setInterval(() => {
      if (corriendoRef.current) setSegundos((s) => s + 1);
    }, 1000);
    return () => clearInterval(id);
  }, [pregunta, correccion]);

  const responder = useCallback(
    async (alternativaId: number) => {
      if (!pregunta || correccion) return;
      setElegida(alternativaId);
      corriendoRef.current = false;
      try {
        const r = await fetch("/api/demo/grade", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            answers: [
              { question_id: pregunta.id, selected_alternative_id: alternativaId },
            ],
          }),
        });
        if (!r.ok) throw new Error("no se pudo corregir");
        const data = await r.json();
        setCorreccion(data.items[0]);
      } catch {
        // Sin corrección no se inventa un resultado: se suelta la selección y
        // el alumno puede volver a intentarlo.
        setElegida(null);
        corriendoRef.current = true;
      }
    },
    [pregunta, correccion]
  );

  if (fallo) return null;

  const color = pregunta ? COLOR_PRUEBA[pregunta.subject] : "var(--prueba-m1)";
  const excedido = segundos > presupuesto;

  return (
    <div className="relative">
      <div
        className="overflow-hidden rounded-2xl border border-border bg-background shadow-[0_1px_2px_rgb(var(--sombra-color)/0.04),0_24px_48px_-24px_rgb(var(--sombra-color)/0.18)]"
        style={{ borderTopColor: color, borderTopWidth: 3 }}
      >
        {/* ── Cabecera: misma que la del ensayo de verdad ────────────── */}
        <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-3">
          <div className="min-w-0">
            <p className="text-[11px] font-medium tracking-wide text-muted uppercase">
              {pregunta ? NOMBRE_CORTO[pregunta.subject] : "Matemática M1"}
            </p>
            <p className="truncate text-sm font-semibold" style={{ color }}>
              {pregunta ? pregunta.node_name : "Cargando una pregunta…"}
            </p>
          </div>
          <div className="shrink-0 text-right">
            <p
              className={cn(
                "font-display text-xl leading-none font-bold tabular-nums",
                excedido && !correccion ? "text-accent-warm-strong" : "text-foreground"
              )}
            >
              {reloj(segundos)}
            </p>
            <p className="mt-0.5 text-[11px] text-muted tabular-nums">
              de {reloj(presupuesto)}
            </p>
          </div>
        </div>

        <div className="p-5">
          {!pregunta ? (
            <Esqueleto />
          ) : (
            <>
              <TextoRico texto={pregunta.stem} className="text-base font-medium" />

              <ul className="mt-4 space-y-2">
                {pregunta.alternatives.map((alt) => {
                  const esCorrecta = correccion?.correct_alternative_id === alt.id;
                  const esElegida = elegida === alt.id;
                  const resuelto = correccion !== null;
                  return (
                    <li key={alt.id}>
                      <button
                        type="button"
                        onClick={() => responder(alt.id)}
                        disabled={resuelto}
                        aria-pressed={esElegida}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-lg border p-3 text-left text-sm transition duration-150",
                          !resuelto &&
                            "border-border hover:border-border-strong hover:bg-surface-hover active:scale-[0.99]",
                          resuelto && esCorrecta && "border-success bg-success/10",
                          resuelto && esElegida && !esCorrecta && "border-danger bg-danger/10",
                          resuelto && !esCorrecta && !esElegida && "border-border opacity-45"
                        )}
                      >
                        <Burbuja letra={alt.label} marcada={esElegida} tamano="chica" />
                        <TextoRico texto={alt.text} inline />
                      </button>
                    </li>
                  );
                })}
              </ul>

              {correccion && (
                <motion.div
                  initial={quieto ? false : { opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="mt-4 rounded-xl border border-border bg-surface p-4"
                >
                  <p
                    className={cn(
                      "text-sm font-semibold",
                      correccion.is_correct ? "text-success" : "text-danger"
                    )}
                  >
                    {correccion.is_correct
                      ? "Correcta. Así se ve cada una de las 65."
                      : "Incorrecta. Esto es lo que verías en el ensayo:"}
                  </p>

                  {/* El error propio antes de la resolución general. Es la
                      promesa que hace la sección de más abajo de esta misma
                      portada ("no «fallaste geometría»"), cumplida acá arriba
                      en la primera pregunta que alguien responde. */}
                  {!correccion.is_correct && correccion.distractor_justification && (
                    <p className="mt-2 text-sm font-medium leading-relaxed text-foreground">
                      {correccion.distractor_justification}
                    </p>
                  )}

                  {correccion.explanation && (
                    <div className="mt-2 text-sm leading-relaxed text-muted">
                      <TextoRico texto={correccion.explanation} />
                    </div>
                  )}

                  <Link
                    href="/registro"
                    className="btn-glow mt-4 flex w-full items-center justify-center rounded-lg px-4 py-3 text-sm font-semibold text-accent-foreground"
                  >
                    Rendir el ensayo completo →
                  </Link>
                  <p className="mt-2 text-center text-xs text-muted">
                    Gratis, sin tarjeta. Al terminar tienes tu puntaje estimado.
                  </p>
                </motion.div>
              )}
            </>
          )}
        </div>
      </div>

      {/* La invitación va FUERA de la tarjeta mientras no ha respondido: dentro
          competiría con las alternativas, que es lo único que queremos que
          toque en este momento. */}
      {pregunta && !correccion && (
        <p className="mt-3 text-center text-xs text-muted">
          Es una pregunta real del banco. Elige una alternativa y te la corregimos.
        </p>
      )}
    </div>
  );
}

function Esqueleto() {
  return (
    <div className="animate-pulse space-y-3" aria-hidden>
      <div className="h-4 w-full rounded bg-surface-hover" />
      <div className="h-4 w-3/4 rounded bg-surface-hover" />
      <div className="mt-5 space-y-2">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-12 rounded-lg bg-surface-hover" />
        ))}
      </div>
    </div>
  );
}
