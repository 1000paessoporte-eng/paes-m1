import Link from "next/link";
import type { RepasoResumen } from "@/lib/api";

const FECHA = new Intl.DateTimeFormat("es-CL", { day: "numeric", month: "long" });

/**
 * Lo que le toca repasar hoy.
 *
 * Es la única tarjeta del panel que propone una tarea CERRADA: las demás
 * llevan a decisiones ("elige un ensayo", "elige un nodo") y esta dice
 * exactamente cuántas preguntas y cuáles. Es lo que la hace servible los días
 * en que el alumno tiene quince minutos y ninguna gana de decidir nada.
 */
export function RepasoModulo({ resumen }: { resumen: RepasoResumen }) {
  const hoy = resumen.pendientes_hoy;

  return (
    <section className="card-panel p-6" aria-labelledby="h-repaso">
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="h-repaso" className="font-semibold tracking-tight">
          Repaso inteligente
        </h2>
        {resumen.dominadas > 0 && (
          <span className="text-xs text-muted">
            {resumen.dominadas} {resumen.dominadas === 1 ? "dominada" : "dominadas"}
          </span>
        )}
      </div>

      {hoy > 0 ? (
        <>
          <p className="mt-3 text-4xl leading-none font-bold">
            {hoy}
            <span className="ml-2 align-middle text-sm font-medium text-muted">
              {hoy === 1 ? "pregunta para hoy" : "preguntas para hoy"}
            </span>
          </p>
          <p className="mt-2 text-sm text-muted">
            Son preguntas que ya fallaste. Vuelven con esperas cada vez más largas
            hasta que te salgan sin pensarlo.
          </p>
          <Link
            href="/repaso"
            className="mt-4 inline-block rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-accent-foreground hover:opacity-90"
          >
            Repasar ahora
          </Link>
        </>
      ) : resumen.en_repaso > 0 ? (
        <>
          <p className="mt-3 text-sm text-muted">
            Hoy no te toca nada: vas al día con las{" "}
            <strong className="text-foreground">{resumen.en_repaso}</strong> preguntas
            que tienes en repaso.
            {resumen.proxima_fecha && (
              <>
                {" "}
                La próxima vuelve el{" "}
                {FECHA.format(new Date(`${resumen.proxima_fecha}T12:00:00`))}.
              </>
            )}
          </p>
        </>
      ) : (
        <p className="mt-3 text-sm text-muted">
          Acá van a volver las preguntas que falles, hasta que las domines. Todavía
          no tienes ninguna: rinde un ensayo y las que se te escapen aparecen acá.
        </p>
      )}
    </section>
  );
}
