"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { crearColegio, unirseAColegio, ApiError } from "@/lib/api";
import { actualizarUsuarioLocal, getClientToken } from "@/lib/auth";

/**
 * La entrada al plan Colegios: sumarse a un curso, o abrir uno.
 *
 * El orden importa. Sumarse va primero y ocupa el espacio grande porque por
 * cada profesor que crea un curso hay treinta alumnos que solo tienen que
 * escribir seis letras. Crear un curso es la acción de una persona por
 * establecimiento, y vive abajo, plegada.
 */

const LARGO_CODIGO = 6;

export function SinCurso() {
  const router = useRouter();
  const quieto = useReducedMotion();
  const [codigo, setCodigo] = useState("");
  const [nombre, setNombre] = useState("");
  const [abriendo, setAbriendo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const completo = codigo.length === LARGO_CODIGO;

  async function entrar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await unirseAColegio(codigo, getClientToken() ?? undefined);
      actualizarUsuarioLocal({ tiene_colegio: true });
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 404
          ? "Ese código no corresponde a ningún curso. Revísalo con tu profesor."
          : "No pudimos sumarte al curso. Intenta de nuevo."
      );
      setEnviando(false);
    }
  }

  async function crear(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await crearColegio(nombre, getClientToken() ?? undefined);
      actualizarUsuarioLocal({ tiene_colegio: true });
      router.refresh();
    } catch {
      setError("No pudimos crear el curso. Intenta de nuevo.");
      setEnviando(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="text-2xl font-semibold">Mi curso</h1>
      <p className="mt-1 text-sm text-muted">
        Si tu colegio usa 1000paes, tu profesor tiene un código de seis letras.
      </p>

      <form
        onSubmit={entrar}
        className="mt-6 rounded-2xl border border-border bg-surface p-6"
      >
        <label htmlFor="codigo-curso" className="text-sm font-medium">
          Código del curso
        </label>

        {/* El campo imita cómo se dicta el código: letra por letra, en
            mayúsculas y con espacio entre caracteres. Escrito en minúscula
            apretada se parecería a una contraseña, que es justo lo que no es
            --el profesor lo escribe en la pizarra. */}
        <input
          id="codigo-curso"
          value={codigo}
          onChange={(e) =>
            setCodigo(
              e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, LARGO_CODIGO)
            )
          }
          autoComplete="off"
          autoCapitalize="characters"
          spellCheck={false}
          placeholder="ABC123"
          aria-describedby="ayuda-codigo"
          className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-4 text-center font-mono text-3xl tracking-[0.4em] uppercase placeholder:text-muted/40 focus:border-accent focus:outline-none"
        />
        <p id="ayuda-codigo" className="mt-2 text-xs text-muted">
          {codigo.length}/{LARGO_CODIGO} caracteres
        </p>

        <button
          type="submit"
          disabled={!completo || enviando}
          className="btn-glow mt-4 w-full rounded-lg px-4 py-2.5 text-sm font-medium text-accent-foreground disabled:cursor-not-allowed disabled:opacity-40"
        >
          {enviando ? "Entrando…" : "Entrar al curso"}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-3 text-sm text-danger">
          {error}
        </p>
      )}

      <div className="mt-8 border-t border-border pt-6">
        {!abriendo ? (
          <button
            type="button"
            onClick={() => setAbriendo(true)}
            className="text-sm text-muted underline decoration-border underline-offset-4 hover:text-foreground"
          >
            Soy profesor y quiero abrir un curso
          </button>
        ) : (
          <motion.form
            onSubmit={crear}
            initial={quieto ? false : { opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            <label htmlFor="nombre-curso" className="text-sm font-medium">
              Nombre del curso
            </label>
            <p className="mt-1 text-xs text-muted">
              Como lo reconozcan tus alumnos. Por ejemplo, “4° B — Liceo Bicentenario”.
            </p>
            <input
              id="nombre-curso"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              maxLength={160}
              className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:border-accent focus:outline-none"
            />
            <button
              type="submit"
              disabled={nombre.trim().length < 2 || enviando}
              className="mt-3 w-full rounded-lg border border-border px-4 py-2.5 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-40"
            >
              {enviando ? "Creando…" : "Crear el curso"}
            </button>
            <p className="mt-3 text-xs text-muted">
              Crear el curso es gratis y te da el panel con el avance de quienes
              entren. El plan con acceso Pro para todo el curso se contrata
              aparte, escribiéndonos.
            </p>
          </motion.form>
        )}
      </div>
    </div>
  );
}
