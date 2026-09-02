/**
 * El respaldo del dashboard.
 *
 * Cada página de aquí dentro tiene ahora su propio `loading.tsx` con su forma
 * real. Esta queda como red: si mañana se agrega una ruta y nadie le escribe la
 * suya, se ve esto en vez de una pantalla en blanco.
 */
import { Cargando, Titulo, Tarjeta } from "@/components/ui/esqueleto";

export default function DashboardLoading() {
  return (
    <Cargando>
      <Titulo className="w-48" />
      <div className="mt-6 space-y-4">
        <Tarjeta className="h-40" />
        <Tarjeta className="h-40" />
      </div>
    </Cargando>
  );
}
