/**
 * Pantalla de carga de login, registro y recuperación de contraseña.
 *
 * Las tres son dinámicas —leen la cookie de sesión antes de decidir si te dejan
 * pasar o te redirigen— y comparten la misma forma: una tarjeta centrada y
 * estrecha con el formulario dentro. Una sola pantalla sirve para el grupo.
 */
import { Cargando, Linea, Tarjeta } from "@/components/ui/esqueleto";

export default function AuthLoading() {
  return (
    <Cargando etiqueta="Cargando">
      <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center px-6 py-16">
        <Linea className="mx-auto h-7 w-44" />
        <div className="mt-8">
          <Tarjeta className="h-64" />
        </div>
        <Linea className="mx-auto mt-6 h-4 w-52" />
      </main>
    </Cargando>
  );
}
