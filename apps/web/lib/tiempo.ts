/** Formatea una cantidad de segundos como "1:23:45" o "23:45". */
export function formatearTiempo(segundos: number): string {
  const seg = Math.max(0, Math.floor(segundos));
  const h = Math.floor(seg / 3600);
  const m = Math.floor((seg % 3600) / 60);
  const s = seg % 60;
  const dosDigitos = (n: number) => n.toString().padStart(2, "0");
  return h > 0 ? `${h}:${dosDigitos(m)}:${dosDigitos(s)}` : `${m}:${dosDigitos(s)}`;
}

/** Igual que `formatearTiempo`, pero a partir de milisegundos. */
export function formatearReloj(ms: number): string {
  return formatearTiempo(Math.floor(ms / 1000));
}
