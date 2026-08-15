"use client";

import Link from "next/link";
import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import type { Carrera, Meta } from "@/lib/api";
import { borrarMeta, buscarCarreras, fijarMeta } from "@/lib/api";
import { getClientToken } from "@/lib/auth";
import { BarraProgreso } from "@/components/ui/barra-progreso";
import { NumeroAnimado } from "@/components/motion/numero-animado";

/**
 * Mi meta: la carrera y cuánto falta.
 *
 * En Chile nadie estudia para "subir el puntaje": se estudia para entrar a una
 * carrera. El puntaje que decide una admisión es el PONDERADO, que combina NEM,
 * ranking y las pruebas con los pesos que fija cada carrera — y casi ningún
 * estudiante lo tiene a la vista mientras estudia.
 *
 * Lo que esta pantalla responde, y que ninguna tabla de puntajes de corte
 * responde, es dónde rinde más la próxima hora de estudio: en una carrera que
 * pondera M1 al 35%, diez puntos en M1 valen tres veces y media más que diez
 * puntos donde pondera 10%.
 */
export function MetaView({ inicial }: { inicial: Meta | null }) {
  const [meta, setMeta] = useState<Meta | null>(inicial);
  const [editando, setEditando] = useState(inicial === null);

  if (editando || meta === null) {
    return (
      <Buscador
        actual={meta}
        onListo={(m) => {
          setMeta(m);
          setEditando(false);
        }}
        onCancelar={meta ? () => setEditando(false) : undefined}
      />
    );
  }

  return (
    <Resultado
      meta={meta}
      onCambiar={() => setEditando(true)}
      onBorrar={async () => {
        await borrarMeta(getClientToken() ?? undefined);
        setMeta(null);
        setEditando(true);
      }}
    />
  );
}

/* ── Elegir carrera ───────────────────────────────────────────────────── */

