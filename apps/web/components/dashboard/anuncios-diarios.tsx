"use client";

import { useSyncExternalStore } from "react";
import { anuncioDeHoy, type Anuncio } from "@/lib/anuncios";

/**
 * Decide cuál de los avisos corresponde hoy, y monta solo ese.
 *
 * La decisión vive acá y no dentro de cada aviso porque es EXCLUYENTE: si cada
 * uno resolviera su propio turno, dos podrían caer el mismo día y el alumno
 * vería ventanas apiladas. Concentrarla en un punto es lo que garantiza el
 * máximo de uno diario.
 *
 * Usa useSyncExternalStore y no useEffect para leer localStorage: el servidor
 * no tiene acceso a él, y esa es justamente la forma que React ofrece para
 * estado externo al DOM sin provocar un desajuste de hidratación. En el
 * servidor devuelve null, así que nada se dibuja hasta que el navegador
 * resuelve el turno.
 */
export function AnunciosDiarios({
  ofrecerPro,
  premio,
  planes,
}: {
  ofrecerPro: boolean;
  premio: React.ReactNode;
  planes: React.ReactNode;
}) {
  const disponibles: Anuncio[] = ofrecerPro && planes ? ["premio", "planes"] : ["premio"];
  const clave = disponibles.join(",");

  const turno = useSyncExternalStore(
    () => () => {},
    () => anuncioDeHoy(clave.split(",") as Anuncio[]),
    () => null,
  );

  if (turno === "planes") return <>{planes}</>;
  if (turno === "premio") return <>{premio}</>;
  return null;
}
