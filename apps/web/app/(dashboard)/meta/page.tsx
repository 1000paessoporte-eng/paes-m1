import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getMeta, type Meta } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { MetaView } from "@/components/meta/meta-view";

export const metadata = {
  title: "Mi meta",
  description:
    "La carrera a la que quieres entrar, tu puntaje ponderado proyectado y dónde rinde más estudiar.",
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

  return <MetaView inicial={meta} />;
}
