import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import { AuthPanel } from "@/components/auth/auth-panel";
import { TOKEN_COOKIE } from "@/lib/auth";


/**
 * Con la sesión ya iniciada, pedir la contraseña otra vez no tiene sentido: el
 * encabezado de la misma página dice "Hola, {nombre}" mientras el formulario
 * pide entrar. Se manda al panel, que es a donde iba.
 */
async function conSesion(): Promise<boolean> {
  return (await cookies()).get(TOKEN_COOKIE)?.value != null;
}

export const metadata = {
  title: "Iniciar sesión",
  description: "Entra a tu cuenta para continuar tus ensayos.",
  alternates: { canonical: "/login" },
  // Fuera del índice: es una pantalla de utilidad, no un resultado de
  // búsqueda. Quien la necesita ya tiene cuenta y llega por el menú, y
  // estaba compitiendo por presupuesto de rastreo con las 1.855 fichas de
  // carrera, que es lo que sí queremos que Google recorra.
  robots: { index: false, follow: true },
};


// `AuthPanel` lee `?next=` con useSearchParams, que exige un límite de Suspense
// para no forzar el renderizado dinámico de toda la ruta.
export default async function LoginPage() {
  if (await conSesion()) redirect("/panel");

  return (
    <Suspense>
      <AuthPanel initialTab="login" />
    </Suspense>
  );
}
