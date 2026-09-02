/**
 * Pantalla de carga del panel de administración.
 *
 * Dos rejillas de métricas y las tablas de abajo.
 */
import { Cargando, Titulo, Rejilla, Filas } from "@/components/ui/esqueleto";

export default function AdminLoading() {
  return (
    <Cargando etiqueta="Cargando el panel">
      <Titulo className="w-72" />
      <div className="mt-6">
        <Rejilla cuantas={4} columnas="grid-cols-2 lg:grid-cols-4" alto="h-24" />
      </div>
      <div className="mt-6">
        <Rejilla cuantas={4} columnas="grid-cols-2 lg:grid-cols-4" alto="h-24" />
      </div>
      <div className="mt-8">
        <Filas cuantas={6} />
      </div>
    </Cargando>
  );
}
