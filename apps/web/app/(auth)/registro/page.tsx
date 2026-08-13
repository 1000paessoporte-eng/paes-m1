import { Suspense } from "react";
import { AuthPanel } from "@/components/auth/auth-panel";

// Misma pantalla que /login, abierta en la pestaña de crear cuenta.
export default function RegistroPage() {
  return (
    <Suspense>
      <AuthPanel initialTab="registro" />
    </Suspense>
  );
}
