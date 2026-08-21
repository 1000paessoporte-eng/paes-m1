import type { ExamAttemptSummary, Subject } from "@/lib/api";

/**
 * Cuánto ha avanzado el alumno desde que llegó, y qué hitos lleva.
 *
 * Vive fuera de los componentes porque es la parte que se puede equivocar: si
 * este archivo miente, la pantalla motiva con un número falso, que es peor que
 * no motivar. Son funciones puras sobre lo que ya devuelve la API.
 */

/** Cuántos ensayos recientes promedia el "ahora". */
const VENTANA_RECIENTE = 3;

export interface AvancePrueba {
  subject: Subject;
  /** Puntaje del PRIMER ensayo que rindió de esta prueba. */
  primero: number;
  /** Promedio de sus ensayos recientes, sin contar el primero. */
  ahora: number;
  /** `ahora - primero`. Puede ser negativo: no se maquilla. */
  delta: number;
  mejor: number;
  ensayos: number;
}

/**
 * El avance de cada prueba, de la que más avanzó a la que menos.
 *
 * SEPARADO POR PRUEBA a propósito. Un 700 de Lectora y un 500 de M2 no se
 * promedian: son escalas distintas sobre temarios distintos, y mezclarlas
 * inventa un progreso que no ocurrió --basta rendir una prueba más fácil para
 * que el número suba--.
 *
 * Necesita dos ensayos de la MISMA prueba: con uno solo no hay desde dónde
 * medir, y un "avance" de cero sería tan falso como uno inventado.
 */
export function avancePorPrueba(intentos: ExamAttemptSummary[]): AvancePrueba[] {
  const porPrueba = new Map<Subject, ExamAttemptSummary[]>();
  for (const intento of intentos) {
    if (intento.estimated_score == null) continue;
    const lista = porPrueba.get(intento.subject) ?? [];
    lista.push(intento);
    porPrueba.set(intento.subject, lista);
  }

  const avances: AvancePrueba[] = [];
  for (const [subject, lista] of porPrueba) {
    if (lista.length < 2) continue;

    // La API entrega el más reciente primero; acá se necesita el orden en que
    // los vivió el alumno.
    const cronologico = [...lista].sort(
      (a, b) => new Date(a.started_at).getTime() - new Date(b.started_at).getTime()
    );
    const puntajes = cronologico.map((i) => i.estimated_score as number);

    const primero = puntajes[0];
    // El primero se EXCLUYE del "ahora": compararlo consigo mismo diluye el
    // avance justo cuando recién hay dos ensayos, que es cuando más importa
    // que se note.
    const resto = puntajes.slice(1);
    const recientes = resto.slice(-VENTANA_RECIENTE);
    const ahora = Math.round(recientes.reduce((a, b) => a + b, 0) / recientes.length);

    avances.push({
      subject,
      primero,
      ahora,
      delta: ahora - primero,
      mejor: Math.max(...puntajes),
      ensayos: puntajes.length,
    });
  }

  return avances.sort((a, b) => b.delta - a.delta);
}

export interface Hito {
  /** Qué logró, en pasado y en segunda persona. */
  titulo: string;
  /** El umbral que había que cruzar. */
  meta: number;
  /** Dónde va hoy. Si `>= meta`, está conseguido. */
  actual: number;
  /** La unidad en plural, para escribir "faltan 3 ensayos". */
  unidad: string;
  /** La misma en singular. Sin esto salía "te falta 1 ensayos". */
  unidadSingular: string;
}

interface DatosHitos {
  ensayos: number;
  preguntasRespondidas: number;
  mejorPuntaje: number;
  mejorRacha: number;
}

/** Los peldaños de cada serie. Cortos al principio: el primero se cruza el día uno. */
const SERIES: {
  unidad: string;
  unidadSingular: string;
  titulo: (n: number) => string;
  metas: number[];
  clave: keyof DatosHitos;
}[] =
  [
    {
      clave: "ensayos",
      unidad: "ensayos",
      unidadSingular: "ensayo",
      titulo: (n) => (n === 1 ? "Rendiste tu primer ensayo" : `Rendiste ${n} ensayos`),
      metas: [1, 3, 5, 10, 25, 50],
    },
    {
      clave: "preguntasRespondidas",
      unidad: "preguntas",
      unidadSingular: "pregunta",
      titulo: (n) => `Respondiste ${n.toLocaleString("es-CL")} preguntas`,
      metas: [50, 250, 1000, 2500],
    },
    {
      clave: "mejorPuntaje",
      unidad: "puntos",
      unidadSingular: "punto",
      titulo: (n) => `Pasaste los ${n} puntos`,
      metas: [450, 550, 650, 750, 850],
    },
    {
      clave: "mejorRacha",
      unidad: "días",
      unidadSingular: "día",
      titulo: (n) => `${n} días seguidos rindiendo`,
      metas: [2, 5, 10, 20],
    },
  ];

/**
 * Los hitos conseguidos y el siguiente de cada serie.
 *
 * Un hito es siempre un hecho verificable --ensayos rendidos, preguntas
 * respondidas--, nunca un elogio genérico. "Vas muy bien" no lo cree nadie;
 * "respondiste 250 preguntas" es cierto y se puede contar.
 *
 * Devuelve también el PRÓXIMO de cada serie, con lo que falta, porque un muro
 * de medallas ya ganadas dice dónde estuvo y no hacia dónde ir.
 */
export function hitos(datos: DatosHitos): { logrados: Hito[]; siguientes: Hito[] } {
  const logrados: Hito[] = [];
  const siguientes: Hito[] = [];

  for (const serie of SERIES) {
    const actual = datos[serie.clave];
    const conseguidas = serie.metas.filter((m) => actual >= m);
    const pendiente = serie.metas.find((m) => actual < m);

    const ultima = conseguidas[conseguidas.length - 1];
    if (ultima !== undefined) {
      logrados.push({
        titulo: serie.titulo(ultima),
        meta: ultima,
        actual,
        unidad: serie.unidad,
        unidadSingular: serie.unidadSingular,
      });
    }
    if (pendiente !== undefined) {
      siguientes.push({
        titulo: serie.titulo(pendiente),
        meta: pendiente,
        actual,
        unidad: serie.unidad,
        unidadSingular: serie.unidadSingular,
      });
    }
  }

  // El más cerca de conseguirse primero: es el que vale la pena empujar hoy.
  siguientes.sort((a, b) => a.actual / a.meta - b.actual / b.meta).reverse();
  return { logrados, siguientes };
}
