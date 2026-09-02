/**
 * Pantalla de carga de la confirmación del pago.
 *
 * Se vuelve de la pasarela y hay que consultar si el pago cuajó. Es el peor
 * sitio del sitio para dejar la pantalla en blanco: quien acaba de pagar y no ve
 * nada asume que perdió la plata.
 */
import { Cargando, Tarjeta, Linea } from "@/components/ui/esqueleto";

export default function PlanResultadoLoading() {
  return (
    <Cargando etiqueta="Confirmando tu pago">
      <div className="mx-auto max-w-lg text-center">
        <div className="mx-auto h-12 w-12 rounded-full bg-surface" />
        <div className="mt-4 flex justify-center">
          <Linea className="h-8 w-64" />
        </div>
        <div className="mt-6">
          <Tarjeta className="h-28" />
        </div>
      </div>
    </Cargando>
  );
}
