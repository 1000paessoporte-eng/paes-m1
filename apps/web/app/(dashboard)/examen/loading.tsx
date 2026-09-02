/**
 * Pantalla de carga del ensayo.
 *
 * El ensayo se abre en dos columnas: la pregunta a la izquierda y el panel de
 * navegación a la derecha. Aquí se nota más que en ningún otro sitio, porque es
 * la pantalla que la gente abre con prisa.
 */
import { Cargando, Tarjeta, Linea } from "@/components/ui/esqueleto";

export default function ExamenLoading() {
  return (
    <Cargando etiqueta="Preparando el ensayo">
      <div className="lg:grid lg:grid-cols-[1.15fr_1fr] lg:items-start lg:gap-6">
        <div className="space-y-5">
          <Linea className="h-4 w-32" />
          <Tarjeta className="h-72" />
          <div className="flex gap-3">
            <Linea className="h-11 w-32 rounded-xl" />
            <Linea className="h-11 w-32 rounded-xl" />
          </div>
        </div>
        <div className="mt-6 lg:mt-0">
          <Tarjeta className="h-64" />
        </div>
      </div>
    </Cargando>
  );
}
