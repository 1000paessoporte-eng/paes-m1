"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError, cancelarSuscripcion, eliminarCuenta } from "@/lib/api";
import { clearClientAuth, getClientToken } from "@/lib/auth";

/**
 * Cancelar la suscripción y borrar la cuenta.
 *
 * Las dos existían solo como "escríbenos a hola@1000paes.cl". Pedir un correo
 * para dejar de pagar --cuando pagar son dos clics-- es fricción puesta a
 * propósito, y pedirlo para ejercer un derecho sobre los propios datos es
 * ponerle un trámite a lo que debería ser un botón. Este producto guarda datos
 * de estudio de menores de edad.
 *
 * Van juntas y al final de la página, con el borde de aviso: son las dos
 * acciones que nadie debería tocar por accidente. Borrar pide además escribir
 * la contraseña, porque es irreversible.
 */
export function ZonaPeligro({
  tienePlanActivo,
  usaGoogle,
}: {
  tienePlanActivo: boolean;
  /** Las cuentas de Google no tienen contraseña que confirmar. */
  usaGoogle: boolean;
}) {
  const router = useRouter();
  const [confirmando, setConfirmando] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);
  const [cancelado, setCancelado] = useState(false);

  async function cancelar() {
    setOcupado(true);
    setError(null);
    try {
      await cancelarSuscripcion(getClientToken() ?? undefined);
      setCancelado(true);
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "No se pudo cancelar. Inténtalo de nuevo."
      );
    }
    setOcupado(false);
  }

  async function borrar() {
    setOcupado(true);
    setError(null);
    try {
      await eliminarCuenta(usaGoogle ? null : password, getClientToken() ?? undefined);
      clearClientAuth();
      // Reemplaza en vez de empujar: volver atrás a una cuenta borrada no
      // lleva a ninguna parte.
      window.location.replace("/");
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? "La contraseña no es correcta."
          : "No se pudo borrar la cuenta. Inténtalo de nuevo."
      );
      setOcupado(false);
    }
  }

  return (
    <section className="mt-10 rounded-xl border border-danger/30 bg-danger/5 p-6">
      <h2 className="font-semibold">Tu cuenta</h2>

      {tienePlanActivo && (
        <div className="mt-4 border-b border-danger/20 pb-4">
          <p className="text-sm text-muted">
            {cancelado
              ? "Tu suscripción no se renovará. Conservas Pro hasta la fecha de término."
              : "Puedes cancelar la renovación cuando quieras. No pierdes lo que ya pagaste: conservas Pro hasta la fecha de término."}
          </p>
          {!cancelado && (
            <button
              type="button"
              onClick={cancelar}
              disabled={ocupado}
              className="mt-3 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium hover:bg-surface-hover disabled:opacity-50"
            >
              Cancelar la renovación
            </button>
          )}
        </div>
      )}

      <div className="mt-4">
        <p className="text-sm text-muted">
          Borrar tu cuenta elimina tus ensayos, tu progreso y tus datos.{" "}
          <strong className="text-foreground">No se puede deshacer.</strong>
        </p>

        {!confirmando ? (
          <button
            type="button"
            onClick={() => setConfirmando(true)}
            className="mt-3 rounded-lg border border-danger/40 px-4 py-2 text-sm font-medium text-danger hover:bg-danger/10"
          >
            Borrar mi cuenta
          </button>
        ) : (
          <div className="mt-3 flex flex-col gap-2">
            {!usaGoogle && (
              <label htmlFor="pass-borrar" className="flex flex-col gap-1 text-sm">
                <span className="text-muted">Escribe tu contraseña para confirmar</span>
                <input
                  id="pass-borrar"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="rounded-lg border border-border bg-background px-3 py-2 focus:border-danger focus:outline-none"
                />
              </label>
            )}
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={borrar}
                disabled={ocupado || (!usaGoogle && password.length === 0)}
                className="rounded-lg bg-danger px-4 py-2 text-sm font-semibold text-on-fill disabled:opacity-50"
              >
                {ocupado ? "Borrando…" : "Sí, borrar mi cuenta"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setConfirmando(false);
                  setPassword("");
                  setError(null);
                }}
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-surface-hover"
              >
                Mejor no
              </button>
            </div>
          </div>
        )}
      </div>

      {error && <p className="mt-3 text-sm text-danger">{error}</p>}
    </section>
  );
}
