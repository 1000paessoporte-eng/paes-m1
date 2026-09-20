"use client";

import { useState } from "react";
import { pedirCotizacionColegio } from "@/lib/api";

/**
 * El formulario de cotización del plan Colegios.
 *
 * Reemplaza a un `mailto:`, que era el único camino para contratar. Un
 * `mailto:` falla callado más de lo que parece --en el teléfono puede no abrir
 * nada, y quien usa webmail ve un cliente de correo que nunca configuró-- y
 * sobre todo no deja registro: si la persona no manda el correo, nadie se
 * entera de que estuvo a punto de contratar.
 *
 * No pide cuenta. Registrarse antes de saber el precio sería poner el
 * formulario más largo justo delante de la pregunta más simple.
 *
 * Solo tres campos son obligatorios --establecimiento, quién escribe y su
 * correo-- más la cantidad de estudiantes, que es lo único sin lo cual no se
 * puede poner un número en la cotización. El resto ayuda, pero pedirlo como
 * requisito espanta a quien está averiguando.
 */

const CARGOS = [
  "Profesor o profesora",
  "Jefatura de UTP",
  "Dirección",
  "Sostenedor",
  "Otro",
];

type Estado = "escribiendo" | "enviando" | "listo";

export function FormularioCotizacion() {
  const [estado, setEstado] = useState<Estado>("escribiendo");
  const [error, setError] = useState<string | null>(null);

  async function enviar(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setEstado("enviando");

    const datos = new FormData(e.currentTarget);
    const texto = (campo: string) => String(datos.get(campo) ?? "").trim();
    const opcional = (campo: string) => texto(campo) || null;

    try {
      await pedirCotizacionColegio({
        establecimiento: texto("establecimiento"),
        contacto: texto("contacto"),
        cargo: texto("cargo"),
        email: texto("email"),
        telefono: opcional("telefono"),
        comuna: opcional("comuna"),
        alumnos: Number(datos.get("alumnos")),
        mensaje: opcional("mensaje"),
      });
      setEstado("listo");
    } catch {
      setEstado("escribiendo");
      setError(
        "No pudimos enviar la solicitud. Escríbenos a 1000paessoporte@gmail.com y lo vemos."
      );
    }
  }

  if (estado === "listo") {
    return (
      <div className="rounded-xl border border-success/40 bg-success/5 p-6 text-center">
        <p className="font-semibold tracking-tight">Recibimos tu solicitud</p>
        <p className="mt-2 text-sm text-muted">
          Te mandamos un correo de confirmación. La cotización formal te llega
          dentro de un día hábil, con los datos para la factura y la orden de
          compra.
        </p>
      </div>
    );
  }

  const deshabilitado = estado === "enviando";

  return (
    <form onSubmit={enviar} className="flex flex-col gap-4">
      <Campo etiqueta="Establecimiento" nombre="establecimiento" requerido
             ejemplo="Liceo Bicentenario de Talca" deshabilitado={deshabilitado} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Campo etiqueta="Tu nombre" nombre="contacto" requerido
               deshabilitado={deshabilitado} />
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Tu cargo</span>
          <select
            name="cargo"
            required
            disabled={deshabilitado}
            defaultValue={CARGOS[0]}
            className="rounded-lg border border-border bg-background px-3 py-2 text-sm"
          >
            {CARGOS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Campo etiqueta="Correo" nombre="email" tipo="email" requerido
               deshabilitado={deshabilitado} />
        <Campo etiqueta="Teléfono" nombre="telefono" opcional
               deshabilitado={deshabilitado} />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Cuántos estudiantes</span>
          <input
            type="number"
            name="alumnos"
            min={1}
            max={5000}
            required
            disabled={deshabilitado}
            placeholder="90"
            className="rounded-lg border border-border bg-background px-3 py-2 text-sm"
          />
          <span className="text-xs text-muted">
            Un curso son unos 30. Si no sabes el número exacto, aproxima.
          </span>
        </label>
        <Campo etiqueta="Comuna" nombre="comuna" opcional deshabilitado={deshabilitado} />
      </div>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">
          Algo más que debamos saber <span className="text-muted">(opcional)</span>
        </span>
        <textarea
          name="mensaje"
          rows={3}
          maxLength={2000}
          disabled={deshabilitado}
          placeholder="Qué cursos, para cuándo lo necesitan, dudas."
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm"
        />
      </label>

      {error && <p className="text-sm text-danger">{error}</p>}

      <button
        type="submit"
        disabled={deshabilitado}
        className="btn-glow rounded-lg px-5 py-3 text-sm font-medium text-accent-foreground disabled:opacity-60"
      >
        {deshabilitado ? "Enviando…" : "Pedir cotización"}
      </button>

      <p className="text-xs text-muted">
        Te responde una persona, no un sistema automático. Usamos estos datos
        solo para responderte esta cotización.
      </p>
    </form>
  );
}

function Campo({
  etiqueta,
  nombre,
  tipo = "text",
  requerido = false,
  opcional = false,
  ejemplo,
  deshabilitado,
}: {
  etiqueta: string;
  nombre: string;
  tipo?: string;
  requerido?: boolean;
  opcional?: boolean;
  ejemplo?: string;
  deshabilitado: boolean;
}) {
  return (
    <label className="flex flex-col gap-1.5 text-sm">
      <span className="font-medium">
        {etiqueta} {opcional && <span className="text-muted">(opcional)</span>}
      </span>
      <input
        type={tipo}
        name={nombre}
        required={requerido}
        disabled={deshabilitado}
        placeholder={ejemplo}
        className="rounded-lg border border-border bg-background px-3 py-2 text-sm"
      />
    </label>
  );
}
