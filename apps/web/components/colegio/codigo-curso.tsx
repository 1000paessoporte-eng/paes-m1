"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useState } from "react";

/**
 * El código del curso, tratado como lo que es: algo que se dicta en voz alta.
 *
 * Es la pieza central del panel del profesor y por eso está en grande, en
 * monoespaciado y con las letras separadas. Un curso de treinta personas lo
 * copia mirando la pizarra o la proyección, no haciendo copiar-y-pegar, así
 * que lo que importa es que se lea de lejos y que no se confunda ninguna
 * letra. El alfabeto ya excluye 0/O y 1/I/L por la misma razón.
 *
 * El botón de copiar existe igual, para el profesor que lo manda por el chat
 * del curso.
 */
export function CodigoCurso({ codigo }: { codigo: string }) {
  const quieto = useReducedMotion();
  const [copiado, setCopiado] = useState(false);

  async function copiar() {
    try {
      await navigator.clipboard.writeText(codigo);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      // Sin permiso de portapapeles no pasa nada: el código está a la vista.
    }
  }

  return (
    <div className="rounded-2xl border border-border bg-surface p-6">
      <p className="text-xs font-medium tracking-wide text-muted uppercase">
        Código del curso
      </p>

      <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-3">
        <p
          className="font-mono text-4xl font-semibold tracking-[0.28em] tabular-nums sm:text-5xl"
          // Se lee como una secuencia de caracteres y no como una palabra: sin
          // esto, un lector de pantalla dice "abc123" de corrido y el alumno
          // no puede escribirlo.
          aria-label={codigo.split("").join(" ")}
        >
          {codigo}
        </p>

        <button
          type="button"
          onClick={copiar}
          className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium hover:border-border-strong"
        >
          {copiado ? "Copiado" : "Copiar"}
        </button>
      </div>

      <motion.p
        key={copiado ? "copiado" : "quieto"}
        initial={quieto ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mt-3 text-sm text-muted"
      >
        Dáselo a tu curso. Cada alumno crea su cuenta, entra en{" "}
        <span className="text-foreground">Mi curso</span> y escribe estas seis
        letras.
      </motion.p>
    </div>
  );
}
