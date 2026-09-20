/**
 * Inicio de sesión con Microsoft: la mitad que corre en el navegador.
 *
 * Es Authorization Code + PKCE, el flujo que Microsoft pide para aplicaciones
 * de página única. En corto:
 *
 * 1. Acá se inventa un secreto al azar (`code_verifier`), se guarda en esta
 *    pestaña y se manda a Microsoft solo su hash (`code_challenge`).
 * 2. Microsoft devuelve a la persona con un código de un solo uso.
 * 3. La API canjea ese código con Microsoft usando el secreto original.
 *
 * Quien intercepte el código no puede usarlo: le falta el secreto, que nunca
 * viajó. Por eso esta aplicación no necesita --ni tiene-- un client secret.
 *
 * El secreto vive en `sessionStorage` y no en `localStorage` a propósito: es
 * de esta pestaña y de este intento, y se borra apenas se usa.
 */

const CLIENT_ID = process.env.NEXT_PUBLIC_MICROSOFT_CLIENT_ID ?? "";

/** `common`: acepta la cuenta del colegio y también la personal. */
const AUTORIZAR = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize";

const CLAVE_VERIFIER = "ms_code_verifier";
const CLAVE_DESTINO = "ms_redirect_to";

export const microsoftDisponible = Boolean(CLIENT_ID);

/** La URI de retorno. Microsoft la compara carácter a carácter con la que
 *  está registrada en Entra, así que se arma de una sola forma en todo el
 *  código y nunca a mano. */
export function uriDeRetorno(): string {
  return `${window.location.origin}/entrar/microsoft`;
}

function aleatorio(largo = 64): string {
  const bytes = new Uint8Array(largo);
  crypto.getRandomValues(bytes);
  // base64url sobre los bytes: sin +, / ni =, que en una URL hay que escapar.
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

async function hashS256(texto: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(texto));
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

/** Manda a la persona a Microsoft. No vuelve: la pestaña navega. */
export async function irAMicrosoft(redirectTo: string): Promise<void> {
  const verifier = aleatorio();
  sessionStorage.setItem(CLAVE_VERIFIER, verifier);
  sessionStorage.setItem(CLAVE_DESTINO, redirectTo);

  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    response_type: "code",
    redirect_uri: uriDeRetorno(),
    response_mode: "query",
    scope: "openid profile email",
    code_challenge: await hashS256(verifier),
    code_challenge_method: "S256",
  });
  window.location.assign(`${AUTORIZAR}?${params}`);
}

/** El secreto de este intento, que se consume al leerlo. */
export function tomarVerifier(): string | null {
  const verifier = sessionStorage.getItem(CLAVE_VERIFIER);
  sessionStorage.removeItem(CLAVE_VERIFIER);
  return verifier;
}

export function tomarDestino(): string {
  const destino = sessionStorage.getItem(CLAVE_DESTINO);
  sessionStorage.removeItem(CLAVE_DESTINO);
  // Solo rutas de este sitio: si esto aceptara una URL completa, bastaría
  // ensuciar sessionStorage para mandar a alguien recién autenticado a otro
  // dominio con aspecto de seguir dentro del sitio.
  return destino && destino.startsWith("/") ? destino : "/panel";
}
