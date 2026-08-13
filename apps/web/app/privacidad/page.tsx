import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Política de privacidad — 1000paes",
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
            </ul>
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
              a una copia de tus datos, corregirlos o eliminar tu cuenta por
              completo, escríbenos a{" "}
              <a href="mailto:hola@1000paes.cl" className="text-accent hover:underline">
                hola@1000paes.cl
              </a>
              .
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
              <a href="mailto:hola@1000paes.cl" className="text-accent hover:underline">
                hola@1000paes.cl
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
