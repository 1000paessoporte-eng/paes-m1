"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { loginWithMicrosoft } from "@/lib/api";
import { setClientAuth } from "@/lib/auth";
import { tomarDestino, tomarVerifier, uriDeRetorno } from "@/lib/microsoft";

/**
 * Cierra el inicio de sesión con Microsoft.
 *
 * Toma el código de la URL y el secreto que esta pestaña guardó antes de
 * salir, y se los pasa a la API, que es quien canjea el token con Microsoft.
 * El navegador nunca decide quién es la persona.
 *
 * El código sirve una sola vez: si esto se ejecutara dos veces --y en
 * desarrollo React monta cada efecto dos veces a propósito-- el segundo canje
 * fallaría y la pantalla mostraría un error sobre un inicio de sesión que en
 * realidad funcionó. De ahí el `ref` que lo corre una sola vez.
 */
export function RetornoMicrosoft() {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const yaCorrio = useRef(false);

  useEffect(() => {
    if (yaCorrio.current) return;
    yaCorrio.current = true;

    // Microsoft avisa así cuando la persona cancela o el administrador del
    // colegio no autoriza la aplicación.
    const errorDeMicrosoft = params.get("error_description") ?? params.get("error");
    if (errorDeMicrosoft) {
      setError("Microsoft no completó el inicio de sesión.");
      return;
    }

    const code = params.get("code");
    const verifier = tomarVerifier();
    if (!code || !verifier) {
      // Pasa al recargar esta página o al abrir el enlace en otra pestaña:
      // el secreto vivía en la pestaña que empezó el intento.
      setError("El intento expiró. Vuelve a entrar con Microsoft.");
      return;
    }

    const destino = tomarDestino();
    loginWithMicrosoft(code, verifier, uriDeRetorno())
      .then((data) => {
        setClientAuth(data.access_token, data.user);
        router.replace(destino);
        router.refresh();
      })
      .catch(() => setError("No se pudo iniciar sesión con Microsoft."));
  }, [params, router]);

  return (
    <main className="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center gap-4 px-6 text-center">
      {error ? (
        <>
          <p className="text-sm text-danger">{error}</p>
          <Link
            href="/login"
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium transition-colors hover:bg-surface-hover"
          >
            Volver a intentar
          </Link>
        </>
      ) : (
        <p className="text-sm text-muted">Entrando con Microsoft…</p>
      )}
    </main>
  );
}
