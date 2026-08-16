import type { Metadata } from "next";
import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getMiPlan } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";

export const metadata: Metadata = {
  title: "Resultado del pago",
  robots: { index: false, follow: false },
};

/**
 * A donde Flow devuelve al usuario cuando termina.
 *
 * Esta pantalla NO decide si el pago se hizo: solo consulta el plan que la API
 * ya tiene registrado. Quien activa la suscripción es el webhook, después de
 * preguntarle a Flow de servidor a servidor. La distinción importa porque esta
 * URL la controla el navegador y cualquiera puede escribirla a mano: si acá se
 * activara algo, regalar el plan Pro sería cuestión de visitarla.
 *
 * De ahí el caso intermedio que la pantalla contempla: el usuario puede llegar
 * antes de que Flow alcance a avisar. En vez de decirle que su pago falló, se
 * le explica que puede tardar un momento y se le ofrece recargar.
 */
export default async function ResultadoPagoPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (!token) redirect("/login?next=/plan/resultado");

  const plan = await getMiPlan(token);
  const activo = plan.plan !== "gratis";

  return (
    <div className="mx-auto max-w-lg">
      <div className="card-panel p-8 text-center">
        <span
          aria-hidden
          className={
            "text-4xl " + (activo ? "text-success" : "text-accent")
          }
        >
          {activo ? "✓" : "⏳"}
        </span>

        <h1 className="mt-4 text-2xl font-semibold tracking-tight">
          {activo ? "Listo, tu plan está activo" : "Estamos confirmando tu pago"}
        </h1>

        {activo ? (
          <p className="mt-3 text-sm leading-relaxed text-muted">
            Tu plan {plan.plan === "pro" ? "Pro" : plan.plan} quedó activo
            {plan.vence_el && (
              <>
                {" "}hasta el{" "}
                {new Date(plan.vence_el).toLocaleDateString("es-CL", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}
              </>
            )}
            . Ya puedes rendir ensayos sin límite.
          </p>
        ) : (
          <p className="mt-3 text-sm leading-relaxed text-muted">
            Si acabas de pagar, la confirmación puede tardar un momento en
            llegar. Recarga esta página en unos segundos. Si el cobro se hizo y
            el plan no aparece, escríbenos y lo revisamos: el pago queda
            registrado aunque la pantalla todavía no lo muestre.
          </p>
        )}

        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link
            href={activo ? "/examen" : "/plan/resultado"}
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
          >
            {activo ? "Rendir un ensayo" : "Recargar"}
          </Link>
          <Link
            href="/perfil"
            className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium transition-colors hover:bg-surface-hover"
          >
            Ver mi plan
          </Link>
        </div>
      </div>
    </div>
  );
}
