/**
 * Pantalla de carga de la demo.
 *
 * La demo es la puerta de entrada: se llega sin cuenta y desde la portada. Si
 * se queda en blanco mientras la API responde, esa persona se va y no vuelve.
 */
import { Cargando, Tarjeta, Linea } from "@/components/ui/esqueleto";

export default function DemoLoading() {
  return (
    <Cargando etiqueta="Cargando la demo">
      <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-16">
        <Linea className="h-4 w-36" />
        <div className="mt-5">
          <Tarjeta className="h-36" />
        </div>
        <div className="mt-5 space-y-3">
          <Tarjeta className="h-14" />
          <Tarjeta className="h-14" />
          <Tarjeta className="h-14" />
          <Tarjeta className="h-14" />
        </div>
      </main>
    </Cargando>
  );
}
