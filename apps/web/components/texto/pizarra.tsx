"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

/**
 * Espacio para hacer el desarrollo, como la hoja que dan en la prueba.
 *
 * En la PAES de verdad se entrega papel para desarrollar: nadie resuelve una
 * ecuación de segundo grado ni un problema de proporciones mirando la pantalla.
 * Acá no había dónde, y el estudiante terminaba con un cuaderno al lado --que
 * está bien-- o, peor, tratando de hacerlo de cabeza y equivocándose en la
 * aritmética de una pregunta que sabía resolver.
 *
 * ## Los trazos se guardan como datos, no como imagen
 *
 * Lo fácil sería guardar el canvas como PNG. Trae dos problemas: deshacer se
 * vuelve imposible --hay que rehacer todo el mapa de bits-- y al cambiar el
 * ancho de la ventana el dibujo se estira y se pixela.
 *
 * Acá cada trazo es la lista de puntos por donde pasó el lápiz. Deshacer es
 * quitar el último de la lista y volver a dibujar; cambiar de tamaño es volver
 * a dibujar con la escala nueva, nítido. Y ocupa menos que un PNG en el
 * almacenamiento del navegador.
 *
 * Los puntos van en fracción del ancho, no en píxeles. Así el desarrollo
 * sobrevive a girar el teléfono o a abrir el panel lateral, y como las dos
 * coordenadas usan la misma medida, nunca se deforma.
 */

type Punto = { x: number; y: number };
type Trazo = { puntos: Punto[]; grosor: number; borrar: boolean };

const GROSORES = [
  { id: "fino", etiqueta: "Fino", valor: 0.0022 },
  { id: "medio", etiqueta: "Medio", valor: 0.0042 },
] as const;

const GROSOR_BORRADOR = 0.028;
const ALTO = 320;

/** Nada a lo que suscribirse: solo sirve para saber si ya estamos en el
 *  navegador sin romper la hidratación. Fuera del componente para no
 *  resuscribir en cada render. */
const sinCambios = () => () => {};
const enCliente = () => true;
const enServidor = () => false;

function leerGuardado(clave: string): Trazo[] {
  if (typeof window === "undefined") return [];
  try {
    const guardado = window.localStorage.getItem(clave);
    return guardado ? (JSON.parse(guardado) as Trazo[]) : [];
  } catch {
    return [];
  }
}

