import { Suspense } from "react";
import { AuthPanel } from "@/components/auth/auth-panel";

export const metadata = {
  title: "Crear cuenta",
  description: "Crea tu cuenta gratis y empieza a practicar para la PAES.",
};


// Misma pantalla que /login, abierta en la pestaña de crear cuenta.
export default function RegistroPage() {
  return (
    <Suspense>
      <AuthPanel initialTab="registro" />
    </Suspense>
  );
}
