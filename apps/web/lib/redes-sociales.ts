/**
 * Redes sociales de 1000paes.
 *
 * Las cuentas todavía no están creadas. Cuando existan, basta con pegar la URL
 * acá: el footer renderiza automáticamente solo las que tengan valor, así que
 * no queda ningún link roto apuntando a una cuenta inexistente.
 *
 * Ejemplo cuando esté lista:
 *   instagram: "https://instagram.com/1000paes",
 */
export interface RedSocial {
  nombre: string;
  url: string;
}

export const REDES_SOCIALES: Record<string, string> = {
  instagram: "",
  tiktok: "",
  facebook: "",
  youtube: "",
};

/** Correo de contacto público. Vacío = no se muestra. */
export const EMAIL_CONTACTO = "";

/** Solo las redes que ya tienen URL configurada. */
export function redesActivas(): RedSocial[] {
  return Object.entries(REDES_SOCIALES)
    .filter(([, url]) => url.trim().length > 0)
    .map(([nombre, url]) => ({ nombre, url }));
}
