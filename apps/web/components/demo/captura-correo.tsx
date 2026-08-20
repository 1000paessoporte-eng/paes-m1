"use client";

import { useState } from "react";
import { dejarCorreo, type LeadSource } from "@/lib/api";

type Estado = "inicial" | "enviando" | "listo" | "error";

/**
 * Deja el correo sin crear cuenta.
 *
 * Existe por el agujero más caro del embudo: quien termina la demo y no se
 * registra se va sin dejar rastro, y no hay forma de volver a hablarle. Crear
 * cuenta son varios pasos; esto es uno.
 *
 * Promete poco a propósito —avisar cuando haya material nuevo— porque es lo
 * único que hoy se puede cumplir. Prometer un informe personalizado que nadie
 * va a mandar es la forma más rápida de quemar una lista de correos.
 */
export function CapturaCorreo({ source }: { source: LeadSource }) {
  const [email, setEmail] = useState("");
  const [estado, setEstado] = useState<Estado>("inicial");

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || estado === "enviando") return;
    setEstado("enviando");
    try {
      await dejarCorreo(email.trim(), source);
      setEstado("listo");
    } catch {
      setEstado("error");
    }
  }

  if (estado === "listo") {
    return (
      <p className="rounded-lg border border-success/40 bg-success/5 px-4 py-3 text-sm text-success">
        Listo. Te escribimos cuando haya preguntas o funciones nuevas.
      </p>
    );
  }

  return (
    <form onSubmit={enviar} className="flex flex-col gap-2">
      <label htmlFor="correo-demo" className="text-sm text-muted">
        ¿Prefieres no crear cuenta todavía? Déjanos tu correo y te avisamos
        cuando sumemos preguntas y funciones nuevas.
      </label>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          id="correo-demo"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="tu@correo.cl"
          autoComplete="email"
          className="flex-1 rounded-lg border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted focus:border-accent focus:outline-none"
        />
        <button
          type="submit"
          disabled={estado === "enviando"}
          className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover disabled:opacity-50"
        >
          {estado === "enviando" ? "Enviando…" : "Avísenme"}
        </button>
      </div>
      {estado === "error" && (
        <p className="text-xs text-danger">
          No pudimos guardarlo. Revisa el correo e inténtalo de nuevo.
        </p>
      )}
      <p className="text-xs text-muted">
        Solo para avisos de 1000paes. Puedes pedir que lo borremos cuando
        quieras.
      </p>
    </form>
  );
}
