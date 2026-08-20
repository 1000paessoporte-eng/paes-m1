import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getMeta, getMiPlan, type Meta } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { MetaView } from "@/components/meta/meta-view";

export const metadata = {
  title: "Mi meta",
  description:
    "Tu lista de postulación, cuánto falta para cada preferencia y qué practicar para acortar la brecha.",
};

export default async function MetaPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let meta: Meta | null = null;
  let sinSesion = false;
  try {
    meta = await getMeta(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) sinSesion = true;
  }
  if (sinSesion) redirect("/login?next=/meta");

  // Cuántas carreras admite SU plan. Si falla, se asume el tope del sistema:
  // que la pantalla ofrezca de más y la API corrija es mejor que esconderle
  // carreras a quien sí las tiene pagadas.
  const plan = await getMiPlan(token).catch(() => null);

  if (meta === null) {
    return (
      <p className="mx-auto max-w-lg text-center text-sm text-muted">
        No se pudo cargar tu meta. Vuelve a intentarlo en unos segundos.
      </p>
    );
  }

  return <MetaView inicial={meta} tope={plan?.carreras_limite ?? 10} />;
}
