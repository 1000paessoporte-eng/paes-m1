/**
 * La marca de 1000paes.
 *
 * El nombre ya traía el dibujo: «1000» tiene tres ceros y un cero es
 * exactamente la forma de una burbuja del cartón de respuestas. El logotipo
 * escribe el nombre y dibuja el objeto en el mismo gesto, con **una sola
 * burbuja rellena** —la respuesta marcada.
 *
 * Antes de esto había tres marcas distintas conviviendo: un cuadrado con
 * degradado y las siglas «1K» en el encabezado, un círculo con «1000» en el
 * icono de iOS, y un triángulo blanco sobre negro en el favicon que no
 * aparecía en ninguna otra parte del producto. Ahora los tres salen de acá.
 *
 * Dos decisiones que conviene no revertir sin pensar:
 *
 * 1. **La marca es acromática.** En este producto el color significa "qué
 *    prueba es"; si la marca tomara uno, pisaría ese significado. Todo se
 *    dibuja con `currentColor`, así que hereda el color del texto y funciona
 *    igual en claro y en oscuro sin una sola regla de tema.
 * 2. **El dibujo cambia según el tamaño.** El relleno hecho a mano
 *    (`CONTORNO_A_MANO`) solo se usa de 64 px para arriba, que es donde el
 *    temblor del borde se ve. Más abajo el borde irregular se convierte en
 *    ruido, así que la burbuja vuelve a ser un círculo y el anillo engorda
 *    para no desaparecer.
 */

/**
 * Contorno de una burbuja rellenada con lápiz: un círculo de radio irregular
 * suavizado con bézier, sobre un lienzo de 120×120 centrado en (60, 60).
 *
 * Va como geometría y no como filtro SVG a propósito: `feTurbulence` y
 * `feDisplacementMap` no existen en Satori, que es lo que genera los iconos
 * de `app/icon.tsx` y `app/apple-icon.tsx`. Un filtro habría funcionado en el
 * navegador y habría salido un círculo liso en el icono de la app.
 */
export const CONTORNO_A_MANO =
  "M101.11 75.01 C99.40 81.32 97.11 88.75 92.72 93.61 C88.33 98.47 81.20 102.22 74.79 " +
  "104.17 C68.39 106.11 60.74 106.48 54.28 105.29 C47.83 104.09 41.86 100.42 36.05 " +
  "97.00 C30.25 93.57 23.33 90.12 19.43 84.74 C15.52 79.36 13.04 71.44 12.62 64.70 " +
  "C12.21 57.95 14.36 50.53 16.93 44.28 C19.51 38.03 23.21 31.55 28.05 27.18 C32.89 " +
  "22.82 39.75 19.70 45.96 18.10 C52.18 16.49 58.95 16.85 65.36 17.54 C71.78 18.23 " +
  "78.76 19.16 84.45 22.22 C90.14 25.28 96.42 30.32 99.51 35.90 C102.60 41.49 102.72 " +
  "49.22 102.98 55.74 C103.25 62.26 102.82 68.70 101.11 75.01Z";

/** Debajo de esto el borde irregular se lee como suciedad, no como lápiz. */
const MINIMO_PARA_TRAZO_A_MANO = 64;

/** El anillo impreso del cartón: fino en grande, grueso en chico. */
function grosorAnillo(tamano: number): number {
  if (tamano >= 64) return 5;
  if (tamano >= 28) return 8;
  return 12;
}

/**
 * Cuánto se ve el anillo impreso.
 *
 * En grande el anillo es un gris tenue del cartón y basta con 0,34. En chico
 * ese mismo valor lo convierte en un fantasma, y como los anillos SON los dos
 * primeros ceros del nombre, el logotipo pasaba a leerse «1··paes». Se sube
 * para que los ceros sigan siendo ceros.
 */
function opacidadAnillo(tamano: number): number {
  return tamano >= 28 ? 0.34 : 0.55;
}

/**
 * El radio del grafito.
 *
 * En chico se achica un poco para que asome el anillo por debajo: si el
 * relleno lo tapa entero, la burbuja marcada deja de parecer una burbuja y se
 * lee como un punto.
 */
function radioRelleno(tamano: number): number {
  return tamano >= 28 ? 42 : 38;
}

/**
 * La burbuja suelta: el cero relleno, extraído del logotipo.
 *
 * Es el símbolo de la marca — favicon, icono de app, avatar. Hereda el color
 * del texto, así que sobre papel se dibuja en grafito y sobre grafito en papel.
 */
export function Burbuja({
  tamano = 28,
  llena = true,
  className,
  titulo,
}: {
  tamano?: number;
  llena?: boolean;
  className?: string;
  titulo?: string;
}) {
  const aMano = llena && tamano >= MINIMO_PARA_TRAZO_A_MANO;
  return (
    <svg
      width={tamano}
      height={tamano}
      viewBox="0 0 120 120"
      className={className}
      role={titulo ? "img" : undefined}
      aria-label={titulo}
      aria-hidden={titulo ? undefined : true}
    >
      <circle
        cx="60"
        cy="60"
        r="46"
        fill="none"
        stroke="currentColor"
        strokeWidth={grosorAnillo(tamano)}
        opacity={opacidadAnillo(tamano)}
      />
      {llena &&
        (aMano ? (
          <path d={CONTORNO_A_MANO} fill="currentColor" />
        ) : (
          <circle cx="60" cy="60" r={radioRelleno(tamano)} fill="currentColor" />
        ))}
    </svg>
  );
}

/**
 * El logotipo: «1000paes» con los ceros dibujados como burbujas.
 *
 * Los tamaños van en `em` para que la marca escale con el `font-size` que le
 * toque: el encabezado la usa a 16 px y una portada podría usarla a 64 sin
 * tocar nada acá.
 */
export function Logotipo({
  className,
  tamanoPx = 16,
}: {
  className?: string;
  /** Se usa solo para elegir el grosor del anillo, no fija el tamaño. */
  tamanoPx?: number;
}) {
  // 0,86 del cuerpo: los ceros tienen que igualar la altura de la "1" y de
  // la "p", no quedar por debajo. A 0,74 se leían como puntos pequeños.
  const cero = Math.round(tamanoPx * 0.86);
  return (
    <span
      className={className}
      style={{
        display: "inline-flex",
        alignItems: "center",
        lineHeight: 1,
        letterSpacing: "-0.02em",
      }}
      aria-label="1000paes"
      role="img"
    >
      <span aria-hidden>1</span>
      <span
        aria-hidden
        style={{ display: "inline-flex", alignItems: "center", gap: "0.07em", margin: "0 0.1em" }}
      >
        <Burbuja tamano={cero} llena={false} />
        <Burbuja tamano={cero} llena={false} />
        <Burbuja tamano={cero} llena />
      </span>
      <span aria-hidden>paes</span>
    </span>
  );
}
