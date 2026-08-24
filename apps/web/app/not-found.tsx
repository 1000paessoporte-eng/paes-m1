import type { Metadata } from "next";
import Link from "next/link";

/**
 * Sin esto, la pestaña de una página inexistente decía "Ensayos PAES gratis con
 * puntaje oficial — 1000paes": el título de la portada, heredado del layout. El
 * que llega a un enlace roto ve en su pestaña el mismo rótulo que si hubiera
 * llegado bien, y en el historial le quedan dos entradas idénticas.
 */
export const metadata: Metadata = {
  title: "Esta página no existe",
  robots: { index: false, follow: true },
};

export default function NotFound() {
  return (
    <main className="flex flex-1 items-center justify-center px-6 py-20">
      <div className="flex max-w-sm flex-col items-center rounded-2xl border border-border bg-surface px-6 py-12 text-center shadow-xl shadow-foreground/5">
        <span className="text-5xl font-semibold tracking-tight text-accent">404</span>
        <h1 className="mt-3 text-lg font-semibold">Esta página no existe</h1>
        <p className="mt-2 text-sm text-muted">
          El nodo que buscas no está en el árbol. Revisa la dirección o vuelve
          al inicio.
        </p>
        <Link
          href="/"
          className="btn-glow mt-6 rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
        >
          Volver al inicio
        </Link>
      </div>
    </main>
  );
}
