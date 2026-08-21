"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import type { Carrera, Meta, Postulacion } from "@/lib/api";
import {
  agregarPostulacion,
  buscarCarreras,
  guardarNotas,
  quitarPostulacion,
  reordenarPostulaciones,
} from "@/lib/api";
import { getClientToken } from "@/lib/auth";
import { BarraProgreso } from "@/components/ui/barra-progreso";
import { NumeroAnimado } from "@/components/motion/numero-animado";

/**
 * Mi meta: la lista de postulación y qué falta para cada preferencia.
 *
 * En Chile no se postula a una carrera: se postulan hasta diez en orden de
 * preferencia, y ese orden decide dónde queda uno. La pregunta que responde
 * esta pantalla no es "¿alcanzo para esta?" sino "¿hasta qué preferencia
 * alcanzo, y qué hago con lo que falta?".
 */

/**
 * Cuántas preferencias admite el sistema de admisión chileno. NO es el tope
 * del usuario: el suyo depende de su plan y llega por props.
 */
const MAX_SISTEMA = 10;

function token() {
  return getClientToken() ?? undefined;
}

export function MetaView({
  inicial,
  tope = MAX_SISTEMA,
}: {
  inicial: Meta;
  /**
   * Cuántas carreras admite SU plan. Venía fijo en 10 y el plan Gratis permite
   * una: el alumno agregaba la primera, apretaba "Agregar carrera" otra vez y
   * se comía un 409 sin explicación después de haber buscado la carrera.
   */
  tope?: number;
}) {
  const [meta, setMeta] = useState<Meta>(inicial);
  const [agregando, setAgregando] = useState(inicial.postulaciones.length === 0);

  const alcanzadas = meta.postulaciones.filter((p) => p.alcanza === true).length;
  const enElTope = meta.postulaciones.length >= tope;

  return (
    <div className="mx-auto w-full max-w-3xl">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-medium tracking-wide text-accent uppercase">Mi meta</p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl">
            Mi lista de postulación
          </h1>
          <p className="mt-1 text-sm text-muted">
            {meta.postulaciones.length === 0
              ? tope === 1
                ? "Agrega la carrera que quieres y mira cuánto te falta."
                : `Agrega hasta ${tope} carreras en el orden que las quieres.`
              : `${meta.postulaciones.length} de ${tope} ${tope === 1 ? "preferencia" : "preferencias"} · ${alcanzadas} con el mínimo alcanzado`}
          </p>
        </div>
        {!agregando && !enElTope && (
          <button
            type="button"
            onClick={() => setAgregando(true)}
            className="btn-glow rounded-lg px-4 py-2 text-sm font-semibold text-accent-foreground"
          >
            Agregar carrera
          </button>
        )}
      </header>

      {/* En el tope y con plan Gratis, el botón "Agregar carrera" desaparecía
          sin decir por qué. Desaparecer sin explicación se lee como que algo
          se rompió; esto dice cuál es el límite y qué lo levanta. */}
      {enElTope && tope < MAX_SISTEMA && (
        <p className="mt-4 rounded-xl border border-border bg-surface px-4 py-3 text-sm text-muted">
          Tu plan incluye{" "}
          {tope === 1 ? "una carrera" : `${tope} carreras`} en Mi meta. Con Pro
          armas la lista completa de hasta {MAX_SISTEMA} preferencias y las
          comparas entre sí.{" "}
          <Link href="/planes" className="font-medium text-accent hover:underline">
            Ver planes
          </Link>
        </p>
      )}

      {agregando && (
        <Buscador
          yaElegidas={meta.postulaciones.map((p) => p.carrera.id)}
          onAgregada={(m) => {
            setMeta(m);
            setAgregando(false);
          }}
          onCerrar={meta.postulaciones.length > 0 ? () => setAgregando(false) : undefined}
        />
      )}

      <Notas meta={meta} onGuardado={setMeta} />

      {meta.postulaciones.length > 0 && (
        <>
          <Proyeccion meta={meta} />
          <Simulador meta={meta} />

          <section className="mt-8" aria-labelledby="h-lista">
            <h2 id="h-lista" className="font-semibold tracking-tight">
              Tus preferencias
            </h2>
            <ol className="mt-4 flex flex-col gap-3">
              {meta.postulaciones.map((p, i) => (
                <Fila
                  key={p.carrera.id}
                  p={p}
                  esPrimera={i === 0}
                  esUltima={i === meta.postulaciones.length - 1}
                  onSubir={async () => {
                    const ids = meta.postulaciones.map((x) => x.carrera.id);
                    [ids[i - 1], ids[i]] = [ids[i], ids[i - 1]];
                    setMeta(await reordenarPostulaciones(ids, token()));
                  }}
                  onBajar={async () => {
                    const ids = meta.postulaciones.map((x) => x.carrera.id);
                    [ids[i], ids[i + 1]] = [ids[i + 1], ids[i]];
                    setMeta(await reordenarPostulaciones(ids, token()));
                  }}
                  onQuitar={async () =>
                    setMeta(await quitarPostulacion(p.carrera.id, token()))
                  }
                />
              ))}
            </ol>
          </section>

          <Plan meta={meta} />
        </>
      )}
    </div>
  );
}

