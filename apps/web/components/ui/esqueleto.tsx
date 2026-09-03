/**
 * Las piezas de las pantallas de carga.
 *
 * Un esqueleto solo sirve si tiene la forma de lo que va a llegar. Si no la
 * tiene, el contenido entra y todo salta de sitio, y eso se siente peor que
 * haber esperado en blanco. Por eso esto son piezas para componer cada pantalla
 * a la medida de su página, y no un spinner genérico para todas.
 *
 * Accesibilidad: quien usa lector de pantalla no ve el gris moviéndose. El
 * contenedor de cada pantalla anuncia "Cargando" una vez y marca la región como
 * ocupada; las piezas de dentro quedan ocultas para el lector, porque leer
 * quince cajas vacías no ayuda a nadie.
 */
import type { ReactNode } from "react";

/**
 * El envoltorio de cada pantalla de carga.
 *
 * `animate-pulse` va aquí y no en cada pieza para que todas parpadeen a la vez:
 * un montón de cajas latiendo cada una por su lado parece un error, no una
 * espera. Tailwind ya respeta `prefers-reduced-motion` en las animaciones.
 */
export function Cargando({
  children,
  etiqueta = "Cargando",
}: {
  children: ReactNode;
  etiqueta?: string;
}) {
  return (
    <div role="status" aria-busy="true" className="animate-pulse">
      <span className="sr-only">{etiqueta}</span>
      <div aria-hidden="true">{children}</div>
    </div>
  );
}

/** Una línea de texto. `ancho` va en clases de Tailwind para poder variarlo. */
export function Linea({ className = "h-4 w-40" }: { className?: string }) {
  return <div className={`rounded-md bg-surface ${className}`} />;
}

/** El título de la página: alto de `text-2xl font-semibold`, que es el que usan todas. */
export function Titulo({ className = "w-56" }: { className?: string }) {
  return <div className={`h-8 rounded-lg bg-surface ${className}`} />;
}

/** Una tarjeta con borde, como las del sitio. */
export function Tarjeta({
  className = "h-40",
  children,
}: {
  className?: string;
  children?: ReactNode;
}) {
  return (
    <div className={`rounded-2xl border border-border bg-surface ${className}`}>
      {children}
    </div>
  );
}

/** Las píldoras de filtro: la fila de pruebas del árbol, las de carreras. */
export function Pildoras({ cuantas = 5 }: { cuantas?: number }) {
  // Anchos distintos porque los nombres de las pruebas lo son. Todas iguales
  // se ve a la legua que es relleno.
  const anchos = ["w-24", "w-40", "w-44", "w-20", "w-52"];
  return (
    <div className="flex flex-wrap gap-2">
      {Array.from({ length: cuantas }, (_, i) => (
        <div
          key={i}
          className={`h-9 rounded-full border border-border bg-surface ${anchos[i % anchos.length]}`}
        />
      ))}
    </div>
  );
}

/** Una rejilla de tarjetas iguales. */
export function Rejilla({
  cuantas = 4,
  columnas = "grid-cols-2 lg:grid-cols-4",
  alto = "h-24",
}: {
  cuantas?: number;
  columnas?: string;
  alto?: string;
}) {
  return (
    <div className={`grid gap-4 ${columnas}`}>
      {Array.from({ length: cuantas }, (_, i) => (
        <Tarjeta key={i} className={alto} />
      ))}
    </div>
  );
}

/** Una lista de filas, para historiales y tablas. */
export function Filas({ cuantas = 5 }: { cuantas?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: cuantas }, (_, i) => (
        <div
          key={i}
          className="flex items-center justify-between rounded-xl border border-border bg-surface p-4"
        >
          <div className="space-y-2">
            <Linea className="h-4 w-48" />
            <Linea className="h-3 w-28" />
          </div>
          <Linea className="h-8 w-16" />
        </div>
      ))}
    </div>
  );
}
