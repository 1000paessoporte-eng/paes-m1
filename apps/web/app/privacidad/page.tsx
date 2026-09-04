import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Política de privacidad",
  alternates: { canonical: "/privacidad" },
};

export default function PrivacidadPage() {
  return (
    <>
    <main className="flex-1 px-6 py-16">
      <article className="mx-auto max-w-2xl">
        <h1 className="text-2xl font-semibold tracking-tight">Política de privacidad</h1>
        <p className="mt-2 text-sm text-muted">Última actualización: agosto de 2026.</p>

        <div className="mt-8 flex flex-col gap-6 text-sm leading-relaxed text-muted [&_h2]:text-base [&_h2]:font-semibold [&_h2]:text-foreground [&_p]:mt-2 [&_ul]:mt-2 [&_ul]:list-disc [&_ul]:pl-5">
          <section>
            <h2>1. Qué datos recogemos</h2>
            <ul>
              <li>Nombre y correo, al crear tu cuenta.</li>
              <li>
                Tu contraseña, nunca en texto plano: se guarda con un hash
                (bcrypt) que no se puede revertir.
              </li>
              <li>
                Si entras con Google: tu identificador de cuenta de Google y
                tu foto de perfil, entregados por Google con tu autorización.
              </li>
              <li>
                Tus respuestas, resultados y tiempos en los ensayos, y tu
                avance en el árbol de habilidades — es lo que permite mostrar
                tu puntaje estimado, tu historial y qué reforzar.
              </li>
              <li>
                Tu correo, si nos lo dejas desde la demo sin crear cuenta. Solo
                guardamos el correo y desde qué pantalla lo dejaste; lo usamos
                para avisarte de material y funciones nuevas, y puedes pedir
                que lo borremos cuando quieras.
              </li>
            </ul>
          </section>

          <section>
            <h2>2. Para qué usamos tus datos</h2>
            <p>
              Solo para operar la plataforma: autenticarte, guardar tu
              progreso, calcular tu puntaje estimado y recomendarte en qué
              nodo del árbol de habilidades reforzar.{" "}
              <strong>No vendemos ni compartimos tus datos con terceros con fines comerciales o publicitarios.</strong>
            </p>
          </section>

          <section>
            <h2>3. Con quién los compartimos</h2>
            <p>Solo con proveedores necesarios para operar el servicio:</p>
            <ul>
              <li>Google, si eliges iniciar sesión con tu cuenta de Google.</li>
              <li>
                Nuestro proveedor de hosting y base de datos, donde vive la
                información de tu cuenta.
              </li>
              <li>
                Un proveedor de correo, únicamente para enviarte el enlace de
                recuperación de contraseña cuando lo solicitas.
              </li>
              <li>
                Flow, la pasarela de pago, si contratas un plan. El pago ocurre
                en su plataforma: 1000paes nunca recibe ni guarda los datos de
                tu tarjeta.
              </li>
            </ul>
            <p>
              No vendemos tus datos, no los cedemos con fines publicitarios ni
              los usamos para entrenar modelos de inteligencia artificial.
            </p>
            <p>
              <strong>Dónde se alojan.</strong> El sitio y la base de datos
              funcionan sobre proveedores de infraestructura cuyos servidores
              están fuera de Chile. Eso implica una transferencia internacional
              de tus datos, que hacemos solo con los proveedores necesarios para
              que la plataforma funcione y bajo sus compromisos contractuales de
              seguridad y confidencialidad.
            </p>
          </section>

          <section>
            <h2>4. Menores de edad</h2>
            <p>
              El plan Colegios está pensado para que un establecimiento
              contrate el acceso para su alumnado, que puede incluir menores
              de edad. En ese caso, es responsabilidad del colegio contar con
              la autorización correspondiente de los apoderados. Solo
              recogemos los datos mínimos necesarios para operar el árbol de
              habilidades y los ensayos de cada estudiante.
            </p>
            <p>
              Buena parte de quienes preparan la PAES son menores de 18 años y
              se registran por su cuenta. Si es tu caso,{" "}
              <strong>
                necesitas la autorización de tu madre, padre o apoderado
              </strong>{" "}
              para crear la cuenta, y en ningún caso te pedimos más datos de los
              necesarios para estudiar: nunca RUT, dirección, teléfono ni datos
              de salud.
            </p>
            <p>
              <strong>Si eres madre, padre o apoderado</strong> y quieres saber
              qué datos tenemos de tu hijo o hija, corregirlos o eliminarlos,
              escríbenos y lo resolvemos sin trámites. Lo mismo si detectas una
              cuenta o un cobro que no autorizaste.
            </p>
          </section>

          <section>
            <h2>5. Seguridad</h2>
            <p>
              Las contraseñas se guardan con hash bcrypt (no en texto plano).
              La sesión se identifica con un token firmado (JWT) que expira a
              los 14 días. Los enlaces de recuperación de contraseña son de un
              solo uso y expiran a los 30 minutos.
            </p>
          </section>

          <section>
            <h2>6. Cookies y almacenamiento local</h2>
            <p>
              1000paes guarda tu token de sesión en una cookie del navegador y
              usa el almacenamiento local para no perder tu progreso en un
              ensayo si recargas la página. No usamos cookies de rastreo ni
              publicidad de terceros.
            </p>
            <p>
              Para saber cuánta gente usa el sitio guardamos, por cada página
              que se abre, la ruta visitada y un número aleatorio que se genera
              en tu navegador. Ese número no dice quién eres: solo sirve para no
              contarte varias veces si abres varias páginas. No guardamos tu
              dirección IP ni tu user agent, y puedes borrarlo cuando quieras
              vaciando el almacenamiento local del sitio.
            </p>
          </section>

          <section>
            <h2>7. Tus derechos sobre tus datos</h2>
            <p>
              Puedes editar tu nombre y contraseña desde tu perfil, y borrar
              intentos de ensayo individuales desde tu historial. Para acceder
              a una copia de tus datos, corregirlos, eliminar tu cuenta por
              completo o sacar tu correo de la lista de avisos, escríbenos a{" "}
              <a href="mailto:1000paessoporte@gmail.com" className="text-accent hover:underline">
                1000paessoporte@gmail.com
              </a>
              .
            </p>
            <p>
              La ley chilena te reconoce los derechos de{" "}
              <strong>
                acceso, rectificación, cancelación y oposición
              </strong>{" "}
              sobre tus datos personales, además de pedir que te los entreguemos
              en un formato que puedas llevarte. Ejercerlos es gratuito y{" "}
              <strong>respondemos dentro de 5 días hábiles</strong>. Si no
              quedas conforme con nuestra respuesta, puedes reclamar ante la
              autoridad de protección de datos que corresponda.
            </p>
            <p>
              Si alguna vez ocurriera una brecha de seguridad que afecte tus
              datos, te avisaremos por correo apenas la detectemos, contándote
              qué pasó y qué hacer.
            </p>
          </section>

          <section>
            <h2>8. Cuánto tiempo conservamos tus datos</h2>
            <p>
              Mientras tu cuenta esté activa. Si pides eliminar tu cuenta,
              borramos tus datos personales salvo que la ley nos obligue a
              conservar algún registro por más tiempo.
            </p>
          </section>

          <section>
            <h2>9. Cambios a esta política</h2>
            <p>
              Si hacemos cambios relevantes a esta política, lo indicaremos en
              la plataforma antes de que entren en vigencia.
            </p>
          </section>

          <section>
            <h2>10. Contacto</h2>
            <p>
              Ante cualquier duda sobre tus datos, escríbenos a{" "}
              <a href="mailto:1000paessoporte@gmail.com" className="text-accent hover:underline">
                1000paessoporte@gmail.com
              </a>
              .
            </p>
          </section>
        </div>

        <p className="mt-10 text-xs text-muted">
          Ver también nuestros{" "}
          <Link href="/terminos" className="text-accent hover:underline">
            Términos y Condiciones
          </Link>
          .
        </p>
      </article>
    </main>
    <SiteFooter />
    </>
  );
}
