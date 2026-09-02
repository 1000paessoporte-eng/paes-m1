/**
 * Pantalla de carga del historial.
 *
 * Una fila por intento rendido, que es exactamente lo que trae la página.
 */
import { Cargando, Titulo, Rejilla, Filas } from "@/components/ui/esqueleto";

export default function HistorialLoading() {
  return (
    <Cargando etiqueta="Cargando tu progreso">
      <Titulo className="w-48" />
      <div className="mt-6">
        <Rejilla cuantas={3} columnas="grid-cols-3" alto="h-24" />
      </div>
      <div className="mt-6">
        <Filas cuantas={5} />
      </div>
    </Cargando>
  );
}