function Buscador({
  actual,
  onListo,
  onCancelar,
}: {
  actual: Meta | null;
  onListo: (m: Meta) => void;
  onCancelar?: () => void;
}) {
  const [texto, setTexto] = useState("");
  const [resultados, setResultados] = useState<Carrera[]>([]);
  const [elegida, setElegida] = useState<Carrera | null>(null);
  const [nem, setNem] = useState(actual?.carrera ? "" : "");
  const [ranking, setRanking] = useState("");
  const [buscando, setBuscando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    if (texto.trim().length < 3) return;
    setBuscando(true);
    setError(null);
    try {
      setResultados(await buscarCarreras(texto, getClientToken() ?? undefined));
    } catch {
      setError("No se pudo buscar. Intenta de nuevo.");
    } finally {
      setBuscando(false);
    }
  }

  async function guardar() {
    if (!elegida) return;
    try {
      const m = await fijarMeta(
        {
          carrera_id: elegida.id,
          puntaje_nem: nem ? Number(nem) : null,
          puntaje_ranking: ranking ? Number(ranking) : null,
        },
        getClientToken() ?? undefined
      );
      onListo(m);
    } catch {
      setError("No se pudo guardar tu meta.");
    }
  }

  return (
    <div className="mx-auto w-full max-w-2xl">
      <h1 className="text-2xl font-bold tracking-tight">¿A qué carrera quieres entrar?</h1>
      <p className="mt-2 text-sm leading-relaxed text-muted">
        Cada carrera pondera las pruebas distinto. Con la tuya elegida, la
        plataforma puede decirte dónde rinde más cada hora de estudio.
      </p>

      <form onSubmit={buscar} className="mt-6 flex gap-2">
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Ingeniería civil, enfermería, Universidad de Chile…"
          aria-label="Buscar carrera o universidad"
          className="min-w-0 flex-1 rounded-lg border border-border bg-background px-4 py-2.5 text-sm"
        />
        <button
          type="submit"
          disabled={texto.trim().length < 3 || buscando}
          className="btn-glow shrink-0 rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground disabled:opacity-50"
        >
          {buscando ? "Buscando…" : "Buscar"}
        </button>
      </form>

      {error && (
        <p className="mt-3 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
          {error}
        </p>
      )}

      {resultados.length > 0 && (
        <ul className="mt-5 flex flex-col gap-2">
          {resultados.map((c) => (
            <li key={c.id}>
              <button
                type="button"
                onClick={() => setElegida(c)}
                aria-pressed={elegida?.id === c.id}
                className={
                  "w-full rounded-xl border p-4 text-left transition " +
                  (elegida?.id === c.id
                    ? "border-accent bg-accent/5 ring-1 ring-accent"
                    : "border-border bg-surface hover:border-border-strong")
                }
              >
                <span className="block text-sm font-semibold">{c.nombre}</span>
                <span className="block text-xs text-muted">
                  {c.universidad} · {c.sede}
                </span>
                <span className="mt-2 block text-xs text-muted">
                  {[
                    c.nem && `NEM ${c.nem}%`,
                    c.ranking && `Ranking ${c.ranking}%`,
                    c.lectora && `Lectora ${c.lectora}%`,
                    c.m1 && `M1 ${c.m1}%`,
                    c.m2 && `M2 ${c.m2}%`,
                    c.historia && `Historia ${c.historia}%`,
                    c.ciencias && `Ciencias ${c.ciencias}%`,
                  ]
                    .filter(Boolean)
                    .join(" · ")}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {resultados.length === 0 && texto && !buscando && (
        <p className="mt-5 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-muted">
          Sin resultados. Los datos son del proceso de Admisión 2026 y cubren
          1.855 carreras de las 47 universidades del sistema centralizado; unas
          pocas quedaron fuera porque su fila en el documento oficial no se pudo
          leer con seguridad.
        </p>
      )}

      {elegida && (
        <div className="card-panel mt-6 p-5">
          <h2 className="font-semibold tracking-tight">Tus notas</h2>
          <p className="mt-1 text-sm text-muted">
            Opcional. Son los puntajes de NEM y ranking que vienen en tu informe,
            no el promedio de notas: la conversión la hace el DEMRE y no la
            estimamos acá. Sin ellos igual verás el peso de cada prueba.
          </p>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <label className="text-sm">
              <span className="block text-xs text-muted">Puntaje NEM</span>
              <input
                inputMode="numeric"
                value={nem}
                onChange={(e) => setNem(e.target.value.replace(/\D/g, "").slice(0, 4))}
                placeholder="Ej: 720"
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 tabular-nums"
              />
            </label>
            <label className="text-sm">
              <span className="block text-xs text-muted">Puntaje ranking</span>
              <input
                inputMode="numeric"
                value={ranking}
                onChange={(e) => setRanking(e.target.value.replace(/\D/g, "").slice(0, 4))}
                placeholder="Ej: 780"
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 tabular-nums"
              />
            </label>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={guardar}
              className="btn-warm rounded-lg px-5 py-2.5 text-sm font-semibold text-on-fill"
            >
              Fijar esta meta →
            </button>
            {onCancelar && (
              <button
                type="button"
                onClick={onCancelar}
                className="rounded-lg border border-border px-4 py-2.5 text-sm font-medium hover:bg-surface-hover"
              >
                Cancelar
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Ver la brecha ────────────────────────────────────────────────────── */

function Resultado({
  meta,
  onCambiar,
  onBorrar,
}: {
  meta: Meta;
  onCambiar: () => void;
  onBorrar: () => void;
}) {
  const quieto = useReducedMotion();
  const { carrera, aportes, ponderado, faltantes, mejor_palanca } = meta;

  // El máximo posible con estas ponderaciones es 1000: sirve de escala para
  // leer el ponderado actual sin inventar un puntaje de corte.
  const porcentaje = ponderado ? (ponderado / 1000) * 100 : 0;

  return (
    <div className="mx-auto w-full max-w-3xl">
      <header>
        <p className="text-xs font-medium tracking-wide text-accent uppercase">Mi meta</p>
        <h1 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl">
          {carrera.nombre}
        </h1>
        <p className="mt-1 text-sm text-muted">
          {carrera.universidad} · {carrera.sede}
        </p>
      </header>

      {/* ── Puntaje ponderado ─────────────────────────────────────────── */}
      <section className="card-panel mt-6 p-6">
        {ponderado != null ? (
          <>
            <p className="text-sm text-muted">Tu puntaje ponderado proyectado</p>
            <p className="mt-1 text-5xl font-bold tracking-tight tabular-nums">
              <NumeroAnimado valor={Math.round(ponderado)} />
              <span className="text-xl font-medium text-muted">/1000</span>
            </p>
            <div className="mt-4">
              <BarraProgreso
                porcentaje={porcentaje}
                etiqueta="Puntaje ponderado proyectado"
                alto="h-2.5"
              />
            </div>
            <p className="mt-3 text-xs leading-relaxed text-muted">
              Calculado con las ponderaciones oficiales de esta carrera y tu
              mejor puntaje en cada prueba. Es una proyección con tus ensayos, no
              un puntaje oficial.
            </p>
          </>
        ) : (
          <>
            <p className="text-sm font-medium">
              Te falta rendir {faltantes.length === 1 ? "una prueba" : "algunas pruebas"}{" "}
              para completar la proyección
            </p>
            <ul className="mt-3 flex flex-wrap gap-2">
              {faltantes.map((f) => (
                <li
                  key={f}
                  className="rounded-full border border-warning/40 bg-warning/10 px-3 py-1 text-xs font-medium text-warning"
                >
                  {f}
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-muted">
              Mostrar un ponderado parcial como si fuera el total sería
              engañarte: aparece cuando estén todos los factores.
            </p>
          </>
        )}
      </section>

      {/* ── Dónde rinde más estudiar ──────────────────────────────────── */}
      <section className="card-panel mt-5 p-6" aria-labelledby="h-aportes">
        <h2 id="h-aportes" className="font-semibold tracking-tight">
          Dónde rinde más tu estudio
        </h2>
        <p className="mt-1 text-sm text-muted">
          Cuánto sube tu ponderado por cada 10 puntos que ganes en cada factor.
          {mejor_palanca && (
            <>
              {" "}
              Hoy tu mayor palanca es <strong className="text-foreground">{mejor_palanca}</strong>.
            </>
          )}
        </p>

        <ul className="mt-5 flex flex-col gap-4">
          {[...aportes]
            .sort((a, b) => b.por_cada_10 - a.por_cada_10)
            .map((a, i) => (
              <motion.li
                key={a.factor}
                initial={quieto ? false : { opacity: 0, x: -8 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.35, delay: i * 0.05 }}
              >
                <div className="flex items-baseline justify-between gap-3 text-sm">
                  <span className="min-w-0 truncate">
                    {a.etiqueta}
                    <span className="ml-2 text-xs text-muted">pondera {a.ponderacion}%</span>
                  </span>
                  <span className="shrink-0 tabular-nums">
                    <strong className="text-foreground">+{a.por_cada_10}</strong>
                    <span className="text-xs text-muted"> por cada 10 pts</span>
                  </span>
                </div>
                <div className="mt-1.5">
                  <BarraProgreso
                    porcentaje={a.ponderacion}
                    etiqueta={`${a.etiqueta}: pondera ${a.ponderacion}%`}
                    delay={i * 0.05}
                    alto="h-1.5"
                  />
                </div>
                <p className="mt-1 text-xs text-muted">
                  {a.origen === "falta"
                    ? "Sin puntaje todavía"
                    : a.origen === "ingresado"
                      ? `${a.puntaje} pts · lo ingresaste tú`
                      : `${a.puntaje} pts · tu mejor ensayo`}
                </p>
              </motion.li>
            ))}
        </ul>
      </section>

      <p className="mt-5 text-xs leading-relaxed text-muted">
        Ponderaciones oficiales del Proceso de Admisión {carrera.proceso}, según
        la oferta definitiva del DEMRE.{" "}
        <a
          href={carrera.fuente}
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent underline-offset-4 hover:underline"
        >
          Ver el documento
        </a>
        . Cambian cada año: revísalas antes de postular.
      </p>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          href="/examen"
          className="btn-warm rounded-lg px-5 py-2.5 text-sm font-semibold text-on-fill"
        >
          Practicar {mejor_palanca ?? "ahora"} →
        </Link>
        <button
          type="button"
          onClick={onCambiar}
          className="rounded-lg border border-border px-4 py-2.5 text-sm font-medium hover:bg-surface-hover"
        >
          Cambiar carrera
        </button>
        <button
          type="button"
          onClick={onBorrar}
          className="rounded-lg px-3 py-2.5 text-sm text-muted hover:text-danger"
        >
          Quitar meta
        </button>
      </div>
    </div>
  );
}