export function Pizarra({ id }: { id: string }) {
  const clave = `pizarra:${id}`;

  // Lo dibujado antes se lee UNA vez, al construir el estado, no dentro de un
  // efecto: un efecto que sincroniza estado encadena renders. El componente
  // lleva `key` donde se usa, así que cambiar de pregunta lo vuelve a montar y
  // la lectura se repite sola.
  const [trazos, setTrazos] = useState<Trazo[]>(() => leerGuardado(clave));
  const [grosor, setGrosor] = useState<number>(GROSORES[0].valor);
  const [borrando, setBorrando] = useState(false);

  // Si ya había desarrollo guardado, la pizarra se abre sola: es la señal de
  // que en esta pregunta estabas trabajando.
  //
  // Pero eso NO puede decidirse en el servidor, que no tiene localStorage: si
  // el servidor pinta el botón y el navegador pinta la pizarra abierta, la
  // hidratación no cuadra. `montado` responde `false` mientras se hidrata y
  // `true` después, que es justo para lo que existe useSyncExternalStore.
  const montado = useSyncExternalStore(sinCambios, enCliente, enServidor);
  const [abiertaAMano, setAbiertaAMano] = useState<boolean | null>(null);
  const abierta = abiertaAMano ?? (montado && trazos.length > 0);
  const setAbierta = setAbiertaAMano;

  const lienzo = useRef<HTMLCanvasElement>(null);
  const dibujando = useRef(false);

  /** Vuelve a dibujarlo todo. Es la única función que toca el canvas. */
  const pintar = useCallback(() => {
    const cv = lienzo.current;
    if (!cv) return;
    const ctx = cv.getContext("2d");
    if (!ctx) return;

    // El canvas se dibuja a la resolución real de la pantalla y se muestra al
    // tamaño CSS. Sin esto, en una pantalla retina la línea sale borrosa.
    const escala = window.devicePixelRatio || 1;
    const ancho = cv.clientWidth;
    const alto = cv.clientHeight;
    if (cv.width !== ancho * escala || cv.height !== alto * escala) {
      cv.width = ancho * escala;
      cv.height = alto * escala;
    }
    ctx.setTransform(escala, 0, 0, escala, 0, 0);
    ctx.clearRect(0, 0, ancho, alto);

    const tinta = getComputedStyle(cv).getPropertyValue("color") || "#000";
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    for (const trazo of trazos) {
      if (trazo.puntos.length === 0) continue;
      // El borrador no borra píxeles a mano: dibuja "quitando", así que es un
      // trazo más de la lista y por eso se puede deshacer como cualquier otro.
      ctx.globalCompositeOperation = trazo.borrar ? "destination-out" : "source-over";
      ctx.strokeStyle = tinta;
      ctx.lineWidth = Math.max(1, trazo.grosor * ancho);

      ctx.beginPath();
      const [primero, ...resto] = trazo.puntos;
      ctx.moveTo(primero.x * ancho, primero.y * ancho);
      if (resto.length === 0) {
        // Un toque sin arrastrar es un punto, no nada.
        ctx.lineTo(primero.x * ancho + 0.1, primero.y * ancho);
      }
      for (const p of resto) ctx.lineTo(p.x * ancho, p.y * ancho);
      ctx.stroke();
    }
    ctx.globalCompositeOperation = "source-over";
  }, [trazos]);

  // Redibujar cuando cambian los trazos, y también cuando cambia el tamaño:
  // por eso los puntos se guardan en fracción y no en píxeles.
  useEffect(() => {
    if (!abierta) return;
    pintar();
    const cv = lienzo.current;
    if (!cv || typeof ResizeObserver === "undefined") return;
    const observador = new ResizeObserver(() => pintar());
    observador.observe(cv);
    return () => observador.disconnect();
  }, [abierta, pintar]);

  // Guardar.
  useEffect(() => {
    try {
      if (trazos.length > 0) {
        window.localStorage.setItem(clave, JSON.stringify(trazos));
      } else {
        window.localStorage.removeItem(clave);
      }
    } catch {
      // Sin espacio o en incógnito: el desarrollo sigue en pantalla.
    }
  }, [trazos, clave]);

  const puntoDe = (e: React.PointerEvent<HTMLCanvasElement>): Punto | null => {
    const cv = lienzo.current;
    if (!cv) return null;
    const caja = cv.getBoundingClientRect();
    if (caja.width === 0) return null;
    return {
      x: (e.clientX - caja.left) / caja.width,
      y: (e.clientY - caja.top) / caja.width,
    };
  };

  const empezar = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const p = puntoDe(e);
    if (!p) return;
    // Capturar el puntero: si no, al salirse del canvas el trazo se corta y
    // queda a medias en vez de seguir hasta que se suelta.
    e.currentTarget.setPointerCapture(e.pointerId);
    dibujando.current = true;
    setTrazos((prev) => [
      ...prev,
      { puntos: [p], grosor: borrando ? GROSOR_BORRADOR : grosor, borrar: borrando },
    ]);
  };

  const seguir = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!dibujando.current) return;
    const p = puntoDe(e);
    if (!p) return;
    setTrazos((prev) => {
      if (prev.length === 0) return prev;
      const ultimo = prev[prev.length - 1];
      return [...prev.slice(0, -1), { ...ultimo, puntos: [...ultimo.puntos, p] }];
    });
  };

  const soltar = () => {
    dibujando.current = false;
  };

  if (!abierta) {
    return (
      <button
        type="button"
        onClick={() => setAbierta(true)}
        className="mt-4 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-muted transition-colors hover:bg-surface-hover hover:text-foreground"
      >
        Hacer el desarrollo
      </button>
    );
  }

  return (
    <div className="mt-4 rounded-xl border border-border bg-background">
      <div
        role="toolbar"
        aria-label="Herramientas del desarrollo"
        className="flex flex-wrap items-center gap-1.5 border-b border-border px-3 py-2"
      >
        <span className="mr-1 text-xs text-muted">Desarrollo</span>

        {GROSORES.map((g) => {
          const activo = !borrando && grosor === g.valor;
          return (
            <button
              key={g.id}
              type="button"
              onClick={() => {
                setBorrando(false);
                setGrosor(g.valor);
              }}
              aria-pressed={activo}
              className={
                "rounded-full border px-3 py-1 text-xs font-medium transition-colors " +
                (activo
                  ? "border-foreground bg-surface-hover text-foreground"
                  : "border-border text-muted hover:bg-surface-hover hover:text-foreground")
              }
            >
              {g.etiqueta}
            </button>
          );
        })}

        <button
          type="button"
          onClick={() => setBorrando((b) => !b)}
          aria-pressed={borrando}
          className={
            "rounded-full border px-3 py-1 text-xs font-medium transition-colors " +
            (borrando
              ? "border-foreground bg-surface-hover text-foreground"
              : "border-border text-muted hover:bg-surface-hover hover:text-foreground")
          }
        >
          Goma
        </button>

        <button
          type="button"
          onClick={() => setTrazos((p) => p.slice(0, -1))}
          disabled={trazos.length === 0}
          className="rounded-full border border-border px-3 py-1 text-xs text-muted transition-colors hover:bg-surface-hover hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
        >
          Deshacer
        </button>

        <button
          type="button"
          onClick={() => setTrazos([])}
          disabled={trazos.length === 0}
          className="rounded-full border border-border px-3 py-1 text-xs text-muted transition-colors hover:bg-surface-hover hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
        >
          Limpiar
        </button>

        <button
          type="button"
          onClick={() => setAbierta(false)}
          className="ml-auto rounded-full px-2 py-1 text-xs text-muted transition-colors hover:text-foreground"
        >
          Cerrar
        </button>
      </div>

      {/* `touch-action: none` es lo que permite dibujar con el dedo: sin eso,
          arrastrar sobre el canvas hace scroll de la página y no se puede
          escribir nada en el teléfono. */}
      <canvas
        ref={lienzo}
        onPointerDown={empezar}
        onPointerMove={seguir}
        onPointerUp={soltar}
        onPointerCancel={soltar}
        style={{ height: ALTO, touchAction: "none" }}
        className="w-full cursor-crosshair rounded-b-xl text-foreground"
        aria-label="Espacio para hacer el desarrollo"
      />
    </div>
  );
}
