/**
 * PAES Regular, Proceso de Admisión 2027: se rinde el 30 de noviembre, 1 y 2
 * de diciembre de 2026 (calendario oficial DEMRE). Se usa el primer día como
 * fecha objetivo del countdown.
 */
export const FECHA_PAES = new Date("2026-11-30T00:00:00-03:00");

/** Días completos que faltan para la PAES. Null si ya pasó la fecha. */
export function diasHastaPaes(ahora: Date = new Date()): number | null {
  const diffMs = FECHA_PAES.getTime() - ahora.getTime();
  if (diffMs <= 0) return null;
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}
