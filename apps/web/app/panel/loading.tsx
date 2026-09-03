/**
 * Pantalla de carga del panel de inicio.
 *
 * Es lo primero que ve al entrar quien ya tiene cuenta. Título, las cuatro
 * cifras de cabecera y las tres columnas de tarjetas.
 */
import { Cargando, Titulo, Rejilla } from "@/components/ui/esqueleto";

export default function PanelLoading() {
  return (
    <Cargando etiqueta="Cargando tu panel">
      <main className="mx-auto w-full max-w-6xl flex-1 p-6">
        <Titulo className="w-64" />
        <div className="mt-7">
          <Rejilla cuantas={4} columnas="grid-cols-2 sm:grid-cols-4" alto="h-20" />
        </div>
        <div className="mt-8">
          <Rejilla cuantas={3} columnas="grid-cols-1 lg:grid-cols-3" alto="h-48" />
        </div>
      </main>
    </Cargando>
  );
}
