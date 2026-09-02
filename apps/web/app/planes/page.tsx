import { Planes, type OfertaTrial } from "@/components/home/planes";
import { getProductos } from "@/lib/api";
import { SiteFooter } from "@/components/site-footer";

export const metadata = {
  title: "Planes",
  description:
    "El plan Gratis no tiene costo ni vencimiento: 4 ensayos al mes con el banco completo, el árbol y las lecciones. Pro quita el tope por $9.990 al mes.",
  alternates: { canonical: "/planes" },
};

/**
 * Los planes tienen página propia en vez de colgar del panel del alumno: la
 * pantalla de trabajo de quien está estudiando no es lugar para una vitrina
 * comercial de pantalla completa. La portada pública mantiene su sección.
 */
export default async function PlanesPage() {
  // Si el catálogo no responde, la página se dibuja igual con el cobro
  // apagado: una vitrina sin botón es mucho mejor que una página caída.
  let pagoDisponible = false;
  let trial: OfertaTrial | null = null;
  try {
    const productos = await getProductos();
    pagoDisponible = productos.pago_disponible;
    trial = {
      disponible: productos.trial_disponible,
      dias: productos.trial_dias,
      monto: productos.trial_monto,
    };
  } catch {
    pagoDisponible = false;
    trial = null;
  }

  return (
    <main className="flex flex-1 flex-col">
      <Planes pagoDisponible={pagoDisponible} trial={trial} encabezado="h1" />
      <SiteFooter />
    </main>
  );
}
