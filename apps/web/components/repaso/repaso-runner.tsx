"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { cn } from "@paes-m1/utils";
import {
  ApiError,
  responderRepaso,
  type RepasoPregunta,
  type RepasoRespuesta,
  type Subject,
} from "@/lib/api";
import { getClientToken, loginHref } from "@/lib/auth";
import { COLOR_PRUEBA, NOMBRE_CORTO } from "@/lib/colores-prueba";
import { Escalera, ESCALERA_DIAS } from "@/components/repaso/escalera";

const FECHA = new Intl.DateTimeFormat("es-CL", { day: "numeric", month: "long" });

/**
 * Cuántos caracteres puede tener la alternativa más larga para que las
 * alternativas quepan en dos columnas.
 *
 * Con respuestas como "396 cm²" una sola columna deja una caja de 670 px con
 * siete caracteres adentro: parece un formulario a medio cargar. Con enunciados
 * largos, en cambio, dos columnas parten el texto en tiras ilegibles. El largo
 * decide, no el gusto.
 */
const LARGO_PARA_DOS_COLUMNAS = 32;

/**
 * Una sesión de repaso: las preguntas que falló, de vuelta.
 *
 * La diferencia con Modo Práctica no está en la mecánica --se elige una
 * alternativa y se corrige-- sino en QUÉ se muestra al fallar. Acá cada
 * alternativa incorrecta trae escrito el error exacto que induce a elegirla, y
 * esa es la única razón por la que la segunda vez sale mejor que la primera:
 * el alumno no vuelve a leer la solución correcta, lee por qué su cabeza fue
 * hacia otro lado.
 *
 * Y eso tiene que VERSE. La primera versión era un cuestionario genérico: nada
 * decía que estas preguntas son las que se le escaparon, ni que cada acierto la
 * aleja un peldaño. Ahora la escalera está a la vista, la prueba pone su color,
 * y el avance de la sesión se cuenta pregunta a pregunta en vez de con una
 * barra continua que no dice cuántas faltan.
 */