/* ── Buscar y agregar ─────────────────────────────────────────────────── */

function Buscador({
  yaElegidas,
  onAgregada,
  onCerrar,
}: {
  yaElegidas: number[];
  onAgregada: (m: Meta) => void;
  onCerrar?: () => void;
}) {
  const [texto, setTexto] = useState("");
  const [resultados, setResultados] = useState<Carrera[] | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    if (texto.trim().length < 3) return;
    setCargando(true);
    setError(null);
    try {
      setResultados(await buscarCarreras(texto, token()));
    } catch {
      setError("No se pudo buscar. Intenta de nuevo.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <section className="card-panel mt-6 p-5">
      <form onSubmit={buscar} className="flex gap-2">
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Ingeniería civil, enfermería concepción…"
          aria-label="Buscar carrera o universidad"
          className="min-w-0 flex-1 rounded-lg border border-border bg-background px-4 py-2.5 text-sm"
        />
        <button
          type="submit"
          disabled={texto.trim().length < 3 || cargando}
          className="btn-glow shrink-0 rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground disabled:opacity-50"
        >
          {cargando ? "Buscando…" : "Buscar"}
        </button>
        {onCerrar && (
          <button
            type="button"
            onClick={onCerrar}
            className="shrink-0 rounded-lg border border-border px-3 text-sm hover:bg-surface-hover"
          >
            Cerrar
          </button>
        )}
      </form>

      {error && <p className="mt-3 text-sm text-danger">{error}</p>}

      {resultados?.length === 0 && (
        <p className="mt-4 text-sm text-muted">
          Sin resultados. Son 1.855 carreras del proceso 2026; unas pocas quedaron
          fuera porque su fila en el documento oficial no se pudo leer con
          seguridad.
        </p>
      )}

      {resultados && resultados.length > 0 && (
        <ul className="mt-4 flex max-h-96 flex-col gap-2 overflow-y-auto">
          {resultados.map((c) => {
            const ya = yaElegidas.includes(c.id);
            return (
              <li key={c.id}>
                <button
                  type="button"
                  disabled={ya}
                  onClick={async () => onAgregada(await agregarPostulacion(c.id, token()))}
                  className="w-full rounded-xl border border-border bg-surface p-3 text-left transition hover:border-border-strong disabled:opacity-50"
                >
                  <span className="block text-sm font-semibold">
                    {c.nombre}
                    {ya && <span className="text-xs text-muted"> · ya está</span>}
                  </span>
                  <span className="block text-xs text-muted">
                    {c.universidad} · {c.sede}
                  </span>
                  <span className="mt-1 block text-xs text-muted">
                    {c.vacantes ? `${c.vacantes} vacantes` : "Vacantes no informadas"}
                    {c.ponderado_min ? ` · mínimo ${c.ponderado_min} pts` : ""}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

/* ── Notas del colegio ────────────────────────────────────────────────── */

function Notas({ meta, onGuardado }: { meta: Meta; onGuardado: (m: Meta) => void }) {
  const [nem, setNem] = useState(meta.puntaje_nem?.toString() ?? "");
  const [ranking, setRanking] = useState(meta.puntaje_ranking?.toString() ?? "");
  const [guardado, setGuardado] = useState(false);

  const faltan = meta.puntaje_nem == null || meta.puntaje_ranking == null;

  return (
    <section className="card-panel mt-5 p-5">
      <h2 className="text-sm font-semibold tracking-tight">Tus notas</h2>
      <p className="mt-1 text-xs leading-relaxed text-muted">
        Los puntajes de NEM y ranking que vienen en tu informe, no el promedio de
        notas: esa conversión la hace el DEMRE y no la estimamos acá. Casi todas
        las carreras los ponderan, así que sin ellos el puntaje final no se puede
        calcular.
      </p>
      <div className="mt-3 flex flex-wrap items-end gap-3">
        <label className="text-sm">
          <span className="block text-xs text-muted">Puntaje NEM</span>
          <input
            inputMode="numeric"
            value={nem}
            onChange={(e) => setNem(e.target.value.replace(/\D/g, "").slice(0, 4))}
            placeholder="720"
            className="mt-1 w-28 rounded-lg border border-border bg-background px-3 py-2 tabular-nums"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-muted">Puntaje ranking</span>
          <input
            inputMode="numeric"
            value={ranking}
            onChange={(e) => setRanking(e.target.value.replace(/\D/g, "").slice(0, 4))}
            placeholder="780"
            className="mt-1 w-28 rounded-lg border border-border bg-background px-3 py-2 tabular-nums"
          />
        </label>
        <button
          type="button"
          onClick={async () => {
            onGuardado(
              await guardarNotas(
                {
                  puntaje_nem: nem ? Number(nem) : null,
                  puntaje_ranking: ranking ? Number(ranking) : null,
                },
                token()
              )
            );
            setGuardado(true);
          }}
          className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-surface-hover"
        >
          {guardado ? "Guardado" : "Guardar"}
        </button>
        {faltan && !guardado && (
          <span className="text-xs text-warning">Faltan tus notas</span>
        )}
      </div>
    </section>
  );
}

/* ── Proyección contra la fecha de la PAES ────────────────────────────── */

function Proyeccion({ meta }: { meta: Meta }) {
  const { proyeccion } = meta;
  if (proyeccion.dias_para_paes == null) return null;

  const sube = (proyeccion.puntos_por_mes ?? 0) > 0;

  return (
    <section className="card-panel mt-5 p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-semibold tracking-tight">Tu ritmo</h2>
        <span className="text-sm text-muted">
          Faltan{" "}
          <strong className="text-foreground tabular-nums">
            {proyeccion.dias_para_paes}
          </strong>{" "}
          días para la PAES
        </span>
      </div>

      {proyeccion.puntos_por_mes == null ? (
        <p className="mt-2 text-sm text-muted">
          Con {proyeccion.ensayos_considerados}{" "}
          {proyeccion.ensayos_considerados === 1 ? "ensayo" : "ensayos"} todavía no
          hay tendencia que valga: dos puntos son una recta, no un ritmo. Rinde al
          menos tres de la misma prueba.
        </p>
      ) : (
        <p className="mt-2 text-sm leading-relaxed">
          Vienes{" "}
          <strong className={sube ? "text-success" : "text-danger"}>
            {sube ? "subiendo" : "bajando"} {Math.abs(proyeccion.puntos_por_mes)} puntos
            al mes
          </strong>{" "}
          sobre {proyeccion.ensayos_considerados} ensayos. A este ritmo llegarías a{" "}
          <strong className="tabular-nums">{proyeccion.proyectado}</strong> en
          noviembre.
          <span className="mt-1 block text-xs text-muted">
            Es una recta trazada entre tu primer y último ensayo de esa prueba, no
            una promesa.
          </span>
        </p>
      )}
    </section>
  );
}

/* ── Simulador ────────────────────────────────────────────────────────── */

/**
 * "¿Y si subo M1 a 750?"
 *
 * Corre entero en el navegador: el ponderado es una suma de pesos por puntajes
 * y las ponderaciones ya vienen en el payload, así que no hace falta ida y
 * vuelta al servidor para responder cada movimiento del deslizador.
 */
function Simulador({ meta }: { meta: Meta }) {
  const pruebas = useMemo(() => {
    const vistos = new Map<string, { etiqueta: string; actual: number }>();
    for (const p of meta.postulaciones) {
      for (const a of p.aportes) {
        if (a.factor === "nem" || a.factor === "ranking") continue;
        if (!vistos.has(a.factor)) {
          vistos.set(a.factor, { etiqueta: a.etiqueta, actual: a.puntaje ?? 500 });
        }
      }
    }
    return [...vistos.entries()];
  }, [meta]);

  const [valores, setValores] = useState<Record<string, number>>(() =>
    Object.fromEntries(pruebas.map(([f, v]) => [f, v.actual]))
  );
  const [abierto, setAbierto] = useState(false);

  if (pruebas.length === 0) return null;

  function simular(p: Postulacion): number | null {
    let total = 0;
    for (const a of p.aportes) {
      const puntaje =
        a.factor === "nem" || a.factor === "ranking"
          ? a.puntaje
          : (valores[a.factor] ?? a.puntaje);
      if (puntaje == null) return null;
      total += (a.ponderacion * puntaje) / 100;
    }
    return Math.round(total * 10) / 10;
  }

  const alcanzadas = meta.postulaciones.filter((p) => {
    const s = simular(p);
    return s != null && p.carrera.ponderado_min != null && s >= p.carrera.ponderado_min;
  }).length;

  const conMinimo = meta.postulaciones.filter(
    (p) => p.carrera.ponderado_min != null
  ).length;

  return (
    <section className="card-panel mt-5 p-5">
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        aria-expanded={abierto}
        className="flex w-full items-center justify-between gap-3 text-left"
      >
        <span>
          <span className="block font-semibold tracking-tight">¿Y si mejoro?</span>
          <span className="block text-xs text-muted">
            Mueve los puntajes y mira qué preferencias alcanzarías
          </span>
        </span>
        <span className="text-muted" aria-hidden>
          {abierto ? "▲" : "▼"}
        </span>
      </button>

      {abierto && (
        <div className="mt-4">
          {pruebas.map(([factor, info]) => (
            <div key={factor} className="mb-4">
              <div className="flex items-baseline justify-between gap-3 text-sm">
                <span>{info.etiqueta}</span>
                <span className="tabular-nums">
                  <strong>{valores[factor]}</strong>
                  <span className="text-xs text-muted"> (hoy {info.actual})</span>
                </span>
              </div>
              <input
                type="range"
                min={100}
                max={1000}
                step={10}
                value={valores[factor]}
                aria-label={`Puntaje simulado de ${info.etiqueta}`}
                onChange={(e) =>
                  setValores((v) => ({ ...v, [factor]: Number(e.target.value) }))
                }
                className="mt-2 w-full accent-[var(--accent)]"
              />
            </div>
          ))}

          <p className="rounded-lg border border-accent/30 bg-accent/5 px-4 py-3 text-sm">
            Con esos puntajes alcanzarías el mínimo de{" "}
            <strong className="tabular-nums">{alcanzadas}</strong> de tus {conMinimo}{" "}
            preferencias que declaran uno.
            <span className="mt-1 block text-xs text-muted">
              El mínimo de postulación es la primera barrera, no el puntaje de
              corte: entrar depende además de cuántos postulen y de las vacantes.
            </span>
          </p>

          <ul className="mt-3 flex flex-col gap-1.5">
            {meta.postulaciones.map((p) => {
              const s = simular(p);
              const min = p.carrera.ponderado_min;
              return (
                <li
                  key={p.carrera.id}
                  className="flex items-baseline justify-between gap-3 text-xs"
                >
                  <span className="min-w-0 truncate text-muted">
                    {p.preferencia}. {p.carrera.nombre}
                  </span>
                  <span className="shrink-0 tabular-nums">
                    {s ?? "—"}
                    {min != null && (
                      <span
                        className={s != null && s >= min ? "text-success" : "text-muted"}
                      >
                        {" "}
                        / {min}
                      </span>
                    )}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </section>
  );
}

/* ── Una preferencia ──────────────────────────────────────────────────── */

function Fila({
  p,
  esPrimera,
  esUltima,
  onSubir,
  onBajar,
  onQuitar,
}: {
  p: Postulacion;
  esPrimera: boolean;
  esUltima: boolean;
  onSubir: () => void;
  onBajar: () => void;
  onQuitar: () => void;
}) {
  const quieto = useReducedMotion();
  const min = p.carrera.ponderado_min;

  return (
    <motion.li layout={!quieto} className="card-panel p-4">
      <div className="flex items-start gap-3">
        <span
          className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-surface-hover text-sm font-bold tabular-nums"
          aria-label={`Preferencia ${p.preferencia}`}
        >
          {p.preferencia}
        </span>

        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold">{p.carrera.nombre}</p>
          <p className="text-xs text-muted">
            {p.carrera.universidad} · {p.carrera.sede}
            {p.carrera.vacantes ? ` · ${p.carrera.vacantes} vacantes` : ""}
          </p>

          {p.ponderado != null ? (
            <div className="mt-3">
              <div className="flex items-baseline justify-between gap-3">
                <span className="text-2xl font-bold tabular-nums">
                  <NumeroAnimado valor={Math.round(p.ponderado)} />
                </span>
                {min != null ? (
                  <span
                    className={
                      "rounded-full px-2.5 py-0.5 text-xs font-semibold " +
                      (p.alcanza
                        ? "bg-success/10 text-success"
                        : "bg-warning/10 text-warning")
                    }
                  >
                    {p.alcanza ? "Alcanzas el mínimo" : `Te faltan ${p.brecha} pts`}
                  </span>
                ) : (
                  <span className="text-xs text-muted">Sin mínimo publicado</span>
                )}
              </div>
              {min != null && (
                <div className="mt-2">
                  <BarraProgreso
                    porcentaje={Math.min(100, (p.ponderado / min) * 100)}
                    color={p.alcanza ? "var(--success)" : "var(--accent)"}
                    etiqueta={`${p.carrera.nombre}: ${p.ponderado} de ${min}`}
                    alto="h-1.5"
                  />
                  <p className="mt-1 text-xs text-muted">
                    Mínimo oficial para postular: {min} pts
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="mt-2 text-xs text-warning">
              Falta {p.faltantes.join(", ")} para calcular tu puntaje acá.
            </p>
          )}
        </div>

        <div className="flex shrink-0 flex-col gap-1">
          <button
            type="button"
            onClick={onSubir}
            disabled={esPrimera}
            aria-label="Subir preferencia"
            className="rounded px-2 text-muted hover:bg-surface-hover hover:text-foreground disabled:opacity-30"
          >
            ▲
          </button>
          <button
            type="button"
            onClick={onBajar}
            disabled={esUltima}
            aria-label="Bajar preferencia"
            className="rounded px-2 text-muted hover:bg-surface-hover hover:text-foreground disabled:opacity-30"
          >
            ▼
          </button>
          <button
            type="button"
            onClick={onQuitar}
            aria-label="Quitar de la lista"
            className="rounded px-2 text-muted hover:text-danger"
          >
            ✕
          </button>
        </div>
      </div>
    </motion.li>
  );
}

/* ── El plan ──────────────────────────────────────────────────────────── */

function Plan({ meta }: { meta: Meta }) {
  if (meta.plan.length === 0) return null;

  const semanal = meta.plan_semanal;
  // Solo se proponen los temas que caben en la semana que el estudiante dijo
  // tener. Un plan que no cabe se mira, no alcanza, y no se hace ninguna de
  // las cosas.
  const temas = meta.plan.slice(0, Math.max(1, semanal?.temas_que_caben ?? meta.plan.length));
  const horas = semanal?.horas_semana ?? null;
  const minutos = semanal?.minutos_estimados ?? 0;

  return (
    <section className="card-panel mt-8 p-6" aria-labelledby="h-plan">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h2 id="h-plan" className="font-semibold tracking-tight">
          Qué practicar esta semana
        </h2>
        {minutos > 0 && (
          <span className="text-xs text-muted">
            ≈ {Math.round(minutos / 60)} h {minutos % 60 ? `${minutos % 60} min` : ""}
          </span>
        )}
      </div>
      <p className="mt-1 text-sm text-muted">
        Los temas donde peor rindes dentro de la prueba que más mueve tu
        {meta.plan_para ? (
          <>
            {" "}
            primera preferencia sin alcanzar: <strong>{meta.plan_para}</strong>.
          </>
        ) : (
          " puntaje."
        )}
      </p>

      {horas != null && (
        <p className="mt-3 rounded-lg border border-accent/30 bg-accent/5 px-3 py-2 text-xs leading-relaxed">
          Dijiste que puedes estudiar <strong>{horas} h a la semana</strong>. Con
          eso alcanzas{" "}
          {semanal?.alcanza_un_ensayo ? "un ensayo corto y " : ""}
          {temas.length} {temas.length === 1 ? "tema" : "temas"}.{" "}
          <Link href="/perfil" className="text-accent underline-offset-4 hover:underline">
            Cambiar mis horas
          </Link>
        </p>
      )}

      <ul className="mt-4 flex flex-col divide-y divide-border">
        {temas.map((n) => (
          <li key={n.code} className="flex items-center justify-between gap-3 py-3">
            <span className="min-w-0">
              <span className="block text-sm font-medium">{n.name}</span>
              <span className="block text-xs text-muted">
                {n.attempts === 0
                  ? "Sin practicar todavía"
                  : `${Math.round(n.accuracy * 100)}% de acierto en ${n.attempts} respuestas`}
              </span>
            </span>
            <Link
              href={n.has_lesson ? `/aprender/${n.code}` : `/practicar/${n.code}`}
              className="shrink-0 text-xs font-medium text-accent hover:underline"
            >
              {n.has_lesson ? "Estudiar →" : "Practicar →"}
            </Link>
          </li>
        ))}
      </ul>

      {semanal?.alcanza_un_ensayo && (
        <Link
          href="/examen"
          className="mt-4 inline-block text-sm font-medium text-accent hover:underline"
        >
          Y un ensayo corto para medir cómo vas →
        </Link>
      )}
    </section>
  );
}
