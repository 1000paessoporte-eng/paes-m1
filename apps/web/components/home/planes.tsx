/**
 * Planes de pago. Todavía no hay precios decididos, así que se muestran como
 * anticipo: poner cifras que después cambien sería prometer algo que no está
 * definido. Cada plan sí declara su duración y su periodo de cobro.
 */

const PLANES = [
  {
    nombre: "Gratis",
    resumen: "Para partir hoy",
    precio: "Sin costo",
    facturacion: "No requiere tarjeta",
    duracion: "Acceso permanente",
    incluye: [
      "Ensayos con el banco de preguntas actual",
      "Puntaje PAES estimado y resolución de cada ejercicio",
      "Historial de tu progreso con gráfico de evolución",
      "Árbol de habilidades completo",
    ],
    destacado: false,
    disponible: true,
  },
  {
    nombre: "Pro",
    resumen: "Para preparar en serio",
    precio: "Precio por definir",
    facturacion: "Mensual o anual",
    duracion: "Mientras la suscripción esté activa",
    incluye: [
      "Todo lo del plan Gratis",
      "Banco de preguntas ampliado y actualizado cada mes",
      "Recomendación automática de qué nodo reforzar",
      "Ensayos ilimitados filtrados por eje temático",
      "Comparación de tu puntaje entre ensayos y por eje",
    ],
    destacado: true,
    disponible: false,
  },
  {
    nombre: "Colegios",
    resumen: "Para cursos completos",
    precio: "Precio por definir",
    facturacion: "Por semestre o año escolar",
    duracion: "Todo el periodo contratado",
    incluye: [
      "Todo lo del plan Pro para cada estudiante",
      "Cuentas para el curso completo",
      "Panel del profesor con el avance de cada alumno",
      "Informes por estudiante, por curso y por eje temático",
      "Ensayos programados con fecha y hora de aplicación",
    ],
    destacado: false,
    disponible: false,
  },
] as const;

export function Planes() {
  return (
    <section id="planes" className="border-t border-border px-6 py-20">
      <div className="mx-auto max-w-5xl">
        <div className="mx-auto max-w-lg text-center">
          <span className="rounded-full border border-accent/40 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
            Próximamente
          </span>
          <h2 className="mt-4 text-2xl font-semibold tracking-tight sm:text-3xl">
            Planes
          </h2>
          <p className="mt-3 text-sm text-muted">
            Hoy todo lo que ves está disponible sin costo. Estos son los planes
            que vienen; los precios se anunciarán acá mismo.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {PLANES.map((plan) => (
            <div
              key={plan.nombre}
              className={
                plan.destacado
                  ? "flex flex-col rounded-xl border border-accent/50 bg-accent/5 p-6"
                  : "flex flex-col rounded-xl border border-border bg-surface p-6"
              }
            >
              <div className="flex items-baseline justify-between gap-2">
                <h3 className="text-base font-semibold">{plan.nombre}</h3>
                {plan.destacado && (
                  <span className="rounded-full bg-accent px-2 py-0.5 text-[11px] font-medium text-accent-foreground">
                    Recomendado
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-muted">{plan.resumen}</p>

              <p
                className={
                  plan.disponible
                    ? "mt-4 text-2xl font-bold tracking-tight text-success"
                    : "mt-4 text-2xl font-bold tracking-tight text-muted"
                }
              >
                {plan.precio}
              </p>

              <dl className="mt-4 flex flex-col gap-1.5 border-y border-border py-3 text-xs">
                <div className="flex justify-between gap-2">
                  <dt className="text-muted">Cobro</dt>
                  <dd className="text-right font-medium">{plan.facturacion}</dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt className="text-muted">Duración</dt>
                  <dd className="text-right font-medium">{plan.duracion}</dd>
                </div>
              </dl>

              <ul className="mt-4 flex flex-1 flex-col gap-2 text-sm text-muted">
                {plan.incluye.map((item) => (
                  <li key={item} className="flex gap-2">
                    <span aria-hidden className="text-accent">
                      ✓
                    </span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>

              <button
                type="button"
                disabled
                className="mt-6 w-full cursor-not-allowed rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-muted"
              >
                {plan.disponible ? "Es el plan actual" : "Disponible pronto"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
