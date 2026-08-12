"use client";

import Script from "next/script";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { loginWithGoogle } from "@/lib/api";
import { setClientAuth } from "@/lib/auth";

/**
 * Botón "Iniciar sesión con Google" (Google Identity Services).
 *
 * Google entrega un ID token firmado en el navegador; ese token se manda a la
 * API, que verifica la firma y que haya sido emitido para nuestro client ID
 * antes de crear la sesión. El navegador nunca decide quién es el usuario.
 *
 * Si `NEXT_PUBLIC_GOOGLE_CLIENT_ID` no está configurado, el componente no
 * renderiza nada: la web sigue funcionando con correo y contraseña.
 */

const CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";

interface GoogleCredentialResponse {
  credential?: string;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: GoogleCredentialResponse) => void;
          }) => void;
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
        };
      };
    };
  }
}

interface Props {
  /** A dónde ir tras iniciar sesión. */
  redirectTo?: string;
  onError?: (mensaje: string) => void;
}

export function GoogleButton({ redirectTo = "/examen", onError }: Props) {
  const router = useRouter();
  const contenedor = useRef<HTMLDivElement>(null);
  const [listo, setListo] = useState(false);
  const [entrando, setEntrando] = useState(false);

  const manejarCredencial = useCallback(
    async (response: GoogleCredentialResponse) => {
      if (!response.credential) return;
      setEntrando(true);
      try {
        const data = await loginWithGoogle(response.credential);
        setClientAuth(data.access_token, data.user);
        router.push(redirectTo);
        router.refresh();
      } catch {
        onError?.("No se pudo iniciar sesión con Google. Intenta de nuevo.");
      } finally {
        setEntrando(false);
      }
    },
    [router, redirectTo, onError]
  );

  useEffect(() => {
    if (!listo || !CLIENT_ID || !contenedor.current || !window.google) return;
    window.google.accounts.id.initialize({
      client_id: CLIENT_ID,
      callback: manejarCredencial,
    });
    window.google.accounts.id.renderButton(contenedor.current, {
      theme: "outline",
      size: "large",
      text: "continue_with",
      shape: "pill",
      locale: "es",
      width: 280,
    });
  }, [listo, manejarCredencial]);

  if (!CLIENT_ID) return null;

  return (
    <>
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => setListo(true)}
      />
      <div className="flex flex-col items-center gap-2">
        <div ref={contenedor} />
        {entrando && <p className="text-xs text-muted">Entrando…</p>}
      </div>
    </>
  );
}
