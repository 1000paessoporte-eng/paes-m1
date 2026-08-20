import type { Diagnostico } from "@/lib/api";

/**
 * El ritmo del alumno contra el que exige la prueba oficial.
 *
 * En la PAES mucha gente no falla por no saber: falla porque no alcanza. Es lo
 * único del examen que nadie entrena, y el dato para medirlo --los segundos
 * que tarda en cada pregunta-- ya se estaba guardando.
 *
 * La proyección de preguntas sin alcanzar viene del servidor y llega en null
 * cuando no hay datos que la sostengan. Acá no se calcula nada: si el servidor
 * calla, la tarjeta calla.
 */
export function DiagnosticoRitmo({ ritmo }: { ritmo: NonNullable<Diagnostico["ritmo"]> }) {
  const vaLento = ritmo.segundos_alumno != null && ritmo.segundos_alumno > ritmo.segundos_oficiales;
  const masLento = ritmo.por_eje[0];

  return (
    <section className="mt-6">
      <h2 className="mb-1 text-sm font-semibold tracking-wide text-muted uppercase">
        Tu ritmo
      </h2>
      <p className="mb-3 text-xs leading-relaxed text-muted">
        Sobre {ritmo.respuestas_medidas} preguntas cronometradas.
      </p>

      <div className="rounded-xl border border-border bg-surface p-5">
        <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2">
          <div>
            <p className="text-2xl font-bold tabular-nums text-foreground">
              {ritmo.segundos_alumno}s
            </p>
            <p className="text-xs text-muted">te demoras por pregunta</p>
          </div>
          <div>
            <p className="text-2xl font-bold tabular-nums text-muted">
              {ritmo.segundos_oficiales}s
            </p>
            <p className="text-xs text-muted">te da la prueba real</p>
          </div>
        </div>

        {ritmo.preguntas_sin_alcanzar != null && (
          <p
            className={
              "mt-4 rounded-lg px-4 py-3 text-sm leading-relaxed " +
              (ritmo.preguntas_sin_alcanzar > 0
                ? "bg-accent-warm/10 text-accent-warm-strong"
                : "bg-success/10 text-success")
            }
          >
            {ritmo.preguntas_sin_alcanzar > 0 ? (
              <>
                A este ritmo dejarías{" "}
                <strong className="tabular-nums">{ritmo.preguntas_sin_alcanzar}</strong>{" "}
                preguntas sin responder en la prueba real. En la PAES las
                incorrectas no descuentan, así que cada una que no alcanzas es
                un punto que regalas.
              </>
            ) : (
              <>Vas a tiempo: alcanzarías a responder la prueba completa.</>
            )}
          </p>
        )}

        {ritmo.por_eje.length > 0 && (
          <>
            <h3 className="mt-5 text-xs font-semibold text-foreground">
              Dónde se te va el tiempo
            </h3>
            <ul className="mt-2 flex flex-col gap-1.5">
              {ritmo.por_eje.map((eje) => (
                <li key={eje.axis_label} className="flex items-baseline justify-between gap-3 text-sm">
                  <span className="text-muted">{eje.axis_label}</span>
                  <span className="tabular-nums text-foreground">
                    {eje.segundos_por_pregunta}s
                  </span>
                </li>
              ))}
            </ul>
            {vaLento && masLento && (
              <p className="mt-3 text-xs leading-relaxed text-muted">
                Lo más caro es <strong className="text-foreground">{masLento.axis_label}</strong>.
                Practicar ese eje suelto es lo que más tiempo te devuelve.
              </p>
            )}
          </>
        )}
      </div>
    </section>
  );
}
