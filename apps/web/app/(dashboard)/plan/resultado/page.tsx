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
 * Sirve para los dos caminos --el pago suelto y la inscripción de tarjeta de la
 * prueba gratis-- porque la pregunta que responde es la misma: "¿quedó
 * activo?". La respuesta sale de consultar el plan real, no del parámetro que
 * traiga la URL.
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
export default async function ResultadoPagoPage({
  searchParams,
}: PageProps<"/plan/resultado">) {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (!token) redirect("/login?next=/plan/resultado");

  const params = await searchParams;
  const plan = await getMiPlan(token);
  const activo = plan.plan !== "gratis";

  // El parámetro solo cambia CÓMO se explica, nunca lo que se afirma: quien
  // decide si el plan está activo es la API. Si se decidiera acá, activar Pro
  // sería cuestión de escribir la URL a mano.
  const veniaDelTrial = params.origen === "trial";
  const estado = typeof params.estado === "string" ? params.estado : null;

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
          {activo
            ? plan.en_trial
              ? `Listo: tienes ${plan.trial_dias} días de Pro`
              : "Listo, tu plan está activo"
            : veniaDelTrial
              ? "No alcanzamos a activar tu prueba"
              : "Estamos confirmando tu pago"}
        </h1>

        {activo && plan.en_trial ? (
          /* Lo primero que se le dice a alguien que acaba de entregar su
             tarjeta es cuándo se le va a cobrar y cuánto. Esconderlo acá,
             justo donde está mirando, es lo que convierte una prueba en un
             cobro por sorpresa y termina en reclamo. */
          <p className="mt-3 text-sm leading-relaxed text-muted">
            Ya puedes rendir ensayos sin límite.
            {plan.vence_el && (
              <>
                {" "}El{" "}
                <strong className="font-medium text-foreground">
                  {new Date(plan.vence_el).toLocaleDateString("es-CL", {
                    day: "numeric",
                    month: "long",
                  })}
                </strong>{" "}
                se cobran ${plan.trial_monto.toLocaleString("es-CL")}
                {plan.tarjeta ? ` a tu ${plan.tarjeta}` : ""} y desde ahí el
                plan se renueva cada mes. Si cancelas antes de esa fecha, no se
                te cobra nada.
              </>
            )}
          </p>
        ) : activo ? (
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
        ) : veniaDelTrial ? (
          <p className="mt-3 text-sm leading-relaxed text-muted">
            {estado === "sin-tarjeta"
              ? "Tu tarjeta no quedó inscrita, así que no se te cobró nada y tu cuenta sigue en el plan Gratis. Puedes intentarlo de nuevo cuando quieras."
              : "No pudimos confirmar la inscripción de tu tarjeta. No se te cobró nada. Si crees que sí quedó registrada, recarga en unos segundos antes de intentarlo de nuevo: nunca cobramos dos veces la misma prueba."}
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
            href={activo ? "/examen" : veniaDelTrial ? "/planes" : "/plan/resultado"}
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
          >
            {activo ? "Rendir un ensayo" : veniaDelTrial ? "Volver a intentar" : "Recargar"}
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
