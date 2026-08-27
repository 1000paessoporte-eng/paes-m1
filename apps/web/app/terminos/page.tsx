import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Términos y condiciones",
  alternates: { canonical: "/terminos" },
};

export default function TerminosPage() {
  return (
    <>
    <main className="flex-1 px-6 py-16">
      <article className="mx-auto max-w-2xl">
        <h1 className="text-2xl font-semibold tracking-tight">Términos y condiciones</h1>
        <p className="mt-2 text-sm text-muted">Última actualización: agosto de 2026.</p>

        <div className="mt-8 flex flex-col gap-6 text-sm leading-relaxed text-muted [&_h2]:text-base [&_h2]:font-semibold [&_h2]:text-foreground [&_p]:mt-2 [&_ul]:mt-2 [&_ul]:list-disc [&_ul]:pl-5">
          <section>
            <h2>1. Qué es 1000paes</h2>
            <p>
              1000paes es una plataforma de preparación para la PAES (Prueba
              de Acceso a la Educación Superior) de Chile, con foco en
              Competencia Matemática (M1 y M2): ensayos cronometrados,
              puntaje estimado, revisión de cada pregunta y seguimiento de tu
              progreso. <strong>1000paes no tiene relación con el DEMRE</strong>{" "}
              ni con ninguna institución oficial del proceso de admisión. El
              puntaje que entrega la plataforma es una estimación referencial
              y no garantiza el puntaje real que obtengas al rendir la PAES.
            </p>
          </section>

          <section>
            <h2>2. Tu cuenta</h2>
            <p>
              Para usar 1000paes necesitas una cuenta, creada con correo y
              contraseña o con tu cuenta de Google. Eres responsable de
              mantener tu contraseña en privado y de todo lo que ocurra bajo
              tu cuenta. Avísanos si sospechas que alguien más accedió a ella.
            </p>
          </section>

          <section>
            <h2>3. Uso permitido</h2>
            <p>La cuenta es personal e intransferible. No está permitido:</p>
            <ul>
              <li>Compartir tu cuenta o revender el acceso a terceros.</li>
              <li>
                Extraer de forma automatizada (scraping) las preguntas,
                explicaciones o cualquier contenido de la plataforma.
              </li>
              <li>
                Intentar vulnerar la seguridad del servicio o acceder a datos
                de otros usuarios.
              </li>
            </ul>
          </section>

          <section>
            <h2>4. Planes y pagos</h2>
            <p>
              El <strong>plan Gratis</strong> no tiene costo e incluye todo el
              material de estudio: el árbol de habilidades completo, las
              lecciones de las cinco pruebas y el banco de preguntas. Tiene una
              cuota mensual de ensayos y permite guardar una carrera en Mi
              meta. La cuota vigente se publica en la página de{" "}
              <Link href="/planes" className="underline">Planes</Link>.
            </p>
            <p>
              El <strong>plan Pro</strong> quita la cuota de ensayos y permite
              guardar hasta diez carreras. Se ofrece en dos períodos: mensual y
              anual. Los precios están expresados en pesos chilenos, se
              muestran en la página de Planes antes de contratar y se cobran a
              través de <strong>Flow</strong>, la pasarela de pago; 1000paes no
              almacena los datos de tu tarjeta.
            </p>
            <p>
              <strong>Cancelar es un clic desde tu perfil</strong>, sin
              escribirle a nadie. Al cancelar se detiene la renovación y{" "}
              <strong>conservas el acceso hasta el final del período que ya
              pagaste</strong>: no se corta el servicio el día que cancelas ni
              se cobran días que no vas a usar.
            </p>
            <p>
              El <strong>plan Colegios</strong> no se contrata desde la web: se
              acuerda conversando y se activa a mano. Si te interesa, escríbenos
              a <a href="mailto:1000paessoporte@gmail.com" className="underline">1000paessoporte@gmail.com</a>.
            </p>
            <p>
              No se realizan cobros sin tu consentimiento explícito. Si
              cambiamos los precios, el cambio no afecta a un período que ya
              pagaste.
            </p>
          </section>

          <section>
            <h2>5. Propiedad del contenido</h2>
            <p>
              Las preguntas, alternativas, explicaciones y el diseño de la
              plataforma son propiedad de 1000paes o de sus licenciantes. Puedes
              usarlos para tu preparación personal, pero no reproducirlos ni
              distribuirlos fuera de la plataforma sin autorización.
            </p>
          </section>

          <section>
            <h2>6. Disponibilidad del servicio</h2>
            <p>
              1000paes está en desarrollo activo: features, el banco de
              preguntas y la disponibilidad del servicio pueden cambiar. Hacemos
              lo posible por avisar con anticipación cambios que te afecten,
              pero no podemos garantizar un funcionamiento ininterrumpido.
            </p>
          </section>

          <section>
            <h2>7. Cierre de cuenta</h2>
            <p>
              Puedes dejar de usar 1000paes cuando quieras. Para eliminar tu
              cuenta y tus datos, escríbenos a{" "}
              <a href="mailto:1000paessoporte@gmail.com" className="text-accent hover:underline">
                1000paessoporte@gmail.com
              </a>
              . Podemos suspender o cerrar cuentas que incumplan estos
              términos.
            </p>
          </section>

          <section>
            <h2>8. Cambios a estos términos</h2>
            <p>
              Si actualizamos estos términos de forma relevante, lo
              indicaremos en la plataforma antes de que entren en vigencia.
            </p>
          </section>

          <section>
            <h2>9. Ley aplicable</h2>
            <p>
              Estos términos se rigen por las leyes de Chile. Ante cualquier
              duda, contáctanos a{" "}
              <a href="mailto:1000paessoporte@gmail.com" className="text-accent hover:underline">
                1000paessoporte@gmail.com
              </a>
              .
            </p>
          </section>
        </div>

        <p className="mt-10 text-xs text-muted">
          Ver también nuestra{" "}
          <Link href="/privacidad" className="text-accent hover:underline">
            Política de Privacidad
          </Link>
          .
        </p>
      </article>
    </main>
    <SiteFooter />
    </>
  );
}
