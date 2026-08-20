import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getRepasoSesion } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { RepasoRunner } from "@/components/repaso/repaso-runner";
import { EstadoVacio } from "@/components/estado-vacio";

export const metadata = {
  title: "Repaso inteligente",
  description: "Las preguntas que fallaste vuelven hasta que las domines.",
};

export default async function RepasoPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let sesion;
  try {
    sesion = await getRepasoSesion(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/repaso");
    throw err;
  }

  if (sesion.preguntas.length === 0) {
    return (
      <EstadoVacio
        title="No tienes nada que repasar hoy"
        description="Acá vuelven las preguntas que fallaste, con esperas cada vez más largas, hasta que las domines. Rinde un ensayo o practica un nodo del árbol: las que se te escapen aparecerán mañana."
        accion={{ href: "/examen", label: "Rendir un ensayo →" }}
        icon={
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
            <path d="M3 3v5h5" />
          </svg>
        }
      />
    );
  }

  return (
    <RepasoRunner
      preguntas={sesion.preguntas}
      pendientesTotales={sesion.pendientes_totales}
    />
  );
}
