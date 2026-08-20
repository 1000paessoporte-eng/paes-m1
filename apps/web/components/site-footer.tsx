import Link from "next/link";
import { EMAIL_CONTACTO, redesActivas } from "@/lib/redes-sociales";

/**
 * Footer del sitio, compartido por la landing pública, el panel y las páginas
 * informativas. Las redes sociales solo aparecen cuando tienen URL configurada
 * en `lib/redes-sociales.ts` (hoy las cuentas no existen todavía).
 */

const ICONOS: Record<string, () => React.ReactElement> = {
  instagram: InstagramIcon,
  tiktok: TikTokIcon,
  facebook: FacebookIcon,
  youtube: YouTubeIcon,
};

const NOMBRES: Record<string, string> = {
  instagram: "Instagram",
  tiktok: "TikTok",
  facebook: "Facebook",
  youtube: "YouTube",
};

export function SiteFooter() {
  const redes = redesActivas();

  return (
    <footer className="border-t border-border bg-surface/50 px-6 py-12">
      <div className="mx-auto max-w-5xl">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div className="col-span-2 sm:col-span-1">
            <Link href="/" className="flex items-center gap-2">
              <span
                className="flex h-7 w-7 items-center justify-center rounded-md text-xs font-bold text-accent-foreground"
                style={{
                  background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
                }}
              >
                1K
              </span>
              <span className="text-sm font-semibold tracking-tight">1000paes</span>
            </Link>
            <p className="mt-3 text-xs leading-relaxed text-muted">
              Ensayos PAES con el tiempo real de la prueba, puntaje estimado y
              la resolución de cada ejercicio.
            </p>
          </div>

          <div>
            <h3 className="text-xs font-semibold tracking-wide text-foreground uppercase">
              Sobre nosotros
            </h3>
            <ul className="mt-3 flex flex-col gap-2 text-sm text-muted">
              <li>
                <Link href="/sobre-nosotros" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Quiénes somos
                </Link>
              </li>
              <li>
                <Link href="/#como-funciona" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Cómo funciona
                </Link>
              </li>
              <li>
                <Link href="/planes" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Planes
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-semibold tracking-wide text-foreground uppercase">
              Más información
            </h3>
            <ul className="mt-3 flex flex-col gap-2 text-sm text-muted">
              <li>
                <Link
                  href="/carreras"
                  className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline"
                >
                  Carreras y ponderaciones
                </Link>
              </li>
              <li>
                <Link
                  href="/preguntas-frecuentes"
                  className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline"
                >
                  Preguntas frecuentes
                </Link>
              </li>
              <li>
                <Link href="/terminos" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Términos y condiciones
                </Link>
              </li>
              <li>
                <Link href="/privacidad" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Política de privacidad
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-semibold tracking-wide text-foreground uppercase">
              Empezar
            </h3>
            <ul className="mt-3 flex flex-col gap-2 text-sm text-muted">
              <li>
                <Link href="/registro" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Crear cuenta gratis
                </Link>
              </li>
              <li>
                <Link href="/login" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Iniciar sesión
                </Link>
              </li>
              <li>
                <Link href="/demo" className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                  Probar sin cuenta
                </Link>
              </li>
            </ul>

            {redes.length > 0 && (
              <div className="mt-5 flex gap-3">
                {redes.map((red) => {
                  const Icono = ICONOS[red.nombre];
                  return (
                    <a
                      key={red.nombre}
                      href={red.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={NOMBRES[red.nombre] ?? red.nombre}
                      className="text-muted transition-colors hover:text-accent"
                    >
                      {Icono ? <Icono /> : null}
                    </a>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        <div className="mt-10 border-t border-border pt-6 text-xs leading-relaxed text-muted">
          <p>
            1000paes no tiene relación con el DEMRE ni con ninguna institución
            oficial del proceso de admisión. El puntaje mostrado es una
            estimación referencial: el puntaje real depende de la forma rendida
            y del proceso de admisión.
          </p>
          {EMAIL_CONTACTO && (
            <p className="mt-2">
              Contacto:{" "}
              <a href={`mailto:${EMAIL_CONTACTO}`} className="-my-1.5 inline-block py-2 hover:text-foreground hover:underline">
                {EMAIL_CONTACTO}
              </a>
            </p>
          )}
        </div>
      </div>
    </footer>
  );
}

function InstagramIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

function TikTokIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M16.5 2h-3v13a2.5 2.5 0 1 1-2.5-2.5c.2 0 .4 0 .5.1V9.5A5.5 5.5 0 1 0 16.5 15V8.6a6.8 6.8 0 0 0 4 1.3V6.6a3.9 3.9 0 0 1-4-3.9V2z" />
    </svg>
  );
}

function FacebookIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M14 9V7.5c0-.8.2-1.2 1.3-1.2H17V3.2c-.6-.1-1.5-.2-2.5-.2C12.2 3 10.7 4.4 10.7 7v2H8v3.2h2.7V21H14v-8.8h2.6l.4-3.2H14z" />
    </svg>
  );
}

function YouTubeIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3-5.2 3z" />
    </svg>
  );
}
