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

/**
 * Correo de contacto público. Vacío = no se muestra.
 *
 * Es el correo de servicio del proyecto, y NO uno del dominio: `1000paes.cl`
 * no tiene registros MX, así que cualquier `@1000paes.cl` rebota. Estuvo vacío
 * hasta ahora, y con él vacío el pie de página escondía el bloque entero: un
 * colegio que quería contratar no encontraba dónde escribir por ninguna parte.
 *
 * Si algún día el dominio recibe correo, se cambia acá y en las dos páginas
 * legales, que citan la dirección dentro del texto.
 */
export const EMAIL_CONTACTO = "1000paessoporte@gmail.com";

/** Solo las redes que ya tienen URL configurada. */
export function redesActivas(): RedSocial[] {
  return Object.entries(REDES_SOCIALES)
    .filter(([, url]) => url.trim().length > 0)
    .map(([nombre, url]) => ({ nombre, url }));
}
