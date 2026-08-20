"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { buscarCarrerasPublico, getCarrera, type CarreraPublica } from "@/lib/api";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { nombreLegible, slugCarrera } from "@/lib/carreras";
import { calcularPonderado, ETIQUETAS, type Factor, type Puntajes } from "@/lib/ponderado";

/** Dónde se guarda la lista entre visitas. No hay cuenta: vive en el navegador. */
const CLAVE = "paes_simulador";

/** El tope de la lista. Es el mismo que el plan Pro permite en Mi meta, y no
 *  por casualidad: esta página es Mi meta sin cuenta. */
const MAX = 10;

/** Los factores que el alumno declara. En este orden, como en el DEMRE. */
const CAMPOS: Factor[] = ["nem", "ranking", "lectora", "m1", "m2", "historia", "ciencias"];

type Guardado = { puntajes: Puntajes; codigos: string[] };

/**
 * "¿Cuánto me falta para mi carrera?", respondido sin cuenta.
 *
 * La ficha de una carrera ya trae su simulador, pero responde por UNA. Nadie
 * elige una sola: se postula a varias y la pregunta real es cuál está más
 * cerca. Eso obliga a escribir los puntajes una vez y compararlas entre sí, y
 * hasta ahora solo se podía hacer con cuenta, dentro de Mi meta.
 *
 * Es lo único que este producto tiene y la competencia no: las 1.855
 * ponderaciones oficiales cruzadas con el puntaje real de la persona. Tenerlo
 * detrás del login era esconder justo el argumento para quedarse.
 *
 * Corre entero en el navegador y no manda nada a ningún servidor: los puntajes
 * de alguien son un dato sensible, y acá no hay razón para que salgan de su
 * teléfono. Se guardan en el propio navegador para que la lista siga ahí al
 * volver.
 */
