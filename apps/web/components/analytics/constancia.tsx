interface Dia {
  date: string;
  questions_answered: number;
  minutes_practiced: number;
}

const DIA_FMT = new Intl.DateTimeFormat("es-CL", { weekday: "narrow" });
const FECHA_LARGA = new Intl.DateTimeFormat("es-CL", { day: "numeric", month: "long" });

/**
 * Las últimas dos semanas, día por día, y las rachas.
 *
 * Los dos gráficos de esta pantalla responden "cuánto rindes"; ninguno
 * respondía "cuántos días apareciste", que es lo que de verdad separa a quien
 * llega preparado a diciembre. Y es la única métrica de la página que no
 * depende de acertar: un día malo suma igual, que es justo el mensaje.
 *
 * La racha se muestra junto a la MEJOR racha a propósito. La actual castiga
 * para siempre a quien se enfermó un martes; ver que alguna vez llegó a nueve
 * días es lo que hace que valga la pena empezar la siguiente.
 */
export function Constancia({
  dias,
  rachaActual,
  mejorRacha,
  diasActivos,
}: {
  dias: Dia[];
  rachaActual: number;
  mejorRacha: number;
  diasActivos: number;
}) {
  const activos = dias.filter((d) => d.questions_answered > 0).length;
  const maxMinutos = Math.max(...dias.map((d) => d.minutes_practiced), 1);

  return (
    <section className="rounded-xl border border-border bg-surface p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h2 className="text-sm font-semibold">Tu constancia</h2>
        <p className="text-xs text-muted">
          {diasActivos} {diasActivos === 1 ? "día" : "días"} de estudio en total
        </p>
      </div>

      <div className="mt-4 flex items-end gap-6">
        <div>
          <p className="text-4xl leading-none font-bold text-accent-warm-strong">
            {rachaActual}
          </p>
          <p className="mt-1 text-xs text-muted">
            {rachaActual === 1 ? "día seguido" : "días seguidos"}
          </p>
        </div>
        <div>
          <p className="text-2xl leading-none font-semibold text-muted">{mejorRacha}</p>
          <p className="mt-1 text-xs text-muted">tu mejor racha</p>
        </div>
      </div>

      {/* Una sola tonalidad: los días no son categorías distintas, es la misma
          medida --cuánto practicaste-- con más o menos intensidad. Pintarlos de
          colores distintos inventaría una diferencia de tipo que no existe. */}
      <ul className="mt-5 flex gap-1.5" aria-label="Últimos 14 días">
        {dias.map((d) => {
          const fecha = new Date(`${d.date}T12:00:00`);
          const practico = d.questions_answered > 0;
          const intensidad = practico
            ? 0.35 + 0.65 * Math.min(1, d.minutes_practiced / maxMinutos)
            : 0;
          return (
            <li key={d.date} className="flex flex-1 flex-col items-center gap-1">
              <div
                className="h-8 w-full rounded-md border border-border"
                style={{
                  backgroundColor: practico
                    ? `color-mix(in srgb, var(--accent) ${Math.round(intensidad * 100)}%, transparent)`
                    : "var(--surface-hover)",
                }}
                title={
                  practico
                    ? `${FECHA_LARGA.format(fecha)}: ${d.questions_answered} preguntas`
                    : `${FECHA_LARGA.format(fecha)}: no practicaste`
                }
              />
              <span className="text-[10px] text-muted" suppressHydrationWarning>
                {DIA_FMT.format(fecha)}
              </span>
            </li>
          );
        })}
      </ul>

      <p className="mt-3 text-sm text-muted">
        Practicaste <strong className="text-foreground">{activos} de los últimos 14 días</strong>
        {activos >= 10
          ? ". Así se llega a diciembre."
          : activos >= 5
            ? ". Un día más esta semana y la semana cambia de cara."
            : ". Media hora hoy ya mueve esta fila."}
      </p>
    </section>
  );
}
