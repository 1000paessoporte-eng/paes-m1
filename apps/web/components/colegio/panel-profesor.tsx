"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type {
  AlumnoDelCurso,
  EjeDelCurso,
  EnsayoProgramado,
  MiColegio,
} from "@/lib/api";
import { salirDelColegio } from "@/lib/api";
import { actualizarUsuarioLocal, getClientToken } from "@/lib/auth";
import { AgendaEnsayos } from "@/components/colegio/agenda-ensayos";
import { CodigoCurso } from "@/components/colegio/codigo-curso";
import { EjesDelCurso } from "@/components/colegio/ejes-del-curso";
import { TablaAlumnos } from "@/components/colegio/tabla-alumnos";

/**
 * El panel del profesor.
 *
 * El orden de la página es el orden en que se necesita: primero el código
 * --sin él no hay curso--, después quién está y cómo va, y al final la agenda.
 * Un profesor que abre esto en marzo necesita lo primero; el que lo abre en
 * septiembre, lo segundo.
 */
export function PanelProfesor({
  colegio,
  alumnos,
  ejes,
  ensayos,
  perdidos,
}: {
  colegio: NonNullable<MiColegio>;
  alumnos: AlumnoDelCurso[];
  ejes: EjeDelCurso[];
  ensayos: EnsayoProgramado[];
  /** Cuántos llevan más de una semana sin rendir.
   *
   * Llega calculado desde el servidor: leer el reloj durante el render de un
   * componente cliente da un resultado distinto en cada re-render, y React lo
   * prohíbe por eso mismo. */
  perdidos: number;
}) {
  const router = useRouter();
  const [saliendo, setSaliendo] = useState(false);

  // "Llevan una semana sin rendir" es falso cuando nunca rindieron: en marzo,
  // con el curso recién armado, esa frase acusaba a treinta personas de algo
  // que no habían tenido tiempo de hacer.
  const nadieRindio = alumnos.every((a) => a.ensayos === 0);

  async function salir() {
    if (
      !confirm(
        "Vas a salir del curso. El curso y sus alumnos siguen ahí, pero pierdes el panel. ¿Seguro?"
      )
    )
      return;
    setSaliendo(true);
    try {
      await salirDelColegio(getClientToken() ?? undefined);
      actualizarUsuarioLocal({ tiene_colegio: false });
      router.refresh();
    } catch {
      setSaliendo(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <p className="text-xs font-medium tracking-wide text-muted uppercase">
          Panel del profesor
        </p>
        <h1 className="mt-1 text-2xl font-semibold">{colegio.nombre}</h1>
        <p className="mt-1 text-sm text-muted">
          {alumnos.length === 0
            ? "Todavía no entra nadie al curso."
            : nadieRindio
              ? `${alumnos.length} ${alumnos.length === 1 ? "alumno" : "alumnos"} en el curso. Todavía nadie rinde un ensayo.`
              : perdidos === 0
                ? `${alumnos.length} ${alumnos.length === 1 ? "alumno" : "alumnos"}, y todos rindieron algo esta semana.`
                : `${alumnos.length} ${alumnos.length === 1 ? "alumno" : "alumnos"}. ${perdidos} ${perdidos === 1 ? "lleva" : "llevan"} más de una semana sin rendir un ensayo.`}
        </p>
      </div>

      <CodigoCurso codigo={colegio.codigo ?? ""} />

      <TablaAlumnos alumnos={alumnos} />

      <EjesDelCurso ejes={ejes} />

      <AgendaEnsayos ensayos={ensayos} puedeAgendar />

      <div className="border-t border-border pt-6">
        <button
          type="button"
          onClick={salir}
          disabled={saliendo}
          className="text-sm text-muted underline decoration-border underline-offset-4 hover:text-danger"
        >
          Salir de este curso
        </button>
      </div>
    </div>
  );
}
