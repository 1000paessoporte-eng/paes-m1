import Link from "next/link";
import type { ReactNode } from "react";

/**
 * Una sección que existe y todavía no tiene datos de este estudiante.
 *
 * Reemplaza al cartel de "Próximamente" que se usaba acá: la analítica está
 * construida y funcionando, así que anunciarla como algo que aún no existe le
 * dice al estudiante algo falso sobre el producto y le quita la razón para
 * volver. Lo que falta no es la función, son sus datos — y de eso se sale
 * haciendo algo, así que el estado vacío trae el botón para hacerlo.
 */
export function EstadoVacio({
  title,
  description,
  icon,
  accion,
}: {
  title: string;
  description: string;
  icon: ReactNode;
  accion?: { href: string; label: string };
}) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 text-accent">
        {icon}
      </div>
      <h1 className="mt-5 text-xl font-semibold">{title}</h1>
      <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">{description}</p>
      {accion && (
        <Link
          href={accion.href}
          className="btn-warm mt-6 rounded-lg px-5 py-2.5 text-sm font-semibold text-on-fill"
        >
          {accion.label}
        </Link>
      )}
    </div>
  );
}
