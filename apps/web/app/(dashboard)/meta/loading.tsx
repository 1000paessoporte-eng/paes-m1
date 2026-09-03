/**
 * Pantalla de carga de Mi meta.
 *
 * El puntaje ponderado arriba y la lista de carreras debajo.
 */
import { Cargando, Titulo, Tarjeta, Filas } from "@/components/ui/esqueleto";

export default function MetaLoading() {
  return (
    <Cargando etiqueta="Cargando tu meta">
      <Titulo className="w-56" />
      <div className="mt-6">
        <Tarjeta className="h-32" />
      </div>
      <div className="mt-6">
        <Filas cuantas={4} />
      </div>
    </Cargando>
  );
}
