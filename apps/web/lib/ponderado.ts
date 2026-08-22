/**
 * El puntaje ponderado, calculado en el navegador.
 *
 * En Chile nadie postula con "el puntaje de matemática": se postula con el
 * PONDERADO, que combina NEM, ranking y pruebas con los pesos que fija cada
 * carrera. Dos personas con los mismos puntajes entran a carreras distintas.
 *
 * Esta lógica vive acá y no dentro del componente porque el componente lleva
 * `use client` y esto tiene que poder importarse (y probarse) sin arrastrar
 * React. Es la misma fórmula que aplica el backend en `modules/goals/service.py`
 * para el alumno con sesión; acá opera sobre las ponderaciones crudas de la
 * carrera, que es lo único que tiene una visita anónima.
 */

/** Los factores que pondera una carrera, en porcentaje. Suman 100. */
export type Ponderaciones = {
  // Opcionales además de nullable porque así los declara el schema generado
  // desde el OpenAPI: un factor que la carrera no pondera puede llegar como
  // null o no llegar. Para el cálculo las dos cosas significan lo mismo.
  nem?: number | null;
  ranking?: number | null;
  lectora?: number | null;
  m1?: number | null;
  historia?: number | null;
  ciencias?: number | null;
  m2?: number | null;
  prueba_especial?: number | null;
  /** Cuando es true, historia y ciencias pesan igual pero solo cuenta la mejor. */
  electivo_alternativo: boolean;
};

/** Lo que la persona declara saber o estimar. Cualquiera puede faltar. */
export type Puntajes = {
  nem?: number | null;
  ranking?: number | null;
  lectora?: number | null;
  m1?: number | null;
  historia?: number | null;
  ciencias?: number | null;
  m2?: number | null;
  prueba_especial?: number | null;
};

export type Factor = keyof Puntajes;

/** Cómo se llama cada factor en pantalla. */
export const ETIQUETAS: Record<Factor, string> = {
  nem: "NEM",
  ranking: "Ranking",
  lectora: "Competencia Lectora",
  m1: "Matemática M1",
  m2: "Matemática M2",
  historia: "Historia y Cs. Sociales",
  ciencias: "Ciencias",
  prueba_especial: "Prueba especial",
};

/**
 * El color de cada factor.
 *
 * Las cinco pruebas PAES llevan SU color, el mismo del árbol, del ensayo y del
 * titular de la portada. NEM, ranking y la prueba especial van en grafito, y
 * esa diferencia no es estética: separa lo que el alumno RINDE de lo que trae
 * de su colegio, que es la distinción más importante de esta pantalla y no se
 * veía por ninguna parte.
 */
export const COLOR_FACTOR: Record<Factor, string> = {
  nem: "var(--accent-2)",
  ranking: "var(--accent-2)",
  lectora: "var(--prueba-lectora)",
  m1: "var(--prueba-m1)",
  m2: "var(--prueba-m2)",
  historia: "var(--prueba-historia)",
  ciencias: "var(--prueba-ciencias)",
  prueba_especial: "var(--accent-2)",
};

/** Si el factor es una de las cinco pruebas PAES. */
export function esPruebaPaes(factor: Factor): boolean {
  return ["lectora", "m1", "m2", "historia", "ciencias"].includes(factor);
}

/** El orden en que se muestran: NEM y ranking primero, como en el DEMRE. */
const ORDEN: Factor[] = [
  "nem",
  "ranking",
  "lectora",
  "m1",
  "m2",
  "historia",
  "ciencias",
  "prueba_especial",
];

/** Un factor que esta carrera efectivamente pondera. */
export type FactorPonderado = { factor: Factor; etiqueta: string; peso: number };

/**
 * Los factores con peso mayor a cero, en orden de presentación.
 *
 * Una carrera pondera 4 o 5 factores de los 8 posibles; mostrar los otros con
 * un 0% sería ruido que compite con el dato que la persona vino a buscar.
 */
export function factoresDe(p: Ponderaciones): FactorPonderado[] {
  return ORDEN.filter((f) => {
    const peso = p[f as keyof Ponderaciones];
    return typeof peso === "number" && peso > 0;
  }).map((factor) => ({
    factor,
    etiqueta: ETIQUETAS[factor],
    peso: p[factor as keyof Ponderaciones] as number,
  }));
}

/**
 * El ponderado, o null si falta algún puntaje que la carrera exige.
 *
 * Devolver null en vez de asumir 0 es deliberado: un ponderado calculado con
 * un hueco es un número plausible y falso, y acá el número decide si alguien
 * cree que puede postular.
 *
 * Con `electivo_alternativo`, historia y ciencias traen el mismo peso pero
 * solo entra la mejor de las dos, así que basta con haber dado una.
 */
export function calcularPonderado(p: Ponderaciones, puntajes: Puntajes): number | null {
  let total = 0;

  for (const { factor, peso } of factoresDe(p)) {
    if (p.electivo_alternativo && (factor === "historia" || factor === "ciencias")) {
      continue;
    }
    const puntaje = puntajes[factor];
    if (puntaje == null) return null;
    total += (peso * puntaje) / 100;
  }

  if (p.electivo_alternativo) {
    const peso = p.historia ?? p.ciencias;
    if (peso != null && peso > 0) {
      const rendidas = [puntajes.historia, puntajes.ciencias].filter(
        (x): x is number => x != null
      );
      // Solo cuenta la mejor: dar las dos pruebas no suma, elige.
      if (rendidas.length === 0) return null;
      total += (peso * Math.max(...rendidas)) / 100;
    }
  }

  return Math.round(total * 10) / 10;
}
