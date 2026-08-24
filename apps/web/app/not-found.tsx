import type { Metadata } from "next";
import Link from "next/link";

/**
 * El título decía "Ensayos PAES gratis con puntaje oficial — 1000paes", el de
 * la portada: quien caía en una dirección rota veía en la pestaña el nombre de
 * una página que no estaba mirando.
 */
export const metadata: Metadata = {
  title: "Página no encontrada",
  robots: { index: false, follow: true },
};

/**
 * Las salidas importan más que el mensaje. Antes había una sola —"Volver al
 * inicio"—, que en un sitio cuyo tráfico entra por 1.855 fichas de carrera
 * deja a la persona más lejos de lo que buscaba, no más cerca. Una dirección
 * rota suele ser una ficha mal escrita o un enlace viejo, así que las tres
 * salidas apuntan a lo que probablemente venía a hacer.
 */
const SALIDAS = [
  {
    href: "/carreras",
    titulo: "Buscar una carrera",
    detalle: "Las ponderaciones oficiales de 1.855 carreras",
  },
  {
    href: "/demo",
    titulo: "Probar sin cuenta",
    detalle: "Cinco preguntas reales, sin registrarse",
  },
  {
    href: "/aprender",
    titulo: "Ver las lecciones",
    detalle: "Los 53 temas del temario, con ejercicios resueltos",
  },
];

export default function NotFound() {
  return (
    <main className="flex flex-1 items-center justify-center px-6 py-20">
      <div className="w-full max-w-md rounded-2xl border border-border bg-surface px-6 py-10 shadow-xl shadow-foreground/5">
        <div className="flex flex-col items-center text-center">
          <span className="text-5xl font-semibold tracking-tight text-accent">404</span>
          <h1 className="mt-3 text-lg font-semibold">Esta página no existe</h1>
          <p className="mt-2 text-sm text-muted">
            El nodo que buscas no está en el árbol. Revisa la dirección, o sigue
            por acá.
          </p>
        </div>

        <ul className="mt-7 grid gap-2">
          {SALIDAS.map((salida) => (
            <li key={salida.href}>
              <Link
                href={salida.href}
                className="block rounded-lg border border-border px-4 py-3 transition-colors hover:bg-surface-hover"
              >
                <span className="block text-sm font-medium">{salida.titulo}</span>
                <span className="block text-xs text-muted">{salida.detalle}</span>
              </Link>
            </li>
          ))}
        </ul>

        <Link
          href="/"
          className="mt-4 block text-center text-sm text-muted underline underline-offset-4 hover:text-foreground"
        >
          Volver al inicio
        </Link>
      </div>
    </main>
  );
}
