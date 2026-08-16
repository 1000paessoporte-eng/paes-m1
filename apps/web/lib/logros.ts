/**
 * Logros del estudiante: qué son y cuándo se consiguen.
 *
 * Regla que ordena este archivo: **cada logro corresponde a algo que el
 * estudiante hizo de verdad**, calculado con los datos que ya devuelve la API
 * (ensayos rendidos, racha, precisión, nodos dominados, mejor puntaje). No hay
 * logros de adorno. Una medalla que se regala no motiva a nadie: la segunda
 * vez que aparece ya no significa nada.
 *
 * Vive fuera del componente y sin `"use client"` a propósito: el panel es un
 * Server Component y necesita llamar esta función durante el render. Un módulo
 * marcado como cliente no se puede invocar desde el servidor, solo renderizar.
 */

export interface Logro {
  id: string;
  titulo: string;
  requisito: string;
  icono: string;
  conseguido: boolean;
}

export function calcularLogros({
  ensayos,
  racha,
  precision,
  nodosDominados,
  mejorPuntaje,
}: {
  ensayos: number;
  racha: number;
  precision: number | null;
  nodosDominados: number;
  mejorPuntaje: number | null;
}): Logro[] {
  return [
    {
      id: "primer-ensayo",
      titulo: "Primer ensayo",
      requisito: "Rinde tu primer ensayo",
      icono: "🎯",
      conseguido: ensayos >= 1,
    },
    {
      id: "cinco-ensayos",
      titulo: "Constancia",
      requisito: "Rinde 5 ensayos",
      icono: "📚",
      conseguido: ensayos >= 5,
    },
    {
      id: "racha-3",
      titulo: "3 días",
      requisito: "Practica 3 días seguidos",
      icono: "🔥",
      conseguido: racha >= 3,
    },
    {
      id: "racha-7",
      titulo: "7 días",
      requisito: "Practica 7 días seguidos",
      icono: "⚡",
      conseguido: racha >= 7,
    },
    {
      id: "precision-70",
      titulo: "Puntería",
      requisito: "Llega a 70% de aciertos",
      icono: "✅",
      conseguido: precision != null && precision >= 0.7,
    },
    {
      id: "nodos-5",
      titulo: "5 temas",
      requisito: "Domina 5 nodos del árbol",
      icono: "🌱",
      conseguido: nodosDominados >= 5,
    },
    {
      id: "puntaje-700",
      titulo: "700 pts",
      requisito: "Alcanza 700 puntos estimados",
      icono: "🏔",
      conseguido: mejorPuntaje != null && mejorPuntaje >= 700,
    },
    {
      id: "puntaje-850",
      titulo: "850 pts",
      requisito: "Alcanza 850 puntos estimados",
      icono: "👑",
      conseguido: mejorPuntaje != null && mejorPuntaje >= 850,
    },
  ];
}
