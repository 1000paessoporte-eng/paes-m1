"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { buscarCarrerasPublico, type CarreraCatalogo } from "@/lib/api";
import { nombreCarrera, nombreLegible, slugCarrera } from "@/lib/carreras";

type Estado = "quieto" | "buscando" | "listo" | "error";

/**
 * El buscador público de carreras.
 *
 * "¿Cuánto puntaje necesito para Enfermería en la UdeC?" es la pregunta con la
 * que la gente llega de verdad, y hasta ahora había que recorrer 47
 * universidades a mano para responderla.
 *
 * El texto vive en la URL (`?q=`) y no solo en el estado: así una búsqueda se
 * puede compartir por WhatsApp, volver con el botón atrás y quedar indexada.
 */
export function BuscadorCarreras({ inicial = "" }: { inicial?: string }) {
  const [texto, setTexto] = useState(inicial);
  const [resultados, setResultados] = useState<CarreraCatalogo[]>([]);
  const [estado, setEstado] = useState<Estado>("quieto");

  useEffect(() => {
    const consulta = texto.trim();
    if (consulta.length < 3) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setEstado("quieto");
      setResultados([]);
      return;
    }

    // Se espera a que deje de escribir: sin esto, "enfermeria" son diez
    // consultas a la base y nueve resultados que nadie llega a leer.
    let vigente = true;
    const t = setTimeout(async () => {
      setEstado("buscando");
      try {
        const data = await buscarCarrerasPublico(consulta);
        if (!vigente) return;
        setResultados(data);
        setEstado("listo");
      } catch {
        if (vigente) setEstado("error");
      }
    }, 250);

    return () => {
      vigente = false;
      clearTimeout(t);
    };
  }, [texto]);

  // La URL sigue al texto sin recargar la página ni ensuciar el historial:
  // con push, cada letra sería una entrada del botón atrás.
  useEffect(() => {
    const url = new URL(window.location.href);
    const consulta = texto.trim();
    if (consulta) url.searchParams.set("q", consulta);
    else url.searchParams.delete("q");
    window.history.replaceState(null, "", url);
  }, [texto]);

  return (
    <div>
      <label htmlFor="q" className="sr-only">
        Buscar una carrera
      </label>
      <input
        id="q"
        type="search"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Enfermería Concepción, Medicina, Ingeniería Civil…"
        autoComplete="off"
        className="w-full rounded-xl border border-border bg-surface px-4 py-3.5 text-base text-foreground placeholder:text-muted focus:border-accent focus:outline-none"
      />

      {estado === "quieto" && texto.trim().length > 0 && texto.trim().length < 3 && (
        <p className="mt-2 text-xs text-muted">Escribe al menos tres letras.</p>
      )}

      {estado === "error" && (
        <p className="mt-3 rounded-lg border border-border bg-surface p-3 text-sm text-muted">
          No pudimos buscar en este momento. Inténtalo de nuevo en unos
          segundos; abajo están todas las universidades.
        </p>
      )}

      {estado === "listo" && resultados.length === 0 && (
        <p className="mt-3 text-sm text-muted">
          Sin resultados para <strong className="text-foreground">{texto.trim()}</strong>.
          Prueba con el nombre de la carrera y la ciudad, por ejemplo
          &quot;pedagogía valparaíso&quot;.
        </p>
      )}

      {resultados.length > 0 && (
        <ul className="mt-3 flex flex-col gap-2">
          {resultados.map((c) => (
            <li key={c.codigo}>
              <Link
                href={`/carrera/${slugCarrera(c)}`}
                className="card-hover flex flex-col gap-0.5 rounded-lg border border-border bg-surface p-3"
              >
                <span className="text-sm font-medium text-foreground">
                  {nombreCarrera(c.nombre)}
                </span>
                <span className="text-xs text-muted">
                  {nombreLegible(c.universidad)} · {nombreLegible(c.sede)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/** Envoltorio que toma el término inicial de `?q=` en la URL. */
export function BuscadorConParams() {
  const params = useSearchParams();
  return <BuscadorCarreras inicial={params.get("q") ?? ""} />;
}


/**
 * La caja tal como se ve antes de hidratar.
 *
 * Existe porque `useSearchParams` obliga a que el buscador se renderice en el
 * cliente, y con un fallback vacío la página que existe justamente para
 * recibir a quien busca aparecía sin buscador durante el primer pintado.
 * Misma caja, mismas medidas: no hay salto cuando el real toma su lugar.
 */
export function BuscadorEsqueleto() {
  return (
    <input
      type="search"
      disabled
      placeholder="Enfermería Concepción, Medicina, Ingeniería Civil…"
      aria-hidden
      className="w-full rounded-xl border border-border bg-surface px-4 py-3.5 text-base text-foreground placeholder:text-muted"
    />
  );
}
