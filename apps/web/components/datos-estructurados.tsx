/**
 * Datos estructurados (JSON-LD) para Google.
 *
 * Es lo que convierte un resultado de búsqueda en una ficha: la página dice
 * "esto es una organización", "esto es una lista de preguntas frecuentes", y
 * el buscador puede mostrarlo como tal en vez de un título y dos líneas.
 *
 * El escape de "<" no es decorativo: `JSON.stringify` no sanea nada, así que
 * un texto que traiga "</script>" cerraría la etiqueta e inyectaría HTML en la
 * página. Hoy todo lo que pasa por acá son constantes nuestras, pero el
 * contenido de las fichas sale de la base, y esa regla no se puede depender de
 * que quien agregue la próxima se acuerde.
 */
export function DatosEstructurados({ datos }: { datos: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(datos).replace(/</g, "\\u003c"),
      }}
    />
  );
}
