"use client";

import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { guardarOnboarding } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * Cuestionario de bienvenida, la primera vez que alguien entra.
 *
 * Cuatro preguntas, una por pantalla, y se puede saltar en cualquier momento.
 * El largo es la decisión más importante acá: cada pregunta extra cuesta
 * estudiantes que cierran la pestaña, así que solo entra la que cambia algo en
 * la plataforma. Preguntar para llenar una base de datos es hacerle perder el
 * tiempo a alguien que vino a estudiar.
 *
 * Qué hace cada respuesta:
 *   pruebas    → el árbol y el configurador de ensayo abren en la principal
 *   curso      → cuánta urgencia tiene lo que le mostramos
 *   primera vez / puntaje anterior → su punto de partida real
 *   horas      → el tamaño del plan de estudio que se le propone
 */

const PRUEBAS = [
  { id: "lectora", label: "Competencia Lectora", nota: "La rinden todos" },
  { id: "m1", label: "Matemática M1", nota: "La rinden casi todos" },
  { id: "m2", label: "Matemática M2", nota: "Ingeniería, ciencias, salud" },
  { id: "ciencias", label: "Ciencias", nota: "Biología, física y química" },
  { id: "historia", label: "Historia y Cs. Sociales", nota: "" },
] as const;

const CURSOS = [
  { id: "tercero", label: "3° medio", nota: "Vas con tiempo" },
  { id: "cuarto", label: "4° medio", nota: "Este es el año" },
  { id: "egresado", label: "Ya egresé", nota: "Rindes como externo" },
] as const;

const HORAS = [
  { valor: 2, label: "Un par de horas", nota: "Menos de 3 a la semana" },
  { valor: 5, label: "Unas 5 horas", nota: "Casi una hora al día" },
  { valor: 10, label: "10 o más", nota: "Preparación intensiva" },
] as const;

const TOTAL_PASOS = 4;

