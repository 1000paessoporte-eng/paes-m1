/**
 * URLs del catálogo público de carreras.
 *
 * Viven aparte del cálculo del ponderado porque son otra cosa: acá se decide
 * cómo se ve un enlace en Google y en un mensaje de WhatsApp. Una vez que una
 * URL está indexada no se cambia sin costo, así que estas funciones son el
 * único lugar donde se arma.
 */

/**
 * La URL pública de una carrera.
 *
 * Lleva el nombre legible por delante (para que el enlace diga de qué es) y el
 * código del DEMRE al final, que es lo único único: hay 1.855 carreras y los
 * nombres se repiten entre universidades. El código se lee de vuelta con
 * `codigoDesdeSlug`, así que la parte de texto puede cambiar sin romper URLs
 * ya indexadas.
 */
export function slugCarrera(c: {
  codigo: string;
  nombre: string;
  universidad: string;
}): string {
  return `${textoPlano(c.nombre)}-${textoPlano(c.universidad)}-${c.codigo}`;
}

/** El código del DEMRE que va al final del slug, o null si no lo trae. */
export function codigoDesdeSlug(slug: string): string | null {
  const codigo = slug.split("-").pop();
  return codigo && /^\d{1,10}$/.test(codigo) ? codigo : null;
}

/**
 * Texto apto para una URL: sin tildes, sin signos y con guiones.
 *
 * Mismo criterio que `normalizar()` en el backend (goals/service.py): nadie
 * escribe "INGENIERÍA" con tilde, y una URL con %C3%8D no la comparte nadie.
 */
function textoPlano(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * La URL del listado de una universidad.
 *
 * El índice se parte en dos niveles a propósito: 1.855 enlaces en una sola
 * página los rastrea mal cualquier buscador, y a una persona tampoco le sirven.
 * 47 universidades arriba, sus carreras adentro.
 */
export function slugUniversidad(universidad: string): string {
  return textoPlano(universidad);
}

/** Encuentra la universidad cuyo slug coincide, o null. */
export function universidadDesdeSlug(
  slug: string,
  universidades: readonly string[]
): string | null {
  return universidades.find((u) => slugUniversidad(u) === slug) ?? null;
}

/** Palabras que en español van en minúscula dentro de un título. */
const CONECTORES = new Set([
  "de", "del", "la", "las", "el", "los", "y", "e", "en", "para",
  "con", "a", "al", "o", "u", "por",
]);

/** "II", "IV": numerales romanos que no deben pasar a minúscula. */
const ROMANO = /^(?:i{1,3}|iv|vi{0,3}|ix|xi{0,2})$/;

/**
 * Un nombre en mayúsculas sostenidas, legible.
 *
 * El PDF del DEMRE trae las 1.855 carreras y 46 de las 47 universidades en
 * mayúsculas. Dejarlas así hace que cada título de Google y cada `h1` se lean
 * como un grito. Se arregla al mostrar y no en la base a propósito: el dato
 * tiene que seguir siendo el que publicó el DEMRE, letra por letra.
 *
 * Un texto que ya viene bien escrito se devuelve intacto, así que esto no
 * estropea las universidades que sí traen mayúsculas y minúsculas.
 */
export function nombreLegible(texto: string): string {
  if (texto !== texto.toUpperCase()) return texto;

  return texto
    .toLowerCase()
    .split(/(\s+|-)/)
    .map((parte, i) => {
      if (/^(\s+|-)$/.test(parte) || parte === "") return parte;
      if (ROMANO.test(parte)) return parte.toUpperCase();
      // El conector solo va en minúscula si no abre el título.
      if (i > 0 && CONECTORES.has(parte)) return parte;
      return parte[0].toUpperCase() + parte.slice(1);
    })
    .join("");
}

/**
 * El nombre de una carrera como se le muestra a una persona.
 *
 * El catálogo del DEMRE numera las variantes de una misma carrera dentro de
 * una universidad ("ARQUITECTURA (23)"), y ese número no significa nada para
 * quien lee: es un identificador interno de la oferta.
 */
export function nombreCarrera(nombre: string): string {
  return nombreLegible(nombre.replace(/\s*\(\d+\)\s*$/, "")).trim();
}
