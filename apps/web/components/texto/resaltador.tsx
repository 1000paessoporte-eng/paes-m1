"use client";

import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

/**
 * Destacar ideas en un texto, como se hace en el papel.
 *
 * En la PAES de verdad el estudiante raya el texto: subraya la idea central,
 * marca el conector que cambia el sentido, y vuelve ahí cuando la pregunta se
 * lo pide. En pantalla no tenía cómo, y releer un texto de dos mil palabras
 * buscando algo que ya encontró es exactamente lo que el papel le ahorraba.
 *
 * ## Por qué no se envuelve el texto en <mark>
 *
 * Lo obvio sería rodear la selección con una etiqueta. No sirve acá: el texto
 * llega como HTML ya construido --fórmulas de KaTeX, tablas, negritas-- y una
 * selección casi nunca respeta esos límites. Envolver "desde la mitad de una
 * negrita hasta dentro de una fórmula" obliga a partir nodos, y al borrar hay
 * que recomponer lo que se partió. Se rompe el KaTeX y se rompe la tabla.
 *
 * Se usa la **CSS Custom Highlight API**: se le entregan rangos al navegador y
 * él los pinta encima. El DOM no se toca ni una vez, así que no hay nada que
 * recomponer al borrar y el HTML original queda intacto.
 *
 * Donde esa API no existe (navegadores viejos de sala de computación) la barra
 * no aparece: es mejor no ofrecer la herramienta que ofrecerla rota.
 *
 * ## Qué se guarda
 *
 * Un rango del DOM es un objeto vivo, no se puede guardar. Lo que se guarda son
 * dos números por marca --desde qué carácter hasta qué carácter, contando sobre
 * el texto visible-- y con eso se reconstruye el rango al volver. Va a
 * `localStorage` por texto: quien recarga la página en mitad de un ensayo no
 * pierde lo que llevaba marcado.
 */

export type ColorMarca = "amarillo" | "verde" | "rosa";

type Marca = { inicio: number; fin: number; color: ColorMarca };

const COLORES: { id: ColorMarca; nombre: string; clase: string }[] = [
  { id: "amarillo", nombre: "Amarillo", clase: "bg-[#fde68a]" },
  { id: "verde", nombre: "Verde", clase: "bg-[#bbf7d0]" },
  { id: "rosa", nombre: "Rosa", clase: "bg-[#fbcfe8]" },
];

/**
 * El registro de resaltados es global del navegador y los nombres del CSS son
 * fijos, así que dos textos en la misma pantalla se pisarían. Cada instancia
 * deja aquí sus rangos y se publica la suma.
 */
const porInstancia = new Map<string, Map<ColorMarca, Range[]>>();

/** Fuera del componente: si se creara en cada render, React se resuscribiría
 *  cada vez. El dato no cambia nunca, así que no hay a qué suscribirse. */
const sinCambios = () => () => {};
const hayApi = () =>
  Boolean((window.CSS as unknown as { highlights?: unknown })?.highlights);
const noEnServidor = () => false;

function publicar() {
  const CSSGlobal = window.CSS as unknown as {
    highlights?: Map<string, unknown>;
  };
  if (!CSSGlobal?.highlights) return;

  for (const { id } of COLORES) {
    const todos: Range[] = [];
    for (const porColor of porInstancia.values()) {
      todos.push(...(porColor.get(id) ?? []));
    }
    const nombre = `marca-${id}`;
    if (todos.length === 0) {
      CSSGlobal.highlights.delete(nombre);
    } else {
      const Constructor = (window as unknown as {
        Highlight: new (...rangos: Range[]) => unknown;
      }).Highlight;
      CSSGlobal.highlights.set(nombre, new Constructor(...todos));
    }
  }
}

/**
 * Los nodos de texto visibles, en orden.
 *
 * KaTeX escribe cada fórmula DOS veces: una en MathML para los lectores de
 * pantalla y otra visible. Si se cuentan las dos, los números dejan de
 * corresponder con lo que la persona ve y las marcas aparecen corridas. Se
 * salta la copia oculta.
 */
function nodosVisibles(raiz: HTMLElement): Text[] {
  const salida: Text[] = [];
  const paseo = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT, {
    acceptNode(nodo) {
      const padre = nodo.parentElement;
      if (!padre) return NodeFilter.FILTER_REJECT;
      if (padre.closest(".katex-mathml")) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    },
  });
  let actual = paseo.nextNode();
  while (actual) {
    salida.push(actual as Text);
    actual = paseo.nextNode();
  }
  return salida;
}

