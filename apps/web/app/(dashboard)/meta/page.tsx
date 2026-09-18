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

  // Los dos en paralelo: eran independientes y en secuencia sumaban. El plan
  // (cuántas carreras admite) lleva su propio catch: si falla, se asume el tope
  // del sistema, que ofrecer de más y que la API corrija es mejor que esconder
  // carreras a quien las pagó.
  let meta: Meta | null = null;
  let sinSesion = false;
  let plan: Awaited<ReturnType<typeof getMiPlan>> | null = null;
  try {
    [meta, plan] = await Promise.all([
      getMeta(token),
      getMiPlan(token).catch(() => null),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) sinSesion = true;
  }
  if (sinSesion) redirect("/login?next=/meta");

  if (meta === null) {
    return (
      <p className="mx-auto max-w-lg text-center text-sm text-muted">
        No se pudo cargar tu meta. Vuelve a intentarlo en unos segundos.
      </p>
    );
  }

  return <MetaView inicial={meta} tope={plan?.carreras_limite ?? 10} />;
}
