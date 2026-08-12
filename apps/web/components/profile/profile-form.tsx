"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError, updateMe } from "@/lib/api";
import { getClientToken, setClientAuth } from "@/lib/auth";

type Msg = { type: "ok" | "error"; text: string };

export function ProfileForm({
  initialName,
  email,
}: {
  initialName: string;
  email: string;
}) {
  const router = useRouter();
  const [name, setName] = useState(initialName);
  const [savingName, setSavingName] = useState(false);
  const [nameMsg, setNameMsg] = useState<Msg | null>(null);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<Msg | null>(null);

  async function handleNameSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSavingName(true);
    setNameMsg(null);
    try {
      const token = getClientToken() ?? undefined;
      const updated = await updateMe({ name }, token);
      if (token) {
        setClientAuth(token, { id: updated.id, email: updated.email, name: updated.name });
      }
      setNameMsg({ type: "ok", text: "Nombre actualizado." });
      router.refresh();
    } catch {
      setNameMsg({ type: "error", text: "No se pudo actualizar el nombre." });
    } finally {
      setSavingName(false);
    }
  }

  async function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSavingPassword(true);
    setPasswordMsg(null);
    try {
      await updateMe(
        { current_password: currentPassword, new_password: newPassword },
        getClientToken() ?? undefined
      );
      setPasswordMsg({ type: "ok", text: "Contraseña actualizada." });
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordMsg({
        type: "error",
        text:
          err instanceof ApiError && err.status === 401
            ? "La contraseña actual es incorrecta."
            : "No se pudo actualizar la contraseña.",
      });
    } finally {
      setSavingPassword(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="rounded-xl border border-border bg-surface p-5">
        <h2 className="text-sm font-medium text-foreground">Datos de la cuenta</h2>
        <form onSubmit={handleNameSubmit} className="mt-4 flex flex-col gap-3">
          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium text-muted">Correo</span>
            <input
              type="email"
              value={email}
              disabled
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-muted disabled:cursor-not-allowed"
            />
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium text-muted">Nombre</span>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground"
            />
          </label>
          {nameMsg && (
            <p
              className={
                nameMsg.type === "ok"
                  ? "text-xs text-success"
                  : "rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-xs text-danger"
              }
            >
              {nameMsg.text}
            </p>
          )}
          <button
            type="submit"
            disabled={savingName || name === initialName}
            className="btn-glow mt-1 self-start rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground disabled:cursor-not-allowed disabled:opacity-60"
          >
            {savingName ? "Guardando…" : "Guardar nombre"}
          </button>
        </form>
      </div>

      <div className="rounded-xl border border-border bg-surface p-5">
        <h2 className="text-sm font-medium text-foreground">Cambiar contraseña</h2>
        <form onSubmit={handlePasswordSubmit} className="mt-4 flex flex-col gap-3">
          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium text-muted">Contraseña actual</span>
            <input
              type="password"
              required
              autoComplete="current-password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground"
            />
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium text-muted">Nueva contraseña</span>
            <input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Mínimo 8 caracteres"
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground"
            />
          </label>
          {passwordMsg && (
            <p
              className={
                passwordMsg.type === "ok"
                  ? "text-xs text-success"
                  : "rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-xs text-danger"
              }
            >
              {passwordMsg.text}
            </p>
          )}
          <button
            type="submit"
            disabled={savingPassword}
            className="mt-1 self-start rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {savingPassword ? "Guardando…" : "Cambiar contraseña"}
          </button>
        </form>
      </div>
    </div>
  );
}
