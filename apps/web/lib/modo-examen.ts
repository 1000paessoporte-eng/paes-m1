"use client";

import { useSyncExternalStore } from "react";

/** Estado del ensayo que corre en esta pestaña, para el resto de la aplicación.
 *
 *  Existe por un motivo concreto: la barra del sitio vive en el layout raíz y
 *  el ensayo, seis niveles más abajo. Sin un canal entre los dos, el menú
 *  seguía ofreciendo Árbol, Analítica y Progreso mientras alguien rendía la
 *  prueba oficial —y como Next navega en el cliente, irse por ahí no disparaba
 *  ni el aviso de cierre de pestaña ni el registro de salidas. Se salía del
 *  ensayo sin que nada quedara anotado.
 *
 *  Es un store externo y no un contexto de React porque el layout raíz es un
 *  componente de servidor: envolverlo en un proveedor cliente arrastraría toda
 *  la página al cliente para pasar un booleano.
 */
export interface ModoExamen {
  /** Hay un ensayo empezado y sin entregar. */
  activo: boolean;
  /** Es el ensayo oficial: condiciones de examen, no práctica suelta. */
  oficial: boolean;
}

const INACTIVO: ModoExamen = { activo: false, oficial: false };

let estado: ModoExamen = INACTIVO;
const suscriptores = new Set<() => void>();

export function setModoExamen(nuevo: ModoExamen): void {
  const proximo = nuevo.activo ? nuevo : INACTIVO;
  if (proximo.activo === estado.activo && proximo.oficial === estado.oficial) return;
  estado = proximo;
  for (const avisar of suscriptores) avisar();
}

function suscribir(avisar: () => void): () => void {
  suscriptores.add(avisar);
  return () => {
    suscriptores.delete(avisar);
  };
}

/** En el servidor siempre es INACTIVO: el HTML se pinta igual para todos y el
 *  ensayo solo existe en la pestaña de quien lo rinde. */
export function useModoExamen(): ModoExamen {
  return useSyncExternalStore(
    suscribir,
    () => estado,
    () => INACTIVO
  );
}
