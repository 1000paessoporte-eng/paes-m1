import katex from "katex";

/**
 * Renderiza el texto de enunciados, alternativas y explicaciones.
 *
 * Admite tres cosas, que es todo lo que necesitan las preguntas de la PAES:
 *  - Fórmulas LaTeX entre signos `$`, por ejemplo `$\frac{3}{4}$`.
 *  - Párrafos separados por línea en blanco.
 *  - Tablas simples en formato markdown (líneas que empiezan con `|`).
 *  - Negritas con `**texto**`, para destacar el nombre de una propiedad
 *    dentro de la teoría de una lección.
 *
 * Se usa KaTeX en lugar de imágenes para que las fórmulas se puedan copiar y
 * escalen bien en pantallas pequeñas.
 */

function escaparHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/** Convierte un fragmento con `$...$` en HTML, dejando el texto plano intacto. */
function renderizarConFormulas(texto: string): string {
  return texto
    .split(/(\$[^$]*\$)/g)
    .map((parte) => {
      if (parte.startsWith("$") && parte.endsWith("$") && parte.length > 2) {
        try {
          return katex.renderToString(parte.slice(1, -1), {
            throwOnError: false,
            displayMode: false,
            output: "html",
          });
        } catch {
          // Si la fórmula está mal escrita, se muestra tal cual en vez de
          // romper la pregunta completa.
          return escaparHtml(parte);
        }
      }
      // Las negritas se aplican DESPUÉS de escapar, así que el texto del
      // banco no puede inyectar etiquetas: los `<` ya se convirtieron en
      // `&lt;` y lo único que se reintroduce es el <strong> de acá.
      return negritas(escaparHtml(parte));
    })
    .join("");
}

/** `**así**` se convierte en negrita. Solo eso: no es un motor de markdown. */
function negritas(texto: string): string {
  return texto.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function esTabla(bloque: string): boolean {
  const lineas = bloque.trim().split("\n");
  return lineas.length >= 2 && lineas.every((l) => l.trim().startsWith("|"));
}

function celdas(linea: string): string[] {
  return linea
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((c) => c.trim());
}

function renderizarTabla(bloque: string): string {
  const lineas = bloque.trim().split("\n");
  const encabezado = celdas(lineas[0]);
  // La segunda línea es el separador (|---|---|) y se descarta.
  const filas = lineas.slice(2).map(celdas);

  const th = encabezado
    .map(
      (c) =>
        `<th class="border border-border px-3 py-1.5 bg-surface-hover font-semibold text-left">${renderizarConFormulas(c)}</th>`
    )
    .join("");

  const tbody = filas
    .map(
      (fila) =>
        `<tr>${fila
          .map((c) => `<td class="border border-border px-3 py-1.5">${renderizarConFormulas(c)}</td>`)
          .join("")}</tr>`
    )
    .join("");

  return `<div class="my-3 overflow-x-auto"><table class="border-collapse text-sm"><thead><tr>${th}</tr></thead><tbody>${tbody}</tbody></table></div>`;
}

function construirHtml(texto: string): string {
  return texto
    .split(/\n\s*\n/)
    .map((bloque) => {
      const limpio = bloque.trim();
      if (!limpio) return "";
      if (esTabla(limpio)) return renderizarTabla(limpio);
      const contenido = limpio
        .split("\n")
        .map((l) => renderizarConFormulas(l))
        .join("<br/>");
      return `<p class="my-2 first:mt-0 last:mb-0 leading-relaxed">${contenido}</p>`;
    })
    .join("");
}

interface Props {
  texto: string;
  className?: string;
  /** Usa `<span>` en vez de `<div>`, para textos que van dentro de una línea. */
  inline?: boolean;
}

export function TextoRico({ texto, className = "", inline = false }: Props) {
  const html = inline ? renderizarConFormulas(texto) : construirHtml(texto);

  // El HTML se genera exclusivamente a partir del banco de preguntas de la
  // propia API (no hay contenido escrito por usuarios), y todo el texto plano
  // pasa por escaparHtml antes de insertarse.
  if (inline) {
    return <span className={className} dangerouslySetInnerHTML={{ __html: html }} />;
  }
  return <div className={className} dangerouslySetInnerHTML={{ __html: html }} />;
}
