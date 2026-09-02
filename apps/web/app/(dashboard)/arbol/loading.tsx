/**
 * Pantalla de carga del árbol de habilidades.
 *
 * Título, la fila de pruebas y la rejilla de nodos: es lo que va a llegar, así
 * que el contenido entra sin mover nada de sitio.
 */
import { Cargando, Titulo, Pildoras, Rejilla } from "@/components/ui/esqueleto";

export default function ArbolLoading() {
  return (
    <Cargando etiqueta="Cargando el árbol de habilidades">
      <Titulo className="w-72" />
      <div className="mt-5">
        <Pildoras cuantas={5} />
      </div>
      <div className="mt-6">
        <Rejilla cuantas={6} columnas="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3" alto="h-36" />
      </div>
    </Cargando>
  );
}
