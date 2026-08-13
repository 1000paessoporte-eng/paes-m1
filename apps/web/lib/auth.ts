// El token se guarda en una cookie NO httpOnly (no en localStorage) para
// que tanto los Server Components (leyéndola via next/headers en cada
// page.tsx) como los Client Components (leyéndola aquí via document.cookie)
// puedan adjuntarla como Authorization Bearer en cada llamada a la API.
// No depende de que el navegador la envíe automáticamente cross-origin —
// solo se usa como almacenamiento legible por JS en el dominio del front.

export const TOKEN_COOKIE = "paes_token";
export const USER_COOKIE = "paes_user";

// Evento propio para que componentes como SiteHeader (que solo re-leen la
// cookie al cambiar de ruta) se enteren de un login/logout/cambio de nombre
// ocurrido en la misma página sin necesitar navegar.
const AUTH_CHANGE_EVENT = "paes:auth-changed";

function notifyAuthChanged() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
  }
}

export function onClientAuthChange(callback: () => void): () => void {
  if (typeof window === "undefined") return () => {};
  window.addEventListener(AUTH_CHANGE_EVENT, callback);
  return () => window.removeEventListener(AUTH_CHANGE_EVENT, callback);
}

const MAX_AGE_SECONDS = 60 * 60 * 24 * 14; // 14 días, igual que la expiración del JWT

export interface AuthUser {
  id: number;
  email: string;
  name: string;
  /** Solo decide si se muestra el enlace al panel. La API vuelve a comprobarlo
   *  en cada llamada, así que editar la cookie no da acceso a nada. */
  is_admin?: boolean;
}

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function writeCookie(name: string, value: string) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${MAX_AGE_SECONDS}; samesite=lax`;
}

function clearCookie(name: string) {
  document.cookie = `${name}=; path=/; max-age=0; samesite=lax`;
}

export function setClientAuth(token: string, user: AuthUser) {
  writeCookie(TOKEN_COOKIE, token);
  writeCookie(USER_COOKIE, JSON.stringify(user));
  notifyAuthChanged();
}

export function clearClientAuth() {
  clearCookie(TOKEN_COOKIE);
  clearCookie(USER_COOKIE);
  notifyAuthChanged();
}

export function getClientToken(): string | null {
  return readCookie(TOKEN_COOKIE);
}

/**
 * Ruta de entrada llevando de vuelta a donde estaba la persona. Se usa cuando
 * la sesión caduca a mitad de uso: sin esto, quien iba en /historial terminaba
 * en /examen tras volver a entrar.
 */
export function loginHref(next?: string | null): string {
  if (!next) return "/login";
  return `/login?next=${encodeURIComponent(next)}`;
}

export function getClientUser(): AuthUser | null {
  const raw = readCookie(USER_COOKIE);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}
