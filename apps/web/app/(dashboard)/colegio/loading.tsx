/**
 * Pantalla de carga del panel del colegio.
 *
 * El curso, su avance por eje y los ensayos agendados.
 */
import { Cargando, Titulo, Tarjeta, Filas } from "@/components/ui/esqueleto";

export default function ColegioLoading() {
  return (
    <Cargando etiqueta="Cargando el curso">
      <Titulo className="w-64" />
      <div className="mt-6">
        <Tarjeta className="h-36" />
      </div>
      <div className="mt-6">
        <Filas cuantas={5} />
      </div>
    </Cargando>
  );
}
