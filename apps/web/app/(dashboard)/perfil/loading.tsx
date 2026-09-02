/**
 * Pantalla de carga del perfil.
 *
 * Cuatro cifras arriba y los bloques de formulario, estrechos como el original.
 */
import { Cargando, Titulo, Rejilla, Tarjeta } from "@/components/ui/esqueleto";

export default function PerfilLoading() {
  return (
    <Cargando etiqueta="Cargando tu perfil">
      <Titulo className="w-40" />
      <div className="mt-6">
        <Rejilla cuantas={4} columnas="grid-cols-2 lg:grid-cols-4" alto="h-24" />
      </div>
      <div className="mt-8 max-w-lg space-y-5">
        <Tarjeta className="h-28" />
        <Tarjeta className="h-28" />
      </div>
    </Cargando>
  );
}
