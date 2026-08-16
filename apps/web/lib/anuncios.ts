/**
 * Qué anuncio mostrar hoy, y solo uno.
 *
 * El problema que resuelve: hay dos avisos que compiten por la misma pantalla
 * —el premio de $500.000 y el plan Pro— y ambos deben aparecer a diario. Si
 * cada uno decidiera por su cuenta, quien entra todos los días vería DOS
 * ventanas apiladas cada mañana, las cerraría sin leer y la segunda quedaría
 * asociada a la molestia de la primera. Un anuncio ignorado no es neutro:
 * enseña a cerrar sin mirar.
 *
 * Por eso la elección es central y excluyente: máximo uno por día, alternando,
 * de modo que a lo largo de una semana la persona vea ambos mensajes sin
 * recibir nunca dos de golpe.
 *
 * La marca es la FECHA, no un booleano: guardar "ya lo vio" obliga a limpiar
 * el registro cada noche desde algún lado. Guardar el día en que se mostró
 * hace que la comparación con hoy resuelva sola el vencimiento.
 */

export type Anuncio = "premio" | "planes";

const CLAVE = "anuncio-diario";

/** Día local en formato YYYY-MM-DD. Local y no UTC: para alguien en Chile el
 *  día cambia a medianoche de acá, no a las 21:00. */
function hoy(): string {
  const d = new Date();
  const mes = String(d.getMonth() + 1).padStart(2, "0");
  const dia = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mes}-${dia}`;
}

interface Registro {
  fecha: string;
  ultimo: Anuncio;
}

function leer(): Registro | null {
  try {
    const crudo = localStorage.getItem(CLAVE);
    if (!crudo) return null;
    const r = JSON.parse(crudo) as Registro;
    return r?.fecha ? r : null;
  } catch {
    // localStorage puede fallar en modo privado o con almacenamiento lleno. Un
    // anuncio no vale romper el panel: si no se puede leer, no se muestra.
    return null;
  }
}

/**
 * Cuál corresponde hoy, o `null` si ya se mostró uno.
 *
 * `disponibles` permite omitir el de planes cuando la persona ya es Pro: no
 * tiene sentido ofrecerle lo que ya compró.
 */
export function anuncioDeHoy(disponibles: Anuncio[]): Anuncio | null {
  if (disponibles.length === 0) return null;

  const registro = leer();
  if (registro?.fecha === hoy()) return null;

  // Alterna respecto del último mostrado. Si el que tocaría no está
  // disponible, cae en el otro en vez de saltarse el día.
  const anterior = registro?.ultimo;
  const preferido: Anuncio = anterior === "premio" ? "planes" : "premio";
  return disponibles.includes(preferido) ? preferido : disponibles[0];
}

/** Marca que hoy ya se mostró este anuncio. */
export function marcarMostrado(anuncio: Anuncio): void {
  try {
    const registro: Registro = { fecha: hoy(), ultimo: anuncio };
    localStorage.setItem(CLAVE, JSON.stringify(registro));
  } catch {
    // Si no se puede escribir, el anuncio volverá a salir. Molesto pero
    // inofensivo, y preferible a que la pantalla falle.
  }
}
