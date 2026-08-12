export default function LoginPage() {
  return (
    <main className="flex flex-1 items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-xl border border-border bg-surface p-6">
        <h1 className="text-lg font-semibold">Inicia sesión</h1>
        <p className="mt-1 text-sm text-muted">
          Continúa tu progreso en el árbol de habilidades.
        </p>
        {/* TODO: formulario de auth (email + provider) */}
      </div>
    </main>
  );
}
