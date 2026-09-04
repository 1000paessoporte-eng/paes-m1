/**
 * Cifras de la auditoría de contenido, para citarlas en la sección legal.
 *
 * Salen de `apps/api/scripts/auditar_derechos.py`, que compara el banco
 * completo contra los folletos oficiales liberados por el DEMRE y deja un
 * informe fechado en `docs/`. Están acá y no escritas a mano en el JSX porque
 * el sitio afirma en público que el banco es original: si la cifra que se
 * muestra deja de corresponder al último informe, la afirmación se convierte
 * en publicidad falsa, que es un problema mayor que el que se quería evitar.
 *
 * REGLA: cada vez que se corra la auditoría, actualizar esto en el mismo
 * commit. Si el resultado deja de ser cero, hay que corregir el banco antes de
 * publicar, no cambiar el texto.
 */
export const AUDITORIA_CONTENIDO = {
  /** Fecha del informe vigente en `docs/auditoria-derechos-<fecha>.md`. */
  fecha: "3 de septiembre de 2026",
  /** Enunciados, alternativas, explicaciones y textos base comparados. */
  piezas: "5.531",
  /** Folletos de pruebas oficiales usados como corpus (sin contar temarios). */
  folletos: 11,
  /** Palabras consecutivas a partir de las cuales se considera bandera roja. */
  umbral: 12,
  /** Coincidencia más larga encontrada, en palabras. */
  maximo: 10,
  /** Cuántas piezas alcanzan ese máximo. */
  piezasEnElMaximo: 2,
  /** Piezas sin ninguna coincidencia de seis palabras o más. */
  sinCoincidencia: "5.205",
} as const;
