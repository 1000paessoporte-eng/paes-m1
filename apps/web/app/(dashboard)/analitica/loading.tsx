/**
 * Pantalla de carga de la analítica.
 *
 * Los gráficos son SVG propios y tardan lo que tarda la consulta que los llena.
 * Las tres cifras de arriba y las dos columnas de gráficos, en su sitio.
 */
import { Cargando, Titulo, Rejilla } from "@/components/ui/esqueleto";

export default function AnaliticaLoading() {
  return (
    <Cargando etiqueta="Cargando tu analítica">
      <Titulo className="w-40" />
      <div className="mt-6">
        <Rejilla cuantas={3} columnas="grid-cols-3" alto="h-24" />
      </div>
      <div className="mt-6">
        <Rejilla cuantas={2} columnas="grid-cols-1 xl:grid-cols-2" alto="h-64" />
      </div>
      <div className="mt-6">
        <Rejilla cuantas={2} columnas="grid-cols-1 xl:grid-cols-2" alto="h-64" />
      </div>
    </Cargando>
  );
}
