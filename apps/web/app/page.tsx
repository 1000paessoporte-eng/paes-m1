import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
      <span className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted">
        PAES M1 · Competencia Matemática
      </span>
      <h1 className="max-w-2xl text-4xl font-semibold tracking-tight sm:text-5xl">
        Domina la M1 con un árbol de habilidades que se adapta a ti
      </h1>
      <p className="max-w-xl text-balance text-muted">
        Modo examen de alto rendimiento, autopsia del error pregunta a
        pregunta y un dashboard que muestra exactamente dónde enfocar tu
        estudio.
      </p>
      <div className="flex gap-3">
        <Link
          href="/arbol"
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-colors hover:opacity-90"
        >
          Empezar ahora
        </Link>
        <Link
          href="/login"
          className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-surface-hover"
        >
          Iniciar sesión
        </Link>
      </div>
    </main>
  );
}