/** De una posición del DOM al número de carácter dentro del texto completo. */
function aDesplazamiento(raiz: HTMLElement, nodo: Node, offset: number): number | null {
  const nodos = nodosVisibles(raiz);
  let contados = 0;
  for (const n of nodos) {
    if (n === nodo) return contados + offset;
    contados += n.data.length;
  }
  return null;
}

/** Y de vuelta: de dos números a un rango que el navegador pueda pintar. */
function aRango(raiz: HTMLElement, inicio: number, fin: number): Range | null {
  const nodos = nodosVisibles(raiz);
  let contados = 0;
  let desde: { nodo: Text; offset: number } | null = null;
  let hasta: { nodo: Text; offset: number } | null = null;

  for (const n of nodos) {
    const largo = n.data.length;
    if (!desde && inicio <= contados + largo) {
      desde = { nodo: n, offset: Math.max(0, inicio - contados) };
    }
    if (!hasta && fin <= contados + largo) {
      hasta = { nodo: n, offset: Math.max(0, fin - contados) };
      break;
    }
    contados += largo;
  }
  if (!desde || !hasta) return null;

  const rango = document.createRange();
  try {
    rango.setStart(desde.nodo, desde.offset);
    rango.setEnd(hasta.nodo, hasta.offset);
  } catch {
    return null;
  }
  return rango;
}

/** Quita de `marcas` el tramo [inicio, fin), partiendo las que lo crucen. */
function borrarTramo(marcas: Marca[], inicio: number, fin: number): Marca[] {
  const salida: Marca[] = [];
  for (const m of marcas) {
    if (m.fin <= inicio || m.inicio >= fin) {
      salida.push(m);
      continue;
    }
    // La goma parte por el medio: quedan los dos extremos que sobreviven.
    if (m.inicio < inicio) salida.push({ ...m, fin: inicio });
    if (m.fin > fin) salida.push({ ...m, inicio: fin });
  }
  return salida;
}

/** Une las marcas del mismo color que se tocan, para no acumular trozos. */
function fundir(marcas: Marca[]): Marca[] {
  const ordenadas = [...marcas].sort((a, b) => a.inicio - b.inicio);
  const salida: Marca[] = [];
  for (const m of ordenadas) {
    const ultima = salida[salida.length - 1];
    if (ultima && ultima.color === m.color && m.inicio <= ultima.fin) {
      ultima.fin = Math.max(ultima.fin, m.fin);
    } else {
      salida.push({ ...m });
    }
  }
  return salida.filter((m) => m.fin > m.inicio);
}

