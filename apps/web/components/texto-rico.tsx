import katex from "katex";

import { DESCRIPCION_FIGURA } from "@/lib/figuras";

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
  // Las comillas también. Antes solo se escapaban & < >, que basta para texto
  // suelto pero NO dentro de un atributo: `alt="..."` se cierra con una comilla
  // y a partir de ahí se pueden agregar atributos, `onerror` incluido. La
  // figura de una lección usa este escape en atributos, así que la diferencia
  // dejó de ser teórica.
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * El signo peso de un monto chileno NO abre una fórmula.
 *
 * `$12.000` es plata, no LaTeX. Se reconoce por el separador de miles, que
 * ninguna fórmula del banco usa: verificado sobre las 2.579 preguntas, cero
 * tramos con `$\d{1,3}\.\d{3}` contienen una orden de LaTeX.
 */
const PESO_CHILENO = /\$(?=\d{1,3}(?:\.\d{3})+)/g;

/** Marca interna para el peso literal. Un carácter de control no aparece en el
 *  banco, sobrevive a `escaparHtml` y KaTeX nunca lo produce. */
const MARCA_PESO = "\u0000";

/**
 * ¿Ese tramo entre `$` es de verdad una fórmula?
 *
 * Lo es si trae una orden de LaTeX (`\frac`, `\times`, `\rightarrow`), o si
 * es simbólico: sin ninguna palabra. Las fórmulas reales del banco son
 * `$-5$`, `$2+$`, `$g = 10$`, `$3H_2SO_4$` -- ninguna contiene una palabra de
 * tres letras. Los tramos que hoy se rompen son prosa castellana que quedó
 * atrapada entre dos montos: "24.000. ¿Cuántos participantes se necesitan
 * para que cada uno pague" salía en cursiva y con las palabras pegadas.
 */
function pareceFormula(cuerpo: string): boolean {
  // Una orden de LaTeX no deja dudas.
  if (cuerpo.includes("\\")) return true;
  // Un solo token sin espacios es notación, no una frase: `$NaOH$`, `$AA$`.
  // Sin esto, las fórmulas químicas caían en la regla de las palabras --NaOH
  // son cuatro letras-- y salían con los signos peso a la vista.
  if (!/\s/.test(cuerpo)) return true;
  // Con espacios, es fórmula solo si no hay ninguna palabra: `$g = 10$`,
  // `$2 + 3$`. La prosa castellana que queda atrapada entre dos montos
  // siempre las tiene.
  return !/\p{L}{3}/u.test(cuerpo);
}

/** Convierte un fragmento con `$...$` en HTML, dejando el texto plano intacto. */
function renderizarConFormulas(texto: string): string {
  return texto
    .replace(PESO_CHILENO, MARCA_PESO)
    .split(/(\$[^$]*\$)/g)
    .map((parte) => {
      if (
        parte.startsWith("$") &&
        parte.endsWith("$") &&
        parte.length > 2 &&
        pareceFormula(parte.slice(1, -1))
      ) {
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
    .join("")
    .replaceAll(MARCA_PESO, "$");
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

/**
 * Una figura dentro del texto: `[figura:/lecciones/geo-pitagoras.svg]`.
 *
 * La teoría de geometría no se puede explicar sin dibujo. "La hipotenusa es el
 * lado opuesto al ángulo recto" es una frase que solo entiende quien ya sabe
 * cuál es; con el triángulo al lado, se ve.
 *
 * Va por el texto y no por una columna nueva en `lessons` a propósito. Una
 * columna significa una migración, y en esta base una migración ya tumbó el
 * login dos veces (`03-trampas.md` §1). Además así la figura se pone DONDE
 * corresponde --entre dos párrafos, junto a la propiedad que ilustra-- y no
 * siempre al principio, que es lo único que permitiría un campo suelto. Y sirve
 * igual en el enunciado del ejemplo o en el error típico.
 */
const FIGURA = /^\[figura:\s*([^\]]+)\]$/;

/** Solo rutas del propio repositorio. El texto viene del banco y no de un
 *  usuario, pero esto acaba en dangerouslySetInnerHTML: se valida igual. */
const RUTA_SEGURA = /^\/(lecciones|preguntas)\/[a-z0-9-]+\.svg$/;

function renderizarFigura(ruta: string): string {
  if (!RUTA_SEGURA.test(ruta)) return "";
  const alt = DESCRIPCION_FIGURA[ruta] ?? "Figura de la lección";
  // Mismo trato que la figura de una pregunta: fondo blanco siempre, también
  // en modo oscuro. Son dibujos de línea negra sobre transparente, y en oscuro
  // desaparecerían. Ver components/exam/figura-pregunta.tsx.
  return (
    `<figure class="my-4 overflow-x-auto rounded-xl border border-border bg-white p-3">` +
    `<img src="${escaparHtml(ruta)}" alt="${escaparHtml(alt)}" loading="lazy" ` +
    `class="mx-auto h-auto max-w-full" />` +
    `</figure>`
  );
}

function construirHtml(texto: string): string {
  return texto
    .split(/\n\s*\n/)
    .map((bloque) => {
      const limpio = bloque.trim();
      if (!limpio) return "";
      const figura = limpio.match(FIGURA);
      if (figura) return renderizarFigura(figura[1].trim());
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
