import Link from "next/link";
import type { ContentStats, Universidad, UsoPublico } from "@/lib/api";
import { GoogleButton } from "@/components/auth/google-button";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { Reveal } from "@/components/motion/reveal";
import { Planes } from "@/components/home/planes";
import { HeroPregunta } from "@/components/home/hero-pregunta";
import { BentoProducto } from "@/components/home/bento-producto";
import { TrazoLapiz } from "@/components/home/trazo-lapiz";
import { EntradaHero } from "@/components/home/entrada-hero";
import { SiteFooter } from "@/components/site-footer";
import { diasHastaPaes } from "@/lib/paes-fecha";
import { CuentaRegresiva } from "@/components/home/cuenta-regresiva";
import { nombreLegible, slugUniversidad } from "@/lib/carreras";
import { COLOR_PRUEBA } from "@/lib/colores-prueba";

/** Portada para visitantes sin sesión: nombre, entrada y qué ofrece el sitio. */

/**
 * Lo que ofrece la plataforma.
 *
 * Es una función y no una constante porque dos de las tarjetas llevan cifras
 * —cuántos nodos tiene el árbol, cuántas carreras trae el catálogo— y esas
 * cifras se cuentan en la base. Escritas a mano envejecían en silencio: la
 * tarjeta del árbol decía "47 nodos" justo encima de la franja que mostraba el
 * número real contado en la base. Cuando el dato no está, la frase se dice sin
 * número en vez de inventarlo (regla 1 del proyecto).
 */



// Las cinco pruebas, en el orden en que las rinde un postulante. Rotan dentro
// del titular; la primera es la que ve quien no tiene JavaScript.


/** Las cinco pruebas, para entrar directo a la demo de cada una. */
const PRUEBAS_DEMO = [
  { id: "lectora", corto: "Lectora" },
  { id: "m1", corto: "Matemática M1" },
  { id: "m2", corto: "Matemática M2" },
  { id: "ciencias", corto: "Ciencias" },
  { id: "historia", corto: "Historia" },
] as const;


const CONFIANZA = [
  {
    title: "Puntaje con tablas oficiales",
    description:
      "La conversión a escala 100-1000 usa las tablas de transformación publicadas por el DEMRE para cada prueba, no una fórmula inventada.",
    icon: TargetIcon,
  },
  {
    title: "Tiempo real de cada prueba",
    description:
      "El cronómetro respeta la razón oficial minutos/pregunta de cada prueba: Competencia Lectora son 65 preguntas en 150 min; M1, 65 en 140; M2, 55 en 140; Ciencias, 80 en 160; Historia, 65 en 120.",
    icon: ClockIcon,
  },
  {
    title: "Sin letra chica",
    description:
      "Estamos en beta: todo lo que ves hoy es gratis, y sumamos preguntas y funciones nuevas cada semana.",
    icon: SparkIcon,
  },
] as const;

