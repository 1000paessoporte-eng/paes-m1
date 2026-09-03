/**
 * Pantalla de carga de la práctica por nodo.
 *
 * Una sola pregunta con sus cuatro alternativas. Ya había un aviso de texto en
 * la propia página; esto además le da la forma que va a ocupar.
 */
import { Cargando, Linea, Tarjeta } from "@/components/ui/esqueleto";

export default function PracticarLoading() {
  return (
    <Cargando etiqueta="Cargando una pregunta">
      <Linea className="h-4 w-40" />
      <div className="mt-5">
        <Tarjeta className="h-32" />
      </div>
      <div className="mt-5 space-y-3">
        <Tarjeta className="h-14" />
        <Tarjeta className="h-14" />
        <Tarjeta className="h-14" />
        <Tarjeta className="h-14" />
      </div>
    </Cargando>
  );
}
