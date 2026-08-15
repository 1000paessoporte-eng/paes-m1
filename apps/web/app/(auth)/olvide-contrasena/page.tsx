"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { forgotPassword, getAuthConfig } from "@/lib/api";


export default function OlvideContrasenaPage() {
  const [email, setEmail] = useState("");
  // Si el servidor no tiene SMTP, el enlace se genera pero nunca sale: no se
  // puede prometer un correo que no se va a enviar.
  const [correoActivo, setCorreoActivo] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    getAuthConfig()
      .then((c) => setCorreoActivo(c.email_enabled))
      .catch(() => setCorreoActivo(null));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await forgotPassword(email);
    } finally {
      // Se muestra el mismo mensaje exista o no el correo: la API tampoco
      // lo revela, así que la web no puede confirmarlo por su cuenta.
      setLoading(false);
      setSent(true);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center px-6 py-20">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-6 shadow-xl shadow-foreground/5">
        <span
          className="flex h-9 w-9 items-center justify-center rounded-lg text-xs font-bold text-accent-foreground"
          style={{
            background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
          }}
        >
          1K
        </span>
        <h1 className="mt-4 text-lg font-semibold">Recupera tu contraseña</h1>
        <p className="mt-1 text-sm text-muted">
          {correoActivo === false
            ? "Todavía no podemos enviarte el link por correo."
            : "Te mandamos un link para crear una contraseña nueva."}
        </p>

        {correoActivo === false && (
          <p className="mt-4 rounded-lg border border-warning/40 bg-warning/10 px-3 py-3 text-left text-sm text-warning">
            <strong className="block">El envío de correos aún no está activo.</strong>
            Podemos generar el enlace, pero todavía no tenemos cómo mandártelo.
            Escríbenos a{" "}
            <a
              href="mailto:1000paessoporte@gmail.com"
              className="font-medium underline underline-offset-4"
            >
              1000paessoporte@gmail.com
            </a>{" "}
            y te ayudamos a recuperar tu cuenta.
          </p>
        )}

        {sent ? (
          <p className="mt-6 rounded-lg border border-border bg-background px-3 py-3 text-sm text-muted">
            {correoActivo === false ? (
              <>
                Registramos tu solicitud, pero el envío de correos todavía no
                está habilitado. Escríbenos a{" "}
                <a
                  href="mailto:1000paessoporte@gmail.com"
                  className="font-medium text-accent underline underline-offset-4"
                >
                  1000paessoporte@gmail.com
                </a>{" "}
                desde este mismo correo y recuperamos tu cuenta a mano.
              </>
            ) : (
              <>
                Si <span className="text-foreground">{email}</span> tiene una
                cuenta en 1000paes, te llegará un correo con las instrucciones.
                El link vence en 30 minutos.
              </>
            )}
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3">
            <label className="flex flex-col gap-1.5 text-left">
              <span className="text-xs font-medium text-muted">Correo</span>
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@correo.com"
                className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted/60"
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="btn-glow mt-2 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Enviando…" : "Enviar link"}
            </button>
          </form>
        )}

        <p className="mt-4 text-center text-xs text-muted">
          <Link href="/login" className="font-medium text-accent hover:underline">
            Volver a iniciar sesión
          </Link>
        </p>
      </div>
    </main>
  );
}