export function LandingPublica({
  stats,
  uso,
  universidades,
  pagoDisponible = false,
}: {
  stats: ContentStats | null;
  uso: UsoPublico | null;
  universidades: Universidad[];
  pagoDisponible?: boolean;
}) {
  const totalCarreras = universidades.length
    ? universidades.reduce((suma, u) => suma + u.carreras, 0)
    : null;

  return (
    <main className="flex flex-1 flex-col">
      {/* ── HERO ─────────────────────────────────────────────────────
          La pregunta ES el hero. Antes acá había una tarjeta de puntaje
          inventada: se veía bien y no probaba nada, así que quien llegaba
          tenía que creernos. De 65 personas que llegaron a la portada en un
          mes, 10 abrieron un ensayo; el resto se fue sin ver jamás una
          pregunta, que es lo único que este producto tiene para mostrar. */}
      <section className="relative overflow-hidden px-6 pt-16 pb-20 sm:pt-20">
        <div className="bg-dot-grid pointer-events-none absolute inset-0 top-0 h-[26rem]" />

        <div className="relative mx-auto grid max-w-6xl grid-cols-1 items-center gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:gap-16">
          {/* La entrada del hero es UNA secuencia, no cinco animaciones sueltas:
              el reloj, el titular, el trazo, la bajada y la acción entran en
              ese orden con 90 ms entre medio. Es el orden en que se leen, y
              acompañarlo hace que la primera pantalla se sienta armada en vez
              de aparecida de golpe. */}
          <EntradaHero className="flex flex-col items-center gap-5 text-center lg:items-start lg:text-left">
            {/* El reloj solo no dice nada: "100 d 08 h" suelto parece un número
                perdido. Con el marco es lo primero que un tercero medio quiere
                saber, y pone el resto de la página en contexto. */}
            <p className="flex flex-wrap items-baseline justify-center gap-x-2 text-sm text-muted lg:justify-start">
              <span>Faltan</span>
              <span className="font-display text-base font-semibold text-foreground">
                <CuentaRegresiva />
              </span>
              <span>para la PAES</span>
            </p>

            <h1 className="text-4xl leading-[1.05] font-bold tracking-tight text-balance sm:text-5xl lg:text-[3.5rem]">
              Rinde la PAES
              <br />
              {/* El trazo se dibuja bajo estas dos palabras y va cambiando por
                  los cinco colores de prueba. Es lo que hacía la palabra que
                  rotaba --moverse y decir que acá están las cinco-- pero sin
                  tocar el texto, así que nada se reacomoda. */}
              <span className="relative inline-block">
                antes de la PAES
                <TrazoLapiz />
              </span>
            </h1>

            <p className="max-w-md text-balance text-lg text-muted">
              Ensayos cronometrados con el tiempo real de cada prueba, puntaje
              estimado en escala 100–1000 y la resolución paso a paso de cada
              ejercicio.
            </p>

            <div className="flex w-full flex-col items-center gap-3 lg:items-start">
              <Link
                href="/registro"
                className="btn-glow w-full rounded-xl px-8 py-3.5 text-center text-base font-semibold text-accent-foreground sm:w-auto"
              >
                Empezar mi primer ensayo →
              </Link>
              <GoogleButton redirectTo="/examen" />
              <p className="text-sm text-muted">
                Gratis, sin tarjeta ·{" "}
                <Link href="/login" className="text-accent">
                  ya tengo cuenta
                </Link>
              </p>
            </div>
          </EntradaHero>

          <div className="mx-auto w-full max-w-md lg:mx-0 lg:max-w-none">
            <HeroPregunta />
          </div>
        </div>

        {/* Las cinco pruebas con su color y su entrada directa a la demo: es el
            código de color del producto entero, enseñado en el primer contacto
            y sin una sola palabra de explicación. */}
        <div className="relative mx-auto mt-14 max-w-6xl">
          <p className="text-center text-sm text-muted">
            O prueba cualquiera de las cinco, sin crear cuenta:
          </p>
          <ul className="mt-3 flex flex-wrap justify-center gap-2">
            {PRUEBAS_DEMO.map((p) => (
              <li key={p.id}>
                <Link
                  href={`/demo?prueba=${p.id}`}
                  style={{ "--c": COLOR_PRUEBA[p.id] } as React.CSSProperties}
                  className="inline-flex rounded-full border border-(--c)/45 bg-(--c)/6 px-4 py-2 text-sm font-semibold text-(--c) transition-colors hover:bg-(--c)/12"
                >
                  {p.corto}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <FranjaCifras stats={stats} />

      <FranjaUso uso={uso} />

      <BentoProducto stats={stats} />

      <section className="border-t border-border bg-surface/50 px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mx-auto max-w-lg text-center">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Hecho con los datos reales de la PAES
            </h2>
            <p className="mt-3 text-sm text-muted">
              Nada de fórmulas inventadas: el puntaje y los tiempos salen de
              lo que publica el DEMRE.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {CONFIANZA.map((item) => (
              <div
                key={item.title}
                className="rounded-xl border border-border bg-background p-5"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <item.icon />
                </div>
                <h3 className="mt-3 text-sm font-semibold text-foreground">
                  {item.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Lo que necesitas saber ──────────────────────────────────── */}
      <section className="border-t border-border px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mx-auto max-w-lg text-center">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Lo que necesitas saber de la PAES
            </h2>
            <p className="mt-3 text-sm text-muted">
              Los datos oficiales de las cinco pruebas, según el temario del
              DEMRE. El tiempo de tu ensayo se calcula con esta proporción.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {PRUEBAS_INFO.map((prueba, i) => (
              <Reveal key={prueba.nombre} delay={Math.min(i, 4) * 0.06}>
              <div className="card-hover h-full rounded-xl border border-border bg-surface p-6">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="font-semibold text-foreground">{prueba.nombre}</h3>
                  <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent">
                    Disponible
                  </span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {prueba.descripcion}
                </p>
                <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-border pt-4 text-sm">
                  <div>
                    <dt className="text-xs text-muted">Preguntas</dt>
                    <dd className="font-semibold tabular-nums">{prueba.preguntas}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted">Duración oficial</dt>
                    <dd className="font-semibold">{prueba.duracion}</dd>
                  </div>
                </dl>
              </div>
              </Reveal>
            ))}
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {DATOS_PAES.map((dato) => (
              <div
                key={dato.title}
                className="rounded-xl border border-border bg-surface p-5"
              >
                <h3 className="text-sm font-semibold text-foreground">
                  {dato.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">
                  {dato.description}
                </p>
              </div>
            ))}
          </div>

          <p className="mt-8 text-center text-sm text-muted">
            ¿Te quedan dudas sobre cómo funciona la plataforma?{" "}
            <Link
              href="/preguntas-frecuentes"
              className="font-medium text-accent hover:underline"
            >
              Mira las preguntas frecuentes
            </Link>
            .
          </p>
        </div>
      </section>

      <SeccionCarreras universidades={universidades} totalCarreras={totalCarreras} />

      {/* ── Cierre motivacional ─────────────────────────────────────── */}
      <CierreMotivacional />

      <Planes pagoDisponible={pagoDisponible} />

      <SiteFooter />
    </main>
  );
}

/** Datos oficiales de cada prueba, tomados del temario DEMRE. */
const PRUEBAS_INFO = [
  {
    nombre: "Competencia Lectora",
    descripcion:
      "Obligatoria para todos: textos literarios, no literarios y discontinuos, con preguntas de localizar, interpretar y evaluar.",
    preguntas: "65",
    duracion: "2 h 30 min",
  },
  {
    nombre: "Competencia Matemática M1",
    descripcion:
      "La prueba base de matemática: cubre el temario de 7° básico a 2° medio. La rinden todas las carreras que piden matemática.",
    preguntas: "65",
    duracion: "2 h 20 min",
  },
  {
    nombre: "Competencia Matemática M2",
    descripcion:
      "Evalúa todo lo de M1 más contenido avanzado de 3° y 4° medio. La piden carreras científicas, de ingeniería y de salud.",
    preguntas: "55",
    duracion: "2 h 20 min",
  },
  {
    nombre: "Ciencias",
    descripcion:
      "Módulo común de Biología, Física y Química más un módulo electivo. Es la prueba más larga de las cinco.",
    preguntas: "80",
    duracion: "2 h 40 min",
  },
  {
    nombre: "Historia y Ciencias Sociales",
    descripcion:
      "Historia, formación ciudadana y economía. Evalúa sobre todo análisis de fuentes: tablas, textos y datos.",
    preguntas: "65",
    duracion: "2 h",
  },
] as const;

const DATOS_PAES = [
  {
    title: "Cada prueba, sus ejes",
    description:
      "Matemática se divide en Números, Álgebra y funciones, Geometría, y Probabilidad; Lectora en localizar, interpretar y evaluar. Tu resultado se desglosa por cada eje.",
  },
  {
    title: "Puntaje de 100 a 1000",
    description:
      "La conversión desde tus respuestas correctas no es lineal: depende de la tabla oficial de cada aplicación.",
  },
  {
    title: "Equivocarse no descuenta",
    description:
      "Las respuestas incorrectas no restan puntaje, así que siempre conviene contestar todas las preguntas.",
  },
] as const;

/** Banda de cierre: recuerda cuánto falta para la prueba y empuja a empezar. */
function CierreMotivacional() {
  const dias = diasHastaPaes();

  return (
    <section className="hero-glow relative overflow-hidden border-t border-border px-6 py-20">
      <div className="relative mx-auto max-w-2xl text-center">
        {dias !== null && (
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/5 px-4 py-1.5 text-sm font-medium text-accent">
            <span aria-hidden className="pulso-reloj">
              <RelojIcon />
            </span>
            Para la PAES faltan{" "}
            {/* El servidor pinta los días; el reloj completo llega con el
                JavaScript. Ver el comentario de CuentaRegresiva. */}
            <span className="hidden sm:inline">
              <CuentaRegresiva />
            </span>
            <span className="sm:hidden tabular-nums">
              {dias} {dias === 1 ? "día" : "días"}
            </span>
          </span>
        )}
        <h2 className="mt-4 text-3xl font-bold tracking-tight text-balance sm:text-4xl">
          El puntaje no se decide el día de la prueba
        </h2>
        <p className="mt-4 text-balance leading-relaxed text-muted">
          Se decide en los meses de antes, en cada ejercicio que entendiste de
          verdad en vez de dejar pasar. Empieza hoy con un ensayo y descubre
          exactamente en qué estás parado.
        </p>
        <Link
          href="/registro"
          className="btn-glow mt-8 inline-flex rounded-lg px-8 py-3.5 text-base font-semibold text-accent-foreground transition-transform hover:-translate-y-0.5"
        >
          Empezar gratis →
        </Link>
        <p className="mt-3 text-xs text-muted">
          Sin tarjeta. Sin compromiso. Toma un minuto.
        </p>
      </div>
    </section>
  );
}

/**
 * Cifras del banco, contadas en la base al momento de servir la página.
 *
 * Nada de "más de 500 ejercicios": el número que se muestra es el que hay. Si
 * la API no respondió, la franja no se dibuja — un dato de menos es preferible
 * a uno inflado, sobre todo en la única página que promete que acá no se
 * inventan datos.
 */
function FranjaCifras({ stats }: { stats: ContentStats | null }) {
  if (!stats) return null;

  const cifras = [
    { valor: stats.questions, etiqueta: "preguntas verificadas" },
    { valor: stats.subjects, etiqueta: "pruebas PAES" },
    { valor: stats.skill_nodes, etiqueta: "temas en el árbol" },
    { valor: stats.passages, etiqueta: "textos de lectura" },
  ];

  return (
    <section
      className="border-t border-border bg-surface/60 px-6 py-10"
      aria-label="Cifras del banco de preguntas"
    >
      <Reveal>
        <dl className="mx-auto grid max-w-4xl grid-cols-2 gap-6 sm:grid-cols-4">
          {cifras.map((c) => (
            <div key={c.etiqueta} className="text-center">
              <dt className="sr-only">{c.etiqueta}</dt>
              <dd>
                <span className="block text-3xl font-bold tracking-tight tabular-nums sm:text-4xl">
                  <NumeroAnimado valor={c.valor} />
                </span>
                <span className="mt-1 block text-xs text-muted sm:text-sm">
                  {c.etiqueta}
                </span>
              </dd>
            </div>
          ))}
        </dl>
      </Reveal>
    </section>
  );
}

/**
 * Cuánto se usa la plataforma.
 *
 * La única prueba social que este proyecto puede mostrar: no hay testimonios
 * ni logos de colegios porque no existen, y la regla 1 prohíbe inventarlos.
 *
 * Por debajo del umbral la franja NO se dibuja. Con cifras chicas el dato
 * juega en contra —"3 ensayos rendidos" espanta en vez de convencer— y esa es
 * una decisión de portada, no del endpoint, que devuelve el número real
 * siempre. Cuando la plataforma se use de verdad, la franja aparece sola.
 */
const MINIMO_ENSAYOS_PARA_PRESUMIR = 50;

function FranjaUso({ uso }: { uso: UsoPublico | null }) {
  if (!uso || uso.ensayos_rendidos < MINIMO_ENSAYOS_PARA_PRESUMIR) return null;

  const cifras = [
    { valor: uso.ensayos_rendidos, etiqueta: "ensayos rendidos" },
    { valor: uso.preguntas_respondidas, etiqueta: "preguntas respondidas" },
    { valor: uso.alumnos, etiqueta: "alumnos preparándose" },
  ];

  return (
    <section
      className="border-t border-border px-6 py-10"
      aria-label="Uso de la plataforma"
    >
      <Reveal>
        <dl className="mx-auto grid max-w-3xl grid-cols-1 gap-6 sm:grid-cols-3">
          {cifras.map((c) => (
            <div key={c.etiqueta} className="text-center">
              <dt className="sr-only">{c.etiqueta}</dt>
              <dd>
                <span className="block text-3xl font-bold tracking-tight tabular-nums text-accent sm:text-4xl">
                  <NumeroAnimado valor={c.valor} />
                </span>
                <span className="mt-1 block text-xs text-muted sm:text-sm">
                  {c.etiqueta}
                </span>
              </dd>
            </div>
          ))}
        </dl>
      </Reveal>
    </section>
  );
}

/** Cuántas universidades se nombran en la portada. El resto está en /carreras. */
const UNIVERSIDADES_EN_PORTADA = 8;

/**
 * La puerta al catálogo de carreras.
 *
 * Las 1.855 fichas con las ponderaciones oficiales del DEMRE existían desde
 * antes, pero no había un solo enlace hacia ellas: ni en el menú, ni en el pie,
 * ni en la portada. Google solo las conocía por el sitemap y una persona no
 * llegaba nunca. Esta sección es ese enlace, y de paso es lo que la gente
 * busca de verdad: cuánto puntaje necesita para la carrera que quiere.
 *
 * Si la API no responde, la sección no se dibuja, igual que la franja de
 * cifras: mejor una sección menos que una lista vacía que parezca un error.
 */
function SeccionCarreras({
  universidades,
  totalCarreras,
}: {
  universidades: Universidad[];
  totalCarreras: number | null;
}) {
  if (universidades.length === 0) return null;

  return (
    <section className="border-t border-border bg-surface/50 px-6 py-20">
      <div className="mx-auto max-w-5xl">
        <div className="mx-auto max-w-xl text-center">
          <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
            ¿Qué puntaje necesitas para tu carrera?
          </h2>
          <p className="mt-3 text-sm text-muted">
            {totalCarreras
              ? `Las ponderaciones oficiales del DEMRE de ${totalCarreras.toLocaleString("es-CL")} carreras en ${universidades.length} universidades: cuánto pesa cada prueba, el ponderado mínimo de postulación y las vacantes.`
              : "Las ponderaciones oficiales del DEMRE: cuánto pesa cada prueba, el ponderado mínimo de postulación y las vacantes."}
          </p>
        </div>

        <ul className="mt-10 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {universidades.slice(0, UNIVERSIDADES_EN_PORTADA).map((u) => (
            <li key={u.universidad}>
              <Link
                href={`/carreras/${slugUniversidad(u.universidad)}`}
                className="card-hover flex items-center justify-between gap-3 rounded-xl border border-border bg-background px-4 py-3"
              >
                <span className="min-w-0 flex-1 text-sm text-foreground">
                  {nombreLegible(u.universidad)}
                </span>
                <span className="shrink-0 text-xs text-muted tabular-nums">
                  {u.carreras} carreras
                </span>
              </Link>
            </li>
          ))}
        </ul>

        <p className="mt-8 text-center text-sm text-muted">
          <Link href="/carreras" className="font-medium text-accent hover:underline">
            Ver todas las universidades
          </Link>{" "}
          · No necesitas cuenta para consultarlas.
        </p>
      </div>
    </section>
  );
}


function TargetIcon({ className }: { className?: string }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1" fill="currentColor" />
    </svg>
  );
}

function RelojIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.5 2" />
    </svg>
  );
}

function ClockIcon({ className }: { className?: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.5 2" />
    </svg>
  );
}

function SparkIcon({ className }: { className?: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className={className}>
      <path d="M12 2l1.8 5.6L19.5 9l-5.7 1.4L12 16l-1.8-5.6L4.5 9l5.7-1.4z" />
    </svg>
  );
}