export function Cuestionario({ nombre }: { nombre: string }) {
  const quieto = useReducedMotion();
  const [abierto, setAbierto] = useState(true);
  const [paso, setPaso] = useState(1);
  const [guardando, setGuardando] = useState(false);

  const [pruebas, setPruebas] = useState<string[]>([]);
  const [curso, setCurso] = useState<string | null>(null);
  const [primeraVez, setPrimeraVez] = useState<boolean | null>(null);
  const [puntajeAnterior, setPuntajeAnterior] = useState("");
  const [horas, setHoras] = useState<number | null>(null);

  async function terminar() {
    setGuardando(true);
    try {
      await guardarOnboarding(
        {
          pruebas_objetivo: pruebas,
          curso,
          primera_vez: primeraVez,
          puntaje_anterior: puntajeAnterior ? Number(puntajeAnterior) : null,
          horas_semana: horas,
        },
        getClientToken() ?? undefined
      );
    } catch {
      // Si falla el guardado no se le bloquea la entrada: el cuestionario es
      // para ayudarlo, no un peaje.
    } finally {
      setAbierto(false);
      // La página se recarga para que el resto de la plataforma tome sus
      // respuestas: qué prueba abrir, qué plan proponerle.
      window.location.reload();
    }
  }

  if (!abierto) return null;

  const puedeSeguir =
    (paso === 1 && pruebas.length > 0) ||
    (paso === 2 && curso !== null) ||
    (paso === 3 && primeraVez !== null) ||
    (paso === 4 && horas !== null);

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-end justify-center bg-foreground/40 p-4 backdrop-blur-sm sm:items-center"
        initial={quieto ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-labelledby="titulo-cuestionario"
          initial={quieto ? false : { opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="card-panel w-full max-w-lg overflow-hidden p-6 sm:p-7"
        >
          {/* Avance: cuatro pasos cortos, y se ve que son cuatro. */}
          <div className="flex items-center gap-2">
            {Array.from({ length: TOTAL_PASOS }, (_, i) => (
              <span
                key={i}
                aria-hidden
                className={
                  "h-1 flex-1 rounded-full " +
                  (i < paso ? "bg-accent" : "bg-surface-hover")
                }
              />
            ))}
          </div>
          <p className="mt-3 text-xs text-muted">
            Paso {paso} de {TOTAL_PASOS}
          </p>

          {paso === 1 && (
            <Paso
              titulo={`Hola ${nombre}, ¿qué pruebas vas a rendir?`}
              ayuda="Elige todas las que apliquen. Con esto la plataforma abre directo en lo tuyo."
            >
              <div className="flex flex-col gap-2">
                {PRUEBAS.map((p) => {
                  const elegida = pruebas.includes(p.id);
                  return (
                    <button
                      key={p.id}
                      type="button"
                      aria-pressed={elegida}
                      onClick={() =>
                        setPruebas((actuales) =>
                          actuales.includes(p.id)
                            ? actuales.filter((x) => x !== p.id)
                            : [...actuales, p.id]
                        )
                      }
                      className={
                        "flex items-center justify-between gap-3 rounded-xl border p-3 text-left transition " +
                        (elegida
                          ? "border-accent bg-accent/5 ring-1 ring-accent"
                          : "border-border hover:border-border-strong")
                      }
                    >
                      <span className="min-w-0">
                        <span className="block text-sm font-medium">{p.label}</span>
                        {p.nota && (
                          <span className="block text-xs text-muted">{p.nota}</span>
                        )}
                      </span>
                      <span
                        aria-hidden
                        className={
                          "flex h-5 w-5 shrink-0 items-center justify-center rounded-md border text-xs " +
                          (elegida
                            ? "border-accent bg-accent text-accent-foreground"
                            : "border-border-strong")
                        }
                      >
                        {elegida ? "✓" : ""}
                      </span>
                    </button>
                  );
                })}
              </div>
            </Paso>
          )}

          {paso === 2 && (
            <Paso titulo="¿En qué curso vas?" ayuda="Para saber cuánto tiempo tienes.">
              <Opciones
                opciones={CURSOS.map((c) => ({
                  id: c.id,
                  label: c.label,
                  nota: c.nota,
                }))}
                elegida={curso}
                onElegir={setCurso}
              />
            </Paso>
          )}

          {paso === 3 && (
            <Paso
              titulo="¿Es tu primera vez rindiendo la PAES?"
              ayuda="Si ya la rendiste, tu puntaje anterior es el punto de partida real."
            >
              <Opciones
                opciones={[
                  { id: "si", label: "Sí, es la primera", nota: "" },
                  { id: "no", label: "Ya la rendí antes", nota: "" },
                ]}
                elegida={primeraVez === null ? null : primeraVez ? "si" : "no"}
                onElegir={(v) => setPrimeraVez(v === "si")}
              />
              {primeraVez === false && (
                <label className="mt-4 block text-sm">
                  <span className="block text-xs text-muted">
                    Tu mejor puntaje anterior (opcional)
                  </span>
                  <input
                    inputMode="numeric"
                    value={puntajeAnterior}
                    onChange={(e) =>
                      setPuntajeAnterior(e.target.value.replace(/\D/g, "").slice(0, 4))
                    }
                    placeholder="Ej: 620"
                    className="mt-1 w-32 rounded-lg border border-border bg-background px-3 py-2 tabular-nums"
                  />
                </label>
              )}
            </Paso>
          )}

          {paso === 4 && (
            <Paso
              titulo="¿Cuánto puedes estudiar por semana?"
              ayuda="Con esto ajustamos el tamaño del plan que te proponemos. Se puede cambiar después."
            >
              <Opciones
                opciones={HORAS.map((h) => ({
                  id: String(h.valor),
                  label: h.label,
                  nota: h.nota,
                }))}
                elegida={horas === null ? null : String(horas)}
                onElegir={(v) => setHoras(Number(v))}
              />
            </Paso>
          )}

          <div className="mt-6 flex flex-wrap items-center gap-3">
            {paso < TOTAL_PASOS ? (
              <button
                type="button"
                disabled={!puedeSeguir}
                onClick={() => setPaso((p) => p + 1)}
                className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground disabled:opacity-40"
              >
                Continuar →
              </button>
            ) : (
              <button
                type="button"
                disabled={!puedeSeguir || guardando}
                onClick={terminar}
                className="btn-warm rounded-lg px-5 py-2.5 text-sm font-semibold text-on-fill disabled:opacity-40"
              >
                {guardando ? "Guardando…" : "Empezar"}
              </button>
            )}

            {paso > 1 && (
              <button
                type="button"
                onClick={() => setPaso((p) => p - 1)}
                className="text-sm text-muted hover:text-foreground"
              >
                Atrás
              </button>
            )}

            {/* Saltar cuenta como responder: no se vuelve a preguntar. Insistir
                con un cuestionario que alguien ya rechazó es la forma más
                rápida de que deje de entrar. */}
            <button
              type="button"
              onClick={terminar}
              className="ml-auto text-sm text-muted underline-offset-4 hover:text-foreground hover:underline"
            >
              Saltar
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

function Paso({
  titulo,
  ayuda,
  children,
}: {
  titulo: string;
  ayuda: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mt-4">
      <h2 id="titulo-cuestionario" className="text-xl font-bold tracking-tight">
        {titulo}
      </h2>
      <p className="mt-1 text-sm leading-relaxed text-muted">{ayuda}</p>
      <div className="mt-5">{children}</div>
    </div>
  );
}

function Opciones({
  opciones,
  elegida,
  onElegir,
}: {
  opciones: { id: string; label: string; nota: string }[];
  elegida: string | null;
  onElegir: (id: string) => void;
}) {
  return (
    <div className="flex flex-col gap-2">
      {opciones.map((o) => (
        <button
          key={o.id}
          type="button"
          aria-pressed={elegida === o.id}
          onClick={() => onElegir(o.id)}
          className={
            "rounded-xl border p-3 text-left transition " +
            (elegida === o.id
              ? "border-accent bg-accent/5 ring-1 ring-accent"
              : "border-border hover:border-border-strong")
          }
        >
          <span className="block text-sm font-medium">{o.label}</span>
          {o.nota && <span className="block text-xs text-muted">{o.nota}</span>}
        </button>
      ))}
    </div>
  );
}
