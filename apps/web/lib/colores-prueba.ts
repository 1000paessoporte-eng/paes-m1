import type { Subject } from "@/lib/api";

/**
 * El color de cada prueba PAES.
 *
 * Es el mismo en el selector de ensayo y en el árbol de habilidades: el
 * estudiante reconoce dónde está sin leer el título, y al cambiar de prueba la
 * pantalla entera cambia con él.
 *
 * Los valores viven en globals.css como tokens, no acá, porque cada uno tiene
 * su variante clara y oscura. Este archivo solo dice qué token le toca a cada
 * prueba, y por eso puede importarse desde componentes servidor y cliente sin
 * arrastrar nada.
 *
 * REGLA: son colores de IDENTIDAD, nunca de ESTADO. No se usan donde el verde
 * ya significa "correcto" o el rojo "incorrecto" --la corrección de una
 * pregunta, el resultado de un ensayo--, porque ahí el color ES el dato.
 */
export const COLOR_PRUEBA: Record<Subject, string> = {
  lectora: "var(--prueba-lectora)",
  m1: "var(--prueba-m1)",
  m2: "var(--prueba-m2)",
  ciencias: "var(--prueba-ciencias)",
  historia: "var(--prueba-historia)",
};

/** Nombre corto, para chips y encabezados donde el largo no cabe. */
export const NOMBRE_CORTO: Record<Subject, string> = {
  lectora: "Lectora",
  m1: "Matemática M1",
  m2: "Matemática M2",
  ciencias: "Ciencias",
  historia: "Historia",
};

/**
 * Qué mide cada prueba, en una línea.
 *
 * Va en el selector porque elegir prueba es la primera decisión del ensayo y
 * el nombre solo no alcanza: "M1" y "M2" no le dicen nada a alguien de tercero
 * medio que todavía no sabe cuál le piden.
 */
export const QUE_MIDE: Record<Subject, string> = {
  lectora: "Textos y comprensión. La rinden todos.",
  m1: "Matemática de 7° a 2° medio. La rinden casi todos.",
  m2: "Suma 3° y 4° medio. Ingeniería, ciencias y salud.",
  ciencias: "Biología, física y química.",
  historia: "Historia, formación ciudadana y economía.",
};

/** Estilo en línea para pintar un elemento con el color de su prueba. */
export function estiloPrueba(subject: Subject) {
  return { "--color-prueba": COLOR_PRUEBA[subject] } as React.CSSProperties;
}
