import type { Metadata } from "next";
import Link from "next/link";
import { FormularioCotizacion } from "@/components/colegios/formulario-cotizacion";
import { SiteFooter } from "@/components/site-footer";

/**
 * La página del plan Colegios.
 *
 * Existía el plan --con precio, panel del profesor, código de curso y ensayos
 * programados, todo construido-- pero no existía dónde contratarlo: en la
 * página de planes había un `mailto:` y nada más. Un colegio que quiere
 * comprar necesita ver qué recibe, cuánto cuesta y cómo se paga, y poder
 * pedirlo sin escribir un correo desde cero.
 *
 * Cada promesa de esta página corresponde a algo que el código hace hoy. La
 * lista sale de `components/home/planes.tsx`, que ya está curada contra el
 * backend: si algo cambia allá, tiene que cambiar acá.
 */

export const metadata: Metadata = {
  title: "Plan Colegios: 1000paes para tu curso",
  description:
    "Preparación PAES para cursos completos: panel del profesor, avance de cada estudiante, ensayos programados y el curso por eje del temario. Cotización con factura y orden de compra.",
  alternates: { canonical: "/colegios" },
};

/** Lo mismo que anuncia la página de planes. Una sola verdad sobre el precio. */
const PRECIO = "$19.900";
const PERIODO = "por estudiante al año";

const INCLUYE = [
  {
    titulo: "Plan Pro para cada estudiante del curso",
    detalle:
      "Las cinco pruebas, ensayos a medida, las 95 lecciones y el puntaje con las tablas oficiales del DEMRE.",
  },
  {
    titulo: "Un código de seis caracteres",
    detalle:
      "Cada alumno entra con su propia cuenta y se suma al curso. El profesor no crea cuentas ajenas ni maneja contraseñas de menores.",
  },
  {
    titulo: "Panel del profesor",
    detalle: "El avance de cada estudiante: qué rindió, cuánto sacó y cuándo.",
  },
  {
    titulo: "El curso por eje del temario",
    detalle: "En qué están fallando todos, para saber qué repasar en clases.",
  },
  {
    titulo: "Ensayos programados",
    detalle:
      "Dejas un ensayo agendado para una fecha y ves quién lo rindió. No bloquea ni cierra a una hora exacta: aparece como tarea y queda la lista de quién cumplió.",
  },
];

const PASOS = [
  {
    numero: 1,
    titulo: "Pides la cotización",
    detalle:
      "Con el formulario de abajo. Te responde una persona dentro de un día hábil, con la cotización formal.",
  },
  {
    numero: 2,
    titulo: "El colegio paga con factura",
    detalle:
      "Contra orden de compra, como compra cualquier establecimiento. No se necesita tarjeta de crédito.",
  },
  {
    numero: 3,
    titulo: "Creas el curso y dictas el código",
    detalle:
      "Seis caracteres que escribes en la pizarra. Cada alumno crea su cuenta y se suma; desde ahí tienen el plan Pro todo el periodo contratado.",
  },
];

export default function ColegiosPage() {
  return (
    <>
      <main>
        <section className="hero-glow relative overflow-hidden px-6 pt-16 pb-14">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-xs font-semibold tracking-wide text-accent uppercase">
              Plan Colegios
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
              Prepara la PAES con tu curso completo
            </h1>
            <p className="mx-auto mt-4 max-w-xl text-muted">
              Cada estudiante con el plan Pro, y tú con el panel para ver cómo
              va cada uno y qué le conviene repasar al curso.
            </p>
            <div className="mt-8 inline-flex flex-col items-center rounded-xl border border-border bg-surface px-6 py-4">
              <p className="text-3xl font-semibold tracking-tight">{PRECIO}</p>
              <p className="text-sm text-muted">{PERIODO}</p>
              <p className="mt-2 text-xs text-muted">
                Desde un curso (30 estudiantes). Sobre 200, conversemos.
              </p>
            </div>
            <p className="mt-6 text-sm">
              <a href="#cotizacion" className="font-medium text-accent hover:underline">
                Pedir una cotización
              </a>
            </p>
          </div>
        </section>

        <section className="border-t border-border px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-semibold tracking-tight">Qué incluye</h2>
            <ul className="mt-6 flex flex-col gap-4">
              {INCLUYE.map((item) => (
                <li
                  key={item.titulo}
                  className="rounded-xl border border-border bg-surface/50 p-4"
                >
                  <p className="font-medium">{item.titulo}</p>
                  <p className="mt-1 text-sm text-muted">{item.detalle}</p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="border-t border-border bg-surface/50 px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-semibold tracking-tight">Cómo funciona</h2>
            <ol className="mt-6 flex flex-col gap-5">
              {PASOS.map((paso) => (
                <li key={paso.numero} className="flex gap-4">
                  <span
                    aria-hidden
                    className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent/10 text-sm font-bold text-accent"
                  >
                    {paso.numero}
                  </span>
                  <span>
                    <span className="block font-medium">{paso.titulo}</span>
                    <span className="mt-1 block text-sm text-muted">{paso.detalle}</span>
                  </span>
                </li>
              ))}
            </ol>

            {/* Esto lo pregunta el sostenedor, no el profesor, y es la pregunta
                que detiene una compra si no está contestada por escrito. */}
            <div className="mt-8 rounded-xl border border-border bg-background p-5">
              <p className="font-medium">Sobre los datos de los estudiantes</p>
              <p className="mt-2 text-sm text-muted">
                Cada estudiante crea su propia cuenta y su historial le
                pertenece: si se cambia de colegio, se lleva su avance. El
                profesor ve el rendimiento académico de quienes están en su
                curso, y nada más. Al contratar, el establecimiento confirma
                que cuenta con la autorización de los apoderados para que sus
                estudiantes usen la plataforma. Puedes revisar la{" "}
                <Link href="/privacidad" className="text-accent hover:underline">
                  política de privacidad
                </Link>{" "}
                completa.
              </p>
            </div>
          </div>
        </section>

        <section id="cotizacion" className="border-t border-border px-6 py-16">
          <div className="mx-auto max-w-2xl">
            <h2 className="text-2xl font-semibold tracking-tight">Pide tu cotización</h2>
            <p className="mt-2 mb-8 text-sm text-muted">
              Sin compromiso y sin crear cuenta. Te llega la cotización formal
              con los datos para la factura y la orden de compra.
            </p>
            <FormularioCotizacion />
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