export function RepasoRunner({
  preguntas,
  pendientesTotales,
}: {
  preguntas: RepasoPregunta[];
  pendientesTotales: number;
}) {
  const router = useRouter();
  const quieto = useReducedMotion();
  const [indice, setIndice] = useState(0);
  const [elegida, setElegida] = useState<number | null>(null);
  const [resultado, setResultado] = useState<RepasoRespuesta | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aciertos, setAciertos] = useState(0);
  const [dominadas, setDominadas] = useState(0);
  const [subidas, setSubidas] = useState(0);

  const pregunta = preguntas[indice];
  const terminado = indice >= preguntas.length;

  async function responder(alternativaId: number) {
    if (resultado || enviando) return;
    setElegida(alternativaId);
    setEnviando(true);
    setError(null);
    try {
      const r = await responderRepaso(
        pregunta.question_id,
        alternativaId,
        getClientToken() ?? undefined
      );
      setResultado(r);
      if (r.is_correct) {
        setAciertos((n) => n + 1);
        setSubidas((n) => n + 1);
      }
      if (r.dominada) setDominadas((n) => n + 1);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push(loginHref("/repaso"));
        return;
      }
      setError("No se pudo guardar tu respuesta. Intenta de nuevo.");
      setElegida(null);
    } finally {
      setEnviando(false);
    }
  }

  function siguiente() {
    setElegida(null);
    setResultado(null);
    setIndice((i) => i + 1);
  }

  if (terminado) {
    return (
      <Resumen
        aciertos={aciertos}
        total={preguntas.length}
        dominadas={dominadas}
        subidas={subidas}
        quedan={Math.max(0, pendientesTotales - preguntas.length)}
        onSeguir={() => router.refresh()}
      />
    );
  }

  const color = COLOR_PRUEBA[pregunta.subject as Subject] ?? "var(--accent)";
  const dosColumnas = pregunta.alternatives.every(
    (a) => a.text.length <= LARGO_PARA_DOS_COLUMNAS
  );
  // El peldaño que se muestra es el de DESPUÉS de responder, para que el
  // alumno vea moverse lo que acaba de ganar.
  const nivelVisible = resultado ? resultado.nivel : pregunta.nivel;

  return (
    // En un monitor la sesión ocupaba el tercio superior y el resto quedaba en
    // blanco: parecía una página a medio cargar. Centrada verticalmente, la
    // pregunta queda donde está mirando el alumno.
    <div className="mx-auto flex min-h-[70vh] max-w-2xl flex-col justify-center py-4">
      {/* ── Cabecera de la sesión ───────────────────────────────────── */}
      <header
        className="overflow-hidden rounded-2xl border border-border bg-surface"
        style={{ borderTopColor: color, borderTopWidth: 3 }}
      >
        <div className="flex flex-wrap items-start justify-between gap-3 px-5 pt-4">
          <div className="min-w-0">
            <p className="text-xs font-medium tracking-wide text-muted uppercase">
              Repaso · {NOMBRE_CORTO[pregunta.subject as Subject] ?? "PAES"}
            </p>
            <h1 className="mt-0.5 truncate font-semibold" style={{ color }}>
              {pregunta.node_name}
            </h1>
          </div>

          {/* En el teléfono esta fila baja bajo el título y ocupa el ancho:
              la escalera se alinea a la izquierda, no flotando al centro. */}
          <div className="flex w-full items-center justify-between gap-4 sm:w-auto sm:justify-end">
            {/* Cuántas veces se le ha resistido. Es lo que convierte "otra
                pregunta" en "esta es LA que no me sale". */}
            {pregunta.veces_fallada > 0 && (
              <span className="rounded-full border border-accent-warm/30 bg-accent-warm/10 px-2.5 py-1 text-xs font-medium text-accent-warm-strong">
                Fallada {pregunta.veces_fallada}{" "}
                {pregunta.veces_fallada === 1 ? "vez" : "veces"}
              </span>
            )}
            <div className="text-left sm:text-right">
              <Escalera
                nivel={nivelVisible}
                color={color}
                className="justify-start sm:justify-end"
              />
              {/* "Peldaño 0 de 5" no le dice nada a nadie. Lo que el alumno
                  quiere saber es cuánto le falta para sacarse la pregunta de
                  encima. */}
              <p className="mt-1.5 text-[11px] whitespace-nowrap text-muted">
                {nivelVisible >= ESCALERA_DIAS.length
                  ? "dominada"
                  : `${ESCALERA_DIAS.length - nivelVisible} ${
                      ESCALERA_DIAS.length - nivelVisible === 1 ? "acierto" : "aciertos"
                    } para dominarla`}
              </p>
            </div>
          </div>
        </div>

        {/* Un segmento por pregunta, no una barra continua: así se ve cuántas
            faltan sin tener que leer un número. */}
        <div className="mt-4 flex gap-1 px-5 pb-4">
          {preguntas.map((p, i) => (
            <span
              key={p.question_id}
              className="h-1.5 flex-1 rounded-full transition-colors duration-500"
              style={{
                backgroundColor:
                  i < indice
                    ? color
                    : i === indice
                      ? `color-mix(in srgb, ${color} 45%, transparent)`
                      : "var(--surface-hover)",
              }}
            />
          ))}
        </div>
      </header>

      {/* ── La pregunta ─────────────────────────────────────────────── */}
      <AnimatePresence mode="wait">
        <motion.div
          key={pregunta.question_id}
          initial={quieto ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={quieto ? undefined : { opacity: 0, y: -8 }}
          transition={{ duration: 0.25 }}
        >
          {pregunta.passage && (
            <div className="mt-5 max-h-72 overflow-y-auto rounded-xl border border-border bg-surface p-4">
              {pregunta.passage_title && (
                <p className="mb-2 font-semibold">{pregunta.passage_title}</p>
              )}
              <p className="text-sm leading-relaxed whitespace-pre-line">{pregunta.passage}</p>
            </div>
          )}

          <p className="mt-6 text-lg leading-relaxed font-medium whitespace-pre-line">
            {pregunta.stem}
          </p>

          {pregunta.image_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={pregunta.image_url} alt="" className="mt-4 max-w-full rounded-lg" />
          )}

          <ul
            className={cn(
              "mt-5 grid gap-2.5",
              dosColumnas ? "sm:grid-cols-2" : "grid-cols-1"
            )}
          >
            {pregunta.alternatives.map((alt) => {
              const esCorrecta = resultado?.correct_alternative_id === alt.id;
              const esElegida = elegida === alt.id;
              const resuelto = resultado !== null;
              return (
                <li key={alt.id}>
                  <button
                    type="button"
                    onClick={() => responder(alt.id)}
                    disabled={resuelto || enviando}
                    className={cn(
                      "group flex h-full w-full items-center gap-3 rounded-xl border-2 p-3.5 text-left transition-all",
                      !resuelto &&
                        "border-border hover:-translate-y-0.5 hover:border-current hover:shadow-sm",
                      resuelto && esCorrecta && "border-success bg-success/10",
                      resuelto && esElegida && !esCorrecta && "border-danger bg-danger/10",
                      resuelto && !esCorrecta && !esElegida && "border-border opacity-45"
                    )}
                    style={!resuelto ? { color } : undefined}
                  >
                    <span
                      className={cn(
                        "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border-2 font-mono text-sm font-bold transition-colors",
                        !resuelto && "border-current",
                        resuelto && esCorrecta && "border-success bg-success text-on-fill",
                        resuelto &&
                          esElegida &&
                          !esCorrecta &&
                          "border-danger bg-danger text-on-fill",
                        resuelto && !esCorrecta && !esElegida && "border-border"
                      )}
                    >
                      {alt.label}
                    </span>
                    <span className="text-foreground">{alt.text}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </motion.div>
      </AnimatePresence>

      {error && (
        <p className="mt-4 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
          {error}
        </p>
      )}

      {/* Quien entra por primera vez no sabe qué es esto ni por qué le sale
          una pregunta que ya vio. Una línea lo explica; desaparece apenas
          responde, porque a esa altura ya lo está viendo funcionar. */}
      {!resultado && (
        <p className="mt-6 text-center text-xs text-muted">
          La fallaste antes. Aciértala {ESCALERA_DIAS.length} veces, con esperas
          cada vez más largas, y sale de tu repaso para siempre.
        </p>
      )}

      {/* ── La corrección ───────────────────────────────────────────── */}
      {resultado && (
        <motion.div
          initial={quieto ? false : { opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mt-5 overflow-hidden rounded-2xl border border-border bg-surface"
        >
          <div
            className={cn(
              "flex items-center justify-between gap-3 px-5 py-3",
              resultado.is_correct ? "bg-success/10" : "bg-danger/10"
            )}
          >
            <p
              className={cn(
                "font-semibold",
                resultado.is_correct ? "text-success" : "text-danger"
              )}
            >
              {resultado.is_correct ? "Correcta" : "Incorrecta"}
            </p>
            <p className="text-right text-xs text-muted">
              {resultado.dominada
                ? "No vuelve a aparecer"
                : resultado.proxima_fecha
                  ? `Vuelve el ${FECHA.format(new Date(`${resultado.proxima_fecha}T12:00:00`))}`
                  : null}
            </p>
          </div>

          <div className="p-5">
            {/* Lo primero que se lee al fallar es POR QUÉ eligió lo que eligió,
                no la solución. La solución la puede leer cualquiera sin haberse
                equivocado; esto solo le sirve a quien cayó justo acá. */}
            {resultado.distractor_justification && (
              <div className="rounded-xl border-l-[3px] border-accent-warm bg-accent-warm/5 py-3 pr-3 pl-4">
                <p className="text-xs font-semibold tracking-wide text-accent-warm-strong uppercase">
                  Dónde se te fue
                </p>
                <p className="mt-1.5">{resultado.distractor_justification}</p>
              </div>
            )}

            {resultado.explanation && (
              <p className="mt-4 text-sm leading-relaxed whitespace-pre-line text-muted">
                {resultado.explanation}
              </p>
            )}

            {resultado.dominada && (
              <p className="mt-4 rounded-lg border border-success/30 bg-success/10 px-3 py-2 text-sm font-medium text-success">
                La dominaste. Cinco aciertos repartidos en dos meses: esta ya no
                vuelve.
              </p>
            )}

            {resultado.newly_unlocked.length > 0 && (
              <p className="mt-3 rounded-lg border border-success/30 bg-success/10 px-3 py-2 text-sm font-medium text-success">
                Desbloqueaste {resultado.newly_unlocked.join(", ")} en el árbol.
              </p>
            )}

            <button
              type="button"
              onClick={siguiente}
              autoFocus
              className="mt-5 w-full rounded-lg px-4 py-3 font-semibold text-on-fill transition hover:opacity-90"
              style={{ backgroundColor: color }}
            >
              {indice + 1 === preguntas.length ? "Ver el resumen" : "Siguiente pregunta"}
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}

/** El cierre de la sesión: qué movió, no solo cuántas acertó. */
function Resumen({
  aciertos,
  total,
  dominadas,
  subidas,
  quedan,
  onSeguir,
}: {
  aciertos: number;
  total: number;
  dominadas: number;
  subidas: number;
  quedan: number;
  onSeguir: () => void;
}) {
  const quieto = useReducedMotion();
  return (
    <motion.div
      initial={quieto ? false : { opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.35 }}
      className="mx-auto max-w-2xl"
    >
      <div className="rounded-2xl border border-border bg-surface p-8 text-center">
        <p className="text-xs font-medium tracking-wide text-muted uppercase">
          Repaso terminado
        </p>
        {/* El número no va en verde: 1 de 11 también es un resultado, y
            pintarlo de "logro" es felicitar por algo que no pasó. El verde se
            reserva para lo que sí es una victoria, abajo. */}
        <p className="mt-2 text-6xl leading-none font-bold">
          {aciertos}
          <span className="text-2xl font-semibold text-muted">/{total}</span>
        </p>

        <div className="mt-7 grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-border p-4">
            <p className="text-3xl font-bold tabular-nums">{subidas}</p>
            <p className="mt-1 text-xs text-muted">
              {subidas === 1 ? "subió un peldaño" : "subieron un peldaño"}
            </p>
          </div>
          {/* Y en cero se muestra neutro: un cero en verde celebra nada. */}
          <div
            className={cn(
              "rounded-xl border p-4",
              dominadas > 0 ? "border-success/30 bg-success/5" : "border-border"
            )}
          >
            <p
              className={cn(
                "text-3xl font-bold tabular-nums",
                dominadas > 0 && "text-success"
              )}
            >
              {dominadas}
            </p>
            <p className="mt-1 text-xs text-muted">
              {dominadas === 1 ? "salió de la cola" : "salieron de la cola"}
            </p>
          </div>
        </div>

        <p className="mt-6 text-sm text-muted">
          Las que acertaste vuelven más adelante; las que fallaste, mañana.
        </p>

        <div className="mt-7 flex flex-col gap-2 sm:flex-row sm:justify-center">
          {quedan > 0 ? (
            <button
              type="button"
              onClick={onSeguir}
              className="rounded-lg bg-accent px-5 py-2.5 font-semibold text-accent-foreground hover:opacity-90"
            >
              Repasar las {quedan} que quedan
            </button>
          ) : (
            <Link
              href="/examen"
              className="rounded-lg bg-accent px-5 py-2.5 font-semibold text-accent-foreground hover:opacity-90"
            >
              Rendir un ensayo
            </Link>
          )}
          <Link
            href="/panel"
            className="rounded-lg border border-border px-5 py-2.5 font-medium hover:bg-surface-hover"
          >
            Volver al panel
          </Link>
        </div>
      </div>
    </motion.div>
  );
}
