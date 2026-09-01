"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  buscarCarrerasPublico,
  type CarreraBusqueda,
  getUbicacionesCarreras,
  type RegionConComunas,
} from "@/lib/api";
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
export function BuscadorCarreras({
  inicial = "",
  regionInicial = "",
  comunaInicial = "",
}: {
  inicial?: string;
  regionInicial?: string;
  comunaInicial?: string;
}) {
  const [texto, setTexto] = useState(inicial);
  const [region, setRegion] = useState(regionInicial);
  const [comuna, setComuna] = useState(comunaInicial);
  const [ubicaciones, setUbicaciones] = useState<RegionConComunas[]>([]);
  const [resultados, setResultados] = useState<CarreraBusqueda[]>([]);
  const [estado, setEstado] = useState<Estado>("quieto");

  // Las regiones y comunas se piden una vez: cambian una vez por proceso de
  // admisión, no mientras alguien busca.
  useEffect(() => {
    let vigente = true;
    getUbicacionesCarreras()
      .then((data) => {
        if (vigente) setUbicaciones(data);
      })
      .catch(() => {
        // Sin ubicaciones el filtro no aparece, pero el buscador por texto
        // sigue funcionando: no es motivo para romper la página.
      });
    return () => {
      vigente = false;
    };
  }, []);

  // Las comunas que ofrece el selector dependen de la región elegida.
  const comunasDeRegion =
    ubicaciones.find((u) => u.region === region)?.comunas ?? [];

  useEffect(() => {
    const consulta = texto.trim();
    const hayUbicacion = Boolean(region || comuna);
    // Sin texto suficiente y sin filtro de ubicación no hay nada que buscar.
    if (consulta.length < 3 && !hayUbicacion) {
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
        const data = await buscarCarrerasPublico(consulta, { region, comuna });
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
  }, [texto, region, comuna]);

  // La URL sigue al texto y a la ubicación sin recargar ni ensuciar el
  // historial: así una búsqueda filtrada se comparte y vuelve con el botón
  // atrás. Con push, cada letra sería una entrada.
  useEffect(() => {
    const url = new URL(window.location.href);
    const consulta = texto.trim();
    for (const [clave, valor] of [
      ["q", consulta],
      ["region", region],
      ["comuna", comuna],
    ] as const) {
      if (valor) url.searchParams.set(clave, valor);
      else url.searchParams.delete(clave);
    }
    window.history.replaceState(null, "", url);
  }, [texto, region, comuna]);

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

      {ubicaciones.length > 0 && (
        <div className="mt-2 flex flex-col gap-2 sm:flex-row">
          <label htmlFor="region" className="sr-only">
            Región
          </label>
          <select
            id="region"
            value={region}
            onChange={(e) => {
              // Al cambiar de región, la comuna anterior deja de existir en el
              // nuevo selector: se limpia para no filtrar por una comuna que no
              // pertenece a la región elegida.
              setRegion(e.target.value);
              setComuna("");
            }}
            className="w-full rounded-xl border border-border bg-surface px-3 py-2.5 text-sm text-foreground focus:border-accent focus:outline-none sm:w-1/2"
          >
            <option value="">Todas las regiones</option>
            {ubicaciones.map((u) => (
              <option key={u.region} value={u.region}>
                {u.region}
              </option>
            ))}
          </select>

          <label htmlFor="comuna" className="sr-only">
            Comuna
          </label>
          <select
            id="comuna"
            value={comuna}
            disabled={comunasDeRegion.length === 0}
            onChange={(e) => setComuna(e.target.value)}
            className="w-full rounded-xl border border-border bg-surface px-3 py-2.5 text-sm text-foreground focus:border-accent focus:outline-none disabled:opacity-50 sm:w-1/2"
          >
            <option value="">
              {region ? "Todas las comunas" : "Elige una región primero"}
            </option>
            {comunasDeRegion.map((c) => (
              <option key={c} value={c}>
                {nombreLegible(c)}
              </option>
            ))}
          </select>
        </div>
      )}

      {estado === "quieto" &&
        texto.trim().length > 0 &&
        texto.trim().length < 3 &&
        !region &&
        !comuna && (
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
          {texto.trim().length >= 3 ? (
            <>
              Sin resultados para{" "}
              <strong className="text-foreground">{texto.trim()}</strong>
              {comuna
                ? ` en ${nombreLegible(comuna)}`
                : region
                  ? ` en la Región de ${region}`
                  : ""}
              . Prueba con el nombre de la carrera y la ciudad, por ejemplo
              &quot;pedagogía valparaíso&quot;.
            </>
          ) : (
            <>
              No hay carreras{" "}
              {comuna
                ? `en ${nombreLegible(comuna)}`
                : region
                  ? `en la Región de ${region}`
                  : "con ese filtro"}
              . Prueba otra región o comuna.
            </>
          )}
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
                  {c.comuna ? ` · ${nombreLegible(c.comuna)}` : ""}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/** Envoltorio que toma el término y la ubicación iniciales de la URL. */
export function BuscadorConParams() {
  const params = useSearchParams();
  return (
    <BuscadorCarreras
      inicial={params.get("q") ?? ""}
      regionInicial={params.get("region") ?? ""}
      comunaInicial={params.get("comuna") ?? ""}
    />
  );
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
