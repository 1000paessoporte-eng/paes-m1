import Link from "next/link";
import type { ContentStats } from "@/lib/api";
import { Reveal } from "@/components/motion/reveal";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { BarraProgreso } from "@/components/ui/barra-progreso";

/**
 * Lo que pasa cuando terminas un ensayo, mostrado en vez de contado.
 *
 * Reemplaza dos secciones que eran exactamente el relleno que se ve en
 * cualquier página: tres pasos numerados ("armas / rindes / mejoras") y seis
 * tarjetas idénticas con un ícono y dos líneas cada una. Nadie lee seis
 * tarjetas iguales, y ninguna mostraba el producto.
 *
 * Acá cada bloque enseña una pantalla real, con el tamaño que le corresponde
 * a su importancia: el puntaje ocupa el doble que los demás porque es lo que
 * la persona vino a buscar, y el resto se reparte parejo. La grilla cierra en
 * 4+2 y 2+2+2, sin huecos: un bento con una celda vacía se lee como un error
 * de carga, no como aire.
 *
 * Los números que ilustran van marcados como ejemplo. Los del banco son
 * reales y salen de la API.
 */
export function BentoProducto({ stats }: { stats: ContentStats | null }) {
  return (
    <section className="border-t border-border px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-2xl">
          <p className="text-xs font-medium tracking-wide text-muted uppercase">
            Al terminar el ensayo
          </p>
          <h2 className="font-display mt-2 text-3xl font-bold tracking-tight text-balance sm:text-4xl">
            No te decimos cuánto sacaste.
            <br />
            Te decimos qué hacer con eso.
          </h2>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
          {/* ── Puntaje: el bloque grande ────────────────────────────── */}
          <Reveal delay={0.0} className="sm:col-span-2 lg:col-span-4">
            <article className="rounded-2xl border border-border bg-surface p-6 h-full">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="font-semibold">Tu puntaje en la escala real</h3>
              <span className="rounded-full bg-surface-hover px-2 py-0.5 text-[11px] text-muted">
                Ejemplo
              </span>
            </div>
            <p className="mt-1 text-sm text-muted">
              De 100 a 1000, con las tablas de transformación oficiales del DEMRE.
              No es un porcentaje disfrazado de puntaje.
            </p>

            {/* La escala, dibujada: es el rango que el alumno conoce de memoria
                y verlo entero ubica su resultado sin explicar nada. */}
            <div className="mt-6">
              <BarraProgreso
                porcentaje={75.5}
                color="var(--prueba-m1)"
                etiqueta="Puntaje 780 sobre la escala de 100 a 1000"
              />
              <div className="mt-2 flex justify-between text-[11px] text-muted tabular-nums">
                <span>100</span>
                <span>1000</span>
              </div>
            </div>

            <div className="mt-5 flex flex-wrap items-end gap-x-8 gap-y-4">
              <div>
                <p className="font-display text-5xl leading-none font-bold">
                  <NumeroAnimado valor={780} duracion={1.1} />
                </p>
                <p className="mt-1 text-xs text-muted">Puntaje estimado</p>
              </div>
              <div>
                <p className="font-display text-2xl leading-none font-semibold text-success">
                  <NumeroAnimado valor={38} duracion={0.9} />
                </p>
                <p className="mt-1 text-xs text-muted">vs. tu ensayo anterior</p>
              </div>
              <div>
                <p className="font-display text-2xl leading-none font-semibold">
                  1 h 37
                </p>
                <p className="mt-1 text-xs text-muted">de 2 h 20 disponibles</p>
              </div>
            </div>
            </article>
          </Reveal>

          {/* ── El porqué del error: la columna alta ─────────────────── */}
          <Reveal delay={0.07} className="sm:col-span-2 lg:col-span-2">
            <article className="rounded-2xl border border-accent-warm/30 bg-accent-warm/5 p-6 h-full">
            <h3 className="font-semibold">Por qué te equivocaste</h3>
            <p className="mt-1 text-sm text-muted">
              No «fallaste geometría». El razonamiento exacto que te llevó a la
              alternativa incorrecta, escrito pregunta por pregunta.
            </p>

            <div className="mt-5 space-y-3">
              {[
                "Sumó los exponentes en vez de multiplicarlos.",
                "Interpretó «aumentado» como una resta.",
                "Dio la hipotenusa, que era un paso intermedio y no lo que se pedía.",
              ].map((error) => (
                <p
                  key={error}
                  className="border-l-2 border-accent-warm pl-3 text-sm leading-relaxed"
                >
                  {error}
                </p>
              ))}
            </div>

            <p className="mt-5 text-xs text-muted">
              Están escritos para{" "}
              <strong className="text-accent-warm-strong">
                cada alternativa incorrecta del banco
              </strong>
              , no para las preguntas en general.
            </p>
            </article>
          </Reveal>

          {/* ── Árbol ─────────────────────────────────────────────────── */}
          <Reveal delay={0.14} className="sm:col-span-1 lg:col-span-2">
            <article className="rounded-2xl border border-border bg-surface p-6 h-full">
            <h3 className="font-semibold">Qué estudiar después</h3>
            <p className="mt-1 text-sm text-muted">
              {stats
                ? `Los ${stats.skill_nodes} temas del temario, en orden.`
                : "El temario completo, en orden."}{" "}
              Cada uno se abre cuando dominas el anterior.
            </p>
            <ul className="mt-4 space-y-2.5">
              {[
                { nombre: "Números racionales", estado: "dominado" },
                { nombre: "Porcentajes", estado: "ahora" },
                { nombre: "Ecuación cuadrática", estado: "bloqueado" },
              ].map((n) => (
                <li key={n.nombre} className="flex items-center gap-2.5 text-sm">
                  <span
                    className={
                      n.estado === "dominado"
                        ? "h-2.5 w-2.5 shrink-0 rounded-full bg-success"
                        : n.estado === "ahora"
                          ? "h-2.5 w-2.5 shrink-0 rounded-full bg-accent-warm"
                          : "h-2.5 w-2.5 shrink-0 rounded-full border border-border-strong"
                    }
                  />
                  <span className={n.estado === "bloqueado" ? "text-muted" : ""}>
                    {n.nombre}
                  </span>
                  {n.estado === "ahora" && (
                    <span className="ml-auto text-[11px] font-semibold text-accent-warm-strong">
                      sigue por acá
                    </span>
                  )}
                </li>
              ))}
            </ul>
            </article>
          </Reveal>

          {/* ── Ritmo ─────────────────────────────────────────────────── */}
          <Reveal delay={0.21} className="sm:col-span-1 lg:col-span-2">
            <article className="rounded-2xl border border-border bg-surface p-6 h-full">
            <h3 className="font-semibold">Si te va a alcanzar el tiempo</h3>
            <p className="mt-1 text-sm text-muted">
              En la PAES mucha gente no falla por no saber: falla porque no
              alcanza. Se mide desde la primera pregunta.
            </p>
            <div className="mt-4 flex items-end gap-6">
              <div>
                <p className="font-display text-3xl leading-none font-bold tabular-nums">
                  55,9<span className="text-base font-semibold">s</span>
                </p>
                <p className="mt-1 text-xs text-muted">te demoras</p>
              </div>
              <div>
                <p className="font-display text-3xl leading-none font-bold text-muted tabular-nums">
                  129<span className="text-base font-semibold">s</span>
                </p>
                <p className="mt-1 text-xs text-muted">te da la prueba</p>
              </div>
            </div>
            </article>
          </Reveal>

          {/* ── Carrera ───────────────────────────────────────────────── */}
          <Reveal delay={0.28} className="sm:col-span-2 lg:col-span-2">
            <article className="rounded-2xl border border-border bg-surface p-6 h-full">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <h3 className="font-semibold">Cuánto te falta para tu carrera</h3>
                <p className="mt-1 max-w-md text-sm text-muted">
                  Cada carrera pondera las pruebas distinto. Eliges hasta diez
                  preferencias y la plataforma te dice dónde rinde más cada hora
                  de estudio.
                </p>
              </div>
              <Link href="/carreras" className="text-accent shrink-0 text-sm font-medium">
                Ver las carreras
              </Link>
            </div>
            <div className="mt-5 space-y-3">
              {[
                { carrera: "Medicina", uni: "U. de Chile", falta: "faltan 47 pts", ok: false },
                { carrera: "Ingeniería Civil", uni: "PUC", falta: "alcanzas", ok: true },
              ].map((c) => (
                <div
                  key={c.carrera}
                  className="flex flex-wrap items-baseline justify-between gap-2 border-b border-border pb-3 last:border-0 last:pb-0"
                >
                  <span className="text-sm font-medium">
                    {c.carrera}{" "}
                    <span className="font-normal text-muted">· {c.uni}</span>
                  </span>
                  <span
                    className={
                      c.ok
                        ? "text-sm font-semibold text-success"
                        : "text-sm font-semibold text-muted"
                    }
                  >
                    {c.falta}
                  </span>
                </div>
              ))}
            </div>
            </article>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
