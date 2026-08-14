import { Suspense } from "react";
import { AuthPanel } from "@/components/auth/auth-panel";

export const metadata = {
  title: "Iniciar sesión",
  description: "Entra a tu cuenta para continuar tus ensayos.",
};


// `AuthPanel` lee `?next=` con useSearchParams, que exige un límite de Suspense
// para no forzar el renderizado dinámico de toda la ruta.
export default function LoginPage() {
  return (
    <Suspense>
      <AuthPanel initialTab="login" />
    </Suspense>
  );
}
