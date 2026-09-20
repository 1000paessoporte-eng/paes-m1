import { Suspense } from "react";
import { RetornoMicrosoft } from "@/components/auth/retorno-microsoft";

/**
 * A donde vuelve Microsoft después de que la persona se autenticó.
 *
 * Es una ruta propia y no un parámetro de `/login` porque la URI de retorno se
 * registra en Entra ID carácter a carácter: mientras menos cosas puedan
 * cambiarla, menos posibilidades de que un día deje de coincidir y el inicio
 * de sesión falle con un error que no dice nada.
 *
 * Fuera del grupo `(auth)`: esa ruta redirige al panel cuando ya hay sesión, y
 * acá la sesión es justamente lo que se está creando.
 */
export const metadata = {
  title: "Entrando con Microsoft",
  robots: { index: false, follow: false },
};

export default function EntrarConMicrosoftPage() {
  return (
    <Suspense fallback={<Mensaje texto="Entrando…" />}>
      <RetornoMicrosoft />
    </Suspense>
  );
}

function Mensaje({ texto }: { texto: string }) {
  return (
    <main className="mx-auto flex min-h-[60vh] max-w-md items-center justify-center px-6">
      <p className="text-sm text-muted">{texto}</p>
    </main>
  );
}