export function SimuladorMultiple() {
  const [puntajes, setPuntajes] = useState<Puntajes>({});
  const [carreras, setCarreras] = useState<CarreraPublica[]>([]);
  const [listo, setListo] = useState(false);

  // Se restaura lo guardado en el primer render del cliente. Hasta que eso
  // ocurre no se escribe nada: si no, el primer efecto pisaría la lista real
  // con el estado vacío inicial.
  useEffect(() => {
    (async () => {
      try {
        const crudo = localStorage.getItem(CLAVE);
        if (crudo) {
          const g = JSON.parse(crudo) as Guardado;
          setPuntajes(g.puntajes ?? {});
          const traidas = await Promise.all(
            (g.codigos ?? []).slice(0, MAX).map((c) => getCarrera(c).catch(() => null))
          );
          setCarreras(traidas.filter((c): c is CarreraPublica => c !== null));
        }
      } catch {
        // Almacenamiento bloqueado o dato corrupto: se empieza en blanco, que
        // es peor que recuperar la lista pero mucho mejor que no cargar.
      }
      setListo(true);
    })();
  }, []);

  useEffect(() => {
    if (!listo) return;
    try {
      const g: Guardado = { puntajes, codigos: carreras.map((c) => c.codigo) };
      localStorage.setItem(CLAVE, JSON.stringify(g));
    } catch {
      // No poder guardar no puede romper la página.
    }
  }, [listo, puntajes, carreras]);

  const filas = carreras
    .map((c) => {
      const ponderado = calcularPonderado(c, puntajes);
      const minimo = c.ponderado_min;
      return {
        carrera: c,
        ponderado,
        minimo,
        diferencia:
          ponderado != null && minimo != null
            ? Math.round((ponderado - minimo) * 10) / 10
            : null,
      };
    })
    // Lo más cerca de alcanzarse primero. Lo que no se puede comparar --sin
    // puntajes o sin mínimo publicado-- va al final, no arriba con un cero.
    .sort((a, b) => {
      if (a.diferencia == null && b.diferencia == null) return 0;
      if (a.diferencia == null) return 1;
      if (b.diferencia == null) return -1;
      return b.diferencia - a.diferencia;
    });

  return (
    <div className="flex flex-col gap-6">
      <section className="rounded-xl border border-border bg-surface p-6">
        <h2 className="font-semibold tracking-tight">1. Tus puntajes</h2>
        <p className="mt-1 text-sm text-muted">
          Los que ya tienes o los que crees que puedes sacar. Se escriben una
          vez y valen para todas las carreras de tu lista.
        </p>
        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {CAMPOS.map((f) => (
            <Campo
              key={f}
              id={f}
              etiqueta={ETIQUETAS[f]}
              valor={puntajes[f] ?? null}
              onChange={(v) => setPuntajes((p) => ({ ...p, [f]: v }))}
            />
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-border bg-surface p-6">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="font-semibold tracking-tight">2. Tus carreras</h2>
          <span className="text-xs text-muted tabular-nums">
            {carreras.length} de {MAX}
          </span>
        </div>
        <BuscadorParaAgregar
          deshabilitado={carreras.length >= MAX}
          yaElegidas={carreras.map((c) => c.codigo)}
          onElegir={(c) => setCarreras((cs) => (cs.length >= MAX ? cs : [...cs, c]))}
        />
      </section>

      {filas.length > 0 && (
        <section className="rounded-xl border border-border bg-surface p-6">
          <h2 className="font-semibold tracking-tight">3. Cuánto te falta</h2>
          <ul className="mt-4 flex flex-col gap-3">
            {filas.map(({ carrera, ponderado, minimo, diferencia }) => (
              <li
                key={carrera.codigo}
                className="rounded-lg border border-border bg-background p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <Link
                      href={`/carrera/${slugCarrera(carrera)}`}
                      className="text-sm font-medium text-foreground hover:underline"
                    >
                      {nombreLegible(carrera.nombre)}
                    </Link>
                    <p className="text-xs text-muted">
                      {nombreLegible(carrera.universidad)}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      setCarreras((cs) => cs.filter((x) => x.codigo !== carrera.codigo))
                    }
                    aria-label={`Quitar ${nombreLegible(carrera.nombre)}`}
                    className="shrink-0 text-xs text-muted underline-offset-4 hover:text-foreground hover:underline"
                  >
                    Quitar
                  </button>
                </div>
                <p className="mt-3 text-sm">
                  <Veredicto ponderado={ponderado} minimo={minimo} diferencia={diferencia} />
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="rounded-xl border border-accent/40 bg-accent/5 p-6 text-center">
        <h2 className="font-semibold">Ahora súbelos</h2>
        <p className="mt-1.5 text-sm text-muted">
          Con una cuenta gratis rindes ensayos cronometrados y tu puntaje real
          reemplaza al estimado, así que esta lista se actualiza sola.
        </p>
        <Link
          href="/registro"
          className="btn-glow mt-4 inline-flex rounded-lg px-6 py-3 text-sm font-semibold text-accent-foreground"
        >
          Crear cuenta gratis →
        </Link>
      </section>
    </div>
  );
}

/**
 * El veredicto de una carrera.
 *
 * Cuando el DEMRE no publicó el ponderado mínimo se dice eso mismo. 1.153 de
 * las 1.855 carreras no lo traen, y presentar un "te faltan 0" ahí sería
 * inventar el dato que decide si alguien cree que puede postular.
 */
function Veredicto({
  ponderado,
  minimo,
  diferencia,
}: {
  ponderado: number | null;
  minimo: number | null | undefined;
  diferencia: number | null;
}) {
  if (ponderado == null) {
    return (
      <span className="text-muted">
        Faltan puntajes que esta carrera pondera. Complétalos arriba.
      </span>
    );
  }
  if (minimo == null) {
    return (
      <span className="text-muted">
        Tu ponderado es{" "}
        <strong className="text-foreground tabular-nums">
          <NumeroAnimado valor={ponderado} duracion={0.6} />
        </strong>
        . El DEMRE no publicó puntaje mínimo para esta carrera, así que no hay
        contra qué compararlo.
      </span>
    );
  }
  if (diferencia != null && diferencia >= 0) {
    return (
      <span className="text-success">
        Tu ponderado es{" "}
        <strong className="tabular-nums">
          <NumeroAnimado valor={ponderado} duracion={0.6} />
        </strong>{" "}
        y el mínimo del proceso anterior fue {minimo}:{" "}
        <strong>te sobran {diferencia} puntos</strong>.
      </span>
    );
  }
  return (
    <span className="text-accent-warm-strong">
      Tu ponderado es{" "}
      <strong className="tabular-nums">
        <NumeroAnimado valor={ponderado} duracion={0.6} />
      </strong>{" "}
      y el mínimo del proceso anterior fue {minimo}:{" "}
      <strong>te faltan {Math.abs(diferencia ?? 0)} puntos</strong>.
    </span>
  );
}

function Campo({
  id,
  etiqueta,
  valor,
  onChange,
}: {
  id: string;
  etiqueta: string;
  valor: number | null;
  onChange: (v: number | null) => void;
}) {
  return (
    <label htmlFor={id} className="flex flex-col gap-1.5 text-sm">
      <span className="text-muted">{etiqueta}</span>
      <input
        id={id}
        type="number"
        inputMode="numeric"
        min={100}
        max={1000}
        value={valor ?? ""}
        onChange={(e) => {
          const n = e.target.value === "" ? null : Number(e.target.value);
          onChange(n != null && Number.isFinite(n) ? n : null);
        }}
        placeholder="—"
        className="rounded-lg border border-border bg-background px-3 py-2 tabular-nums focus:border-accent focus:outline-none"
      />
    </label>
  );
}

/** Buscar y agregar. Reusa el buscador público que ya existe en la API. */
function BuscadorParaAgregar({
  onElegir,
  yaElegidas,
  deshabilitado,
}: {
  onElegir: (c: CarreraPublica) => void;
  yaElegidas: string[];
  deshabilitado: boolean;
}) {
  const [texto, setTexto] = useState("");
  const [opciones, setOpciones] = useState<{ codigo: string; nombre: string; universidad: string }[]>([]);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    const q = texto.trim();
    if (q.length < 3) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setOpciones([]);
      return;
    }
    let vigente = true;
    const t = setTimeout(async () => {
      try {
        const r = await buscarCarrerasPublico(q);
        if (vigente) setOpciones(r);
      } catch {
        if (vigente) setOpciones([]);
      }
    }, 250);
    return () => {
      vigente = false;
      clearTimeout(t);
    };
  }, [texto]);

  async function agregar(codigo: string) {
    setCargando(true);
    try {
      const c = await getCarrera(codigo);
      onElegir(c);
      setTexto("");
      setOpciones([]);
    } catch {
      // Si no se puede traer la ficha, no se agrega a medias.
    }
    setCargando(false);
  }

  if (deshabilitado) {
    return (
      <p className="mt-4 text-sm text-muted">
        Llegaste a {MAX} carreras, que es el tope. Quita alguna para agregar otra.
      </p>
    );
  }

  return (
    <div className="mt-4">
      <label htmlFor="agregar" className="sr-only">
        Buscar una carrera para agregar
      </label>
      <input
        id="agregar"
        type="search"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Enfermería Concepción, Medicina, Ingeniería Civil…"
        autoComplete="off"
        className="w-full rounded-lg border border-border bg-background px-4 py-3 text-base focus:border-accent focus:outline-none"
      />
      {opciones.length > 0 && (
        <ul className="mt-2 flex flex-col gap-1">
          {opciones.slice(0, 8).map((o) => {
            const yaEsta = yaElegidas.includes(o.codigo);
            return (
              <li key={o.codigo}>
                <button
                  type="button"
                  disabled={yaEsta || cargando}
                  onClick={() => agregar(o.codigo)}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-left text-sm hover:bg-surface-hover disabled:opacity-50"
                >
                  <span className="block text-foreground">{nombreLegible(o.nombre)}</span>
                  <span className="block text-xs text-muted">
                    {nombreLegible(o.universidad)}
                    {yaEsta ? " · ya está en tu lista" : ""}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
