"use client";

import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { guardarOnboarding } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * La única pregunta que se hace antes de dejar entrar.
 *
 * Fueron cuatro pasos hasta el 2026-08-18. Los datos de producción mostraron
 * lo que cuestan: de seis personas que lo vieron, tres lo completaron, dos lo
 * saltaron entero y una contestó la primera pregunta y abandonó en la segunda.
 * La mitad de la gente que llega a esta pantalla no llega al final, y llegar
 * al final no era el objetivo: el objetivo era que se quedaran.
 *
 * Se conservó la pregunta que de verdad configura la plataforma (qué pruebas
 * va a rendir: define en qué abre el árbol y el configurador de ensayo) y se
 * sacaron las otras tres. No se perdieron: curso, si es su primera PAES, su
 * puntaje anterior y sus horas semanales se editan en /perfil, donde ya vivían
 * (`MisDatos`), y quien no las llene igual recibe un plan completo porque
 * `_plan_semanal` trata la ausencia de horas como "propón todo".
 *
 * Regla para quien venga después: una pregunta más acá se paga en estudiantes
 * que cierran la pestaña. Si algo se puede preguntar después, se pregunta
 * después; si se puede deducir del comportamiento, no se pregunta.
 */

const PRUEBAS = [
  { id: "lectora", label: "Competencia Lectora", nota: "La rinden todos" },
  { id: "m1", label: "Matemática M1", nota: "La rinden casi todos" },
  { id: "m2", label: "Matemática M2", nota: "Ingeniería, ciencias, salud" },
  { id: "ciencias", label: "Ciencias", nota: "Biología, física y química" },
  { id: "historia", label: "Historia y Cs. Sociales", nota: "" },
] as const;

export function Cuestionario({ nombre }: { nombre: string }) {
  const quieto = useReducedMotion();
  const [abierto, setAbierto] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [pruebas, setPruebas] = useState<string[]>([]);

  async function terminar() {
    setGuardando(true);
    try {
      // Solo viaja lo que se preguntó. El resto de los campos los completa
      // /perfil cuando la persona quiera, y el backend solo pisa lo que recibe.
      await guardarOnboarding(
        { pruebas_objetivo: pruebas },
        getClientToken() ?? undefined
      );
    } catch {
      // Si falla el guardado no se le bloquea la entrada: el cuestionario es
      // para ayudarlo, no un peaje.
    } finally {
      setAbierto(false);
      // La página se recarga para que el resto de la plataforma tome la
      // respuesta: en qué prueba abrir el árbol y el configurador de ensayo.
      window.location.reload();
    }
  }

  if (!abierto) return null;

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
          {/* Sin barra de pasos: no hay pasos. Mostrar "1 de 1" solo anunciaría
              un trámite donde hay una pregunta. */}
          <h2 id="titulo-cuestionario" className="text-xl font-semibold tracking-tight">
            Hola {nombre}, ¿qué pruebas vas a rendir?
          </h2>
          <p className="mt-1 text-sm text-muted">
            Elige todas las que apliquen. Es lo único que necesitamos para abrir
            directo en lo tuyo.
          </p>

          <div className="mt-5 flex flex-col gap-2">
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
                    {p.nota && <span className="block text-xs text-muted">{p.nota}</span>}
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

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={pruebas.length === 0 || guardando}
              onClick={terminar}
              className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground disabled:opacity-40"
            >
              {guardando ? "Guardando…" : "Empezar"}
            </button>

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

          <p className="mt-4 text-xs text-muted">
            Puedes cambiar esto y contarnos el resto cuando quieras, en tu perfil.
          </p>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
