import Link from "next/link";

export default function NotFound() {
  return (
    <main className="bg-grid-fade relative flex flex-1 items-center justify-center overflow-hidden px-6 py-20">
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-1/3 -z-10 h-[320px] w-[560px] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-25 blur-[100px]"
        style={{
          background:
            "radial-gradient(closest-side, var(--accent), var(--accent-2), transparent)",
        }}
      />

      <div className="flex max-w-sm flex-col items-center rounded-2xl border border-border bg-surface px-6 py-12 text-center shadow-2xl shadow-black/20">
        <span className="text-5xl font-semibold tracking-tight text-gradient">404</span>
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
