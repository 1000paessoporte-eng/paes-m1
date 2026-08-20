import Link from "next/link";
import { BarraProgreso } from "@/components/ui/barra-progreso";

/**
 * El plan Pro dentro del panel, para quien está en el plan Gratis.
 *
 * Un aviso que aparece y se cierra se olvida; este queda. La diferencia
 * importa porque la decisión de pagar rara vez se toma en el momento en que
 * uno ve el anuncio: se toma más tarde, cuando el tope estorba de verdad, y
 * entonces conviene que la salida esté a la vista y no haya que recordarla.
 *
 * Muestra el consumo real antes que el precio. "Llevas 3 de 4 ensayos" es
 * información sobre la propia situación; "$9.990 al mes" sin contexto es
 * publicidad. El orden decide cuál de las dos parece.
 */
export function ProModulo({
  usados,
  limite,
}: {
  usados: number;
  limite: number | null;
}) {
  const restantes = limite != null ? Math.max(0, limite - usados) : null;
  const sinCupo = restantes === 0;

  return (
    <section
      className="card-panel p-5"
      aria-labelledby="h-pro"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="h-pro" className="font-semibold tracking-tight">
          Plan Pro
        </h2>
        <span className="text-xs font-medium text-muted">$9.990 al mes</span>
      </div>

      {limite != null ? (
        <div className="mt-3">
          <div className="flex items-baseline justify-between gap-3 text-sm">
            <span className="tabular-nums">
              <strong>{usados}</strong>
              <span className="text-muted"> de {limite} ensayos este mes</span>
            </span>
            <span
              className={
                "shrink-0 text-xs font-medium " +
                (sinCupo ? "text-accent-warm-strong" : "text-muted")
              }
            >
              {sinCupo ? "Sin cupo" : `Te quedan ${restantes}`}
            </span>
          </div>
          <div className="mt-2">
            <BarraProgreso
              porcentaje={(usados / limite) * 100}
              color={sinCupo ? "var(--accent-warm)" : "var(--accent)"}
              etiqueta={`${usados} de ${limite} ensayos usados este mes`}
              alto="h-1.5"
            />
          </div>
        </div>
      ) : (
        <p className="mt-3 text-sm text-muted">
          Ensayos sin límite de las cinco pruebas, comparación por eje y hasta
          10 preferencias en Mi meta.
        </p>
      )}

      <ul className="mt-4 flex flex-col gap-1.5 text-xs text-muted">
        {[
          "Ensayos sin límite, de las cinco pruebas",
          "Comparación de tu puntaje entre ensayos y por eje",
          "Hasta 10 preferencias en Mi meta",
        ].map((item) => (
          <li key={item} className="flex gap-2">
            <span aria-hidden className="text-accent">
              ✓
            </span>
            <span>{item}</span>
          </li>
        ))}
      </ul>

      <Link
        href="/planes"
        className="btn-glow mt-4 block rounded-lg px-4 py-2.5 text-center text-sm font-semibold text-accent-foreground"
      >
        {sinCupo ? "Seguir rindiendo con Pro" : "Ver el plan Pro"}
      </Link>
    </section>
  );
}