export function Resaltador({
  id,
  children,
  className = "",
}: {
  /** Identifica el texto para poder recuperar sus marcas al volver. */
  id: string;
  children: React.ReactNode;
  className?: string;
}) {
  const contenedor = useRef<HTMLDivElement>(null);
  const instancia = useId();
  const [herramienta, setHerramienta] = useState<ColorMarca | "goma" | null>(null);

  const clave = `marcas:${id}`;

  // ¿Existe la API en este navegador? Es un dato del navegador que hay que leer
  // sin romper la hidratación: en el servidor no hay `window`, así que se
  // responde `false` y React vuelve a preguntar ya en el cliente. Esto es
  // exactamente para lo que existe useSyncExternalStore; hacerlo con un
  // useState dentro de un efecto provoca un render en cascada.
  const disponible = useSyncExternalStore(sinCambios, hayApi, noEnServidor);

  // Lo marcado la vez anterior se lee UNA vez, al construir el estado.
  //
  // El componente lleva `key={id}` donde se usa, así que cambiar de texto lo
  // vuelve a montar y esta lectura se repite sola: no hace falta un efecto que
  // sincronice, que es lo que encadenaría renders.
  const [marcas, setMarcas] = useState<Marca[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const guardado = window.localStorage.getItem(clave);
      return guardado ? (JSON.parse(guardado) as Marca[]) : [];
    } catch {
      // Modo incógnito o almacenamiento lleno: se sigue sin marcas previas.
      return [];
    }
  });

  // Pintar y guardar en cada cambio.
  useEffect(() => {
    const raiz = contenedor.current;
    if (!raiz || !disponible) return;

    const porColor = new Map<ColorMarca, Range[]>();
    for (const m of marcas) {
      const rango = aRango(raiz, m.inicio, m.fin);
      if (!rango) continue;
      const lista = porColor.get(m.color) ?? [];
      lista.push(rango);
      porColor.set(m.color, lista);
    }
    porInstancia.set(instancia, porColor);
    publicar();

    try {
      if (marcas.length > 0) {
        window.localStorage.setItem(clave, JSON.stringify(marcas));
      } else {
        window.localStorage.removeItem(clave);
      }
    } catch {
      // Si no se puede guardar, las marcas siguen vivas en pantalla.
    }
  }, [marcas, disponible, instancia, clave]);

  // Al desmontar, dejar de pintar lo de este texto.
  useEffect(() => {
    return () => {
      porInstancia.delete(instancia);
      publicar();
    };
  }, [instancia]);

  const aplicar = useCallback(() => {
    if (!herramienta) return;
    const raiz = contenedor.current;
    if (!raiz) return;

    const seleccion = window.getSelection();
    if (!seleccion || seleccion.isCollapsed || seleccion.rangeCount === 0) return;

    const rango = seleccion.getRangeAt(0);
    if (!raiz.contains(rango.commonAncestorContainer)) return;

    const inicio = aDesplazamiento(raiz, rango.startContainer, rango.startOffset);
    const fin = aDesplazamiento(raiz, rango.endContainer, rango.endOffset);
    if (inicio === null || fin === null || fin <= inicio) return;

    setMarcas((previas) => {
      // Marcar encima de otro color lo reemplaza, en vez de superponerlos:
      // dos resaltados sobre el mismo texto no se ven, se ensucian.
      const limpias = borrarTramo(previas, inicio, fin);
      if (herramienta === "goma") return fundir(limpias);
      return fundir([...limpias, { inicio, fin, color: herramienta }]);
    });

    seleccion.removeAllRanges();
  }, [herramienta]);

  if (!disponible) {
    // Sin la API, el texto se muestra tal cual y sin barra: una herramienta
    // que no funciona es peor que no tenerla.
    return <div className={className}>{children}</div>;
  }

  return (
    <div className={className}>
      <div
        role="toolbar"
        aria-label="Destacar el texto"
        className="mb-3 flex flex-wrap items-center gap-1.5 border-b border-border pb-3"
      >
        <span className="mr-1 text-xs text-muted">Destacar</span>

        {COLORES.map((c) => {
          const activo = herramienta === c.id;
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => setHerramienta(activo ? null : c.id)}
              aria-pressed={activo}
              title={`Destacar en ${c.nombre.toLowerCase()}`}
              className={
                "size-7 rounded-full border transition-[box-shadow,border-color] " +
                c.clase +
                (activo
                  ? " border-foreground ring-2 ring-foreground/25"
                  : " border-border-strong hover:border-foreground/50")
              }
            >
              <span className="sr-only">{c.nombre}</span>
            </button>
          );
        })}

        <button
          type="button"
          onClick={() => setHerramienta(herramienta === "goma" ? null : "goma")}
          aria-pressed={herramienta === "goma"}
          className={
            "ml-1 rounded-full border px-3 py-1 text-xs font-medium transition-colors " +
            (herramienta === "goma"
              ? "border-foreground bg-surface-hover text-foreground"
              : "border-border text-muted hover:bg-surface-hover hover:text-foreground")
          }
        >
          Goma
        </button>

        {marcas.length > 0 && (
          <button
            type="button"
            onClick={() => setMarcas([])}
            className="rounded-full border border-border px-3 py-1 text-xs text-muted transition-colors hover:bg-surface-hover hover:text-foreground"
          >
            Borrar todo
          </button>
        )}

        {herramienta && (
          <span className="ml-auto text-xs text-muted">
            {herramienta === "goma"
              ? "Selecciona lo que quieras borrar"
              : "Selecciona el texto que quieras destacar"}
          </span>
        )}
      </div>

      {/* `onMouseUp` y `onTouchEnd`: en el teléfono no hay mouseup al soltar la
          selección, y esta prueba se rinde tanto en celular como en sala. */}
      <div
        ref={contenedor}
        onMouseUp={aplicar}
        onTouchEnd={aplicar}
        className={herramienta ? "cursor-text" : undefined}
      >
        {children}
      </div>
    </div>
  );
}
