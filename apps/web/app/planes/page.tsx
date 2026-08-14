import { Planes } from "@/components/home/planes";
import { SiteFooter } from "@/components/site-footer";

export const metadata = {
  title: "Planes",
  description: "Qué incluye cada plan de 1000paes y cuánto cuesta.",
};

/**
 * Los planes tienen página propia en vez de colgar del panel del alumno: la
 * pantalla de trabajo de quien está estudiando no es lugar para una vitrina
 * comercial de pantalla completa. La portada pública mantiene su sección.
 */
export default function PlanesPage() {
  return (
    <main className="flex flex-1 flex-col">
      <Planes />
      <SiteFooter />
    </main>
  );
}
