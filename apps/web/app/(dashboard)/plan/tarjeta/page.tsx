import type { Metadata } from "next";
import { ConfirmarTarjeta } from "@/components/plan/confirmar-tarjeta";

export const metadata: Metadata = {
  title: "Activando tu prueba",
  robots: { index: false, follow: false },
};

/** A donde Flow devuelve al usuario tras registrar su tarjeta para el trial. */
export default function TarjetaPage() {
  return (
    <div className="mx-auto max-w-lg">
      <ConfirmarTarjeta />
    </div>
  );
}
