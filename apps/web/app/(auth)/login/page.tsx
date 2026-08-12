export default function LoginPage() {
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

      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-6 shadow-2xl shadow-black/20">
        <span
          className="flex h-9 w-9 items-center justify-center rounded-lg text-xs font-bold text-white"
          style={{
            background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
          }}
        >
          M1
        </span>
        <h1 className="mt-4 text-lg font-semibold">Inicia sesión</h1>
        <p className="mt-1 text-sm text-muted">
          Continúa tu progreso en el árbol de habilidades.
        </p>

        {/* TODO: conectar a auth real (email + provider) */}
        <form className="mt-6 flex flex-col gap-3">
          <label className="flex flex-col gap-1.5 text-left">
            <span className="text-xs font-medium text-muted">Correo</span>
            <input
              type="email"
              placeholder="tu@correo.com"
              disabled
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted/60 disabled:cursor-not-allowed"
            />
          </label>
          <label className="flex flex-col gap-1.5 text-left">
            <span className="text-xs font-medium text-muted">Contraseña</span>
            <input
              type="password"
              placeholder="••••••••"
              disabled
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted/60 disabled:cursor-not-allowed"
            />
          </label>
          <button
            type="button"
            disabled
            className="btn-glow mt-2 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground disabled:cursor-not-allowed disabled:opacity-60"
          >
            Continuar
          </button>
        </form>
        <p className="mt-4 text-center text-xs text-muted">
          Autenticación en construcción.
        </p>
      </div>
    </main>
  );
}
