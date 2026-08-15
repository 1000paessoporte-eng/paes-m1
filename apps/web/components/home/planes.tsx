import Link from "next/link";
/*
 * PRECIO DE LANZAMIENTO, NO "ANTES/AHORA"
 * ---------------------------------------
 * El precio mayor se rotula como PRECIO NORMAL —el que regirá cuando termine
 * el lanzamiento— y no como un precio anterior. La diferencia no es de estilo:
 * la Ley 19.496 del consumidor obliga a que un precio tachado corresponda a
 * uno efectivamente cobrado antes, y estos planes todavía no se cobran. Anunciar
 * un descuento sobre un precio que nunca existió es publicidad engañosa, y el
 * SERNAC ha multado exactamente eso.
 *
 * Cuando el lanzamiento termine y el precio normal se cobre de verdad, ahí sí
 * podrá presentarse como precio anterior.
 **
 * Planes de pago.
 *
 * Los precios se fijaron contra el mercado chileno de preparación PAES
 * (agosto 2026), tomando como referencia lo que cobra cada categoría:
 *
 * - Plataformas de práctica de matemática, la competencia directa:
 *   SimplePAES $8.000/mes. Es el techo natural de 1000paes: hoy el banco de
 *   preguntas es más chico, así que cobrar por encima no se sostiene.
 * - Plataformas con banco grande + clases: PreuTest $26.000/mes o $86.000/año.
 * - Preuniversitarios online completos: Filadd $397.000-$467.000 al año
 *   (~$33.000/mes en 12 cuotas). Otra liga: incluyen clases en vivo.
 * - Modelo B2B donde el colegio paga y el alumno entra gratis:
 *   Puntaje Nacional, Umáximo. Ninguno publica su tarifa institucional.
 *
 * De ahí el posicionamiento: Pro entra bajo el competidor directo, y el plan
 * de temporada existe porque la demanda es estacional (la PAES se rinde a fin
 * de año, no se estudia todo el año parejo).
 *
 * Los precios se muestran con IVA incluido, como exige el marco de precios al
 * consumidor final.
 */

/**
 * Los requisitos del premio, en el orden en que se verifican.
 *
 * Todos menos el último se comprueban con datos que la plataforma ya registra:
 * meses pagados, ensayos rendidos y días con actividad. Eso importa porque un
 * requisito que no se puede verificar no es un requisito, es una excusa para
 * discutir con el ganador.
 */
const REQUISITOS_PREMIO = [
  {
    titulo: "6 meses de plan Pro en el último año",
    detalle:
      "Sumados, dentro de los 12 meses anteriores al día de la prueba. No tienen que ser seguidos.",
  },
  {
    titulo: "30 ensayos completos rendidos",
    detalle:
      "De 34 preguntas o más, terminados. Los ensayos cortos y la práctica por tema no cuentan para este requisito.",
  },
  {
    titulo: "15 días seguidos con ensayo",
    detalle:
      "Tu mejor racha, no la que tengas activa el día de la prueba. Enfermarse un día no deja a nadie fuera.",
  },
  {
    titulo: "90 días distintos con práctica",
    detalle:
      "Días en que respondiste al menos 10 preguntas. Se premia la constancia, no una maratón de última semana.",
  },
  {
    titulo: "Haber practicado esa prueba acá",
    detalle:
      "Al menos 10 de tus ensayos tienen que ser de la prueba en la que obtuviste el puntaje nacional.",
  },
  {
    titulo: "Certificado oficial del DEMRE",
    detalle:
      "A nombre del titular de la cuenta, con el mismo RUT. La cuenta debe ser personal, no compartida.",
  },
  {
    titulo: "Reclamarlo dentro de 30 días",
    detalle:
      "Desde la publicación oficial de resultados. Pasado ese plazo el premio caduca.",
  },
] as const;

const PLANES = [
  {
    nombre: "Gratis",
    resumen: "Para partir hoy",
    precio: "Sin costo",
    precioNormal: null,
    periodo: null,
    alternativa: null,
    facturacion: "No requiere tarjeta",
    duracion: "Acceso permanente",
    incluye: [
      "4 ensayos al mes, con el banco de preguntas actual",
      "Puntaje PAES estimado y resolución de cada ejercicio",
      "Historial de tu progreso con gráfico de evolución",
      "Árbol de habilidades y lecciones completas",
      "Una carrera en Mi meta, con su puntaje ponderado",
    ],
    destacado: false,
    disponible: true,
  },
  {
    nombre: "Pro",
    resumen: "Para preparar en serio",
    precio: "$5.990",
    precioNormal: "$9.990",
    periodo: "al mes",
    alternativa: "o $34.900 por toda la temporada (normal $59.900), hasta el día de la PAES",
    facturacion: "Mensual, sin permanencia",
    duracion: "Mientras la suscripción esté activa",
    incluye: [
      "Todo lo del plan Gratis",
      "Banco de preguntas ampliado y actualizado cada mes",
      "Recomendación automática de qué nodo reforzar",
      "Ensayos sin límite, filtrados por eje temático",
      "Comparación de tu puntaje entre ensayos y por eje",
      "Hasta 10 preferencias en Mi meta, con simulador",
    ],
    destacado: true,
    disponible: false,
  },
  {
    nombre: "Colegios",
    resumen: "Para cursos completos",
    precio: "$3.500",
    precioNormal: "$4.900",
    periodo: "por alumno al año",
    alternativa: "Desde un curso (30 alumnos). Sobre 200 alumnos, a convenir",
    facturacion: "Por año escolar, con factura",
    duracion: "Todo el periodo contratado",
    incluye: [
      "Todo lo del plan Pro para cada estudiante",
      "Cuentas para el curso completo",
      "Panel del profesor con el avance de cada alumno",
      "Informes por estudiante, por curso y por eje temático",
      "Ensayos programados con fecha y hora de aplicación",
    ],
    destacado: false,
    disponible: false,
  },
] as const;

export function Planes() {
  return (
    <section id="planes" className="border-t border-border px-6 py-20">
      <div className="mx-auto max-w-5xl">
        <div className="mx-auto max-w-lg text-center">
          <span className="rounded-full border border-accent/40 bg-accent/5 px-3 py-1 text-xs font-medium text-accent">
            Próximamente
          </span>
          <h2 className="mt-4 text-2xl font-semibold tracking-tight sm:text-3xl">
            Planes
          </h2>
          <p className="mt-3 text-sm text-muted">
            Hoy todo lo que ves está disponible sin costo, y seguirá estándolo
            para el plan Gratis. Estos son los precios de los planes que vienen;
            avisaremos antes de que empiece a cobrarse.
          </p>
          <p className="mt-2 text-xs text-muted">
            Valores en pesos chilenos, IVA incluido.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {PLANES.map((plan) => (
            <div
              key={plan.nombre}
              className={
                plan.destacado
                  ? "flex flex-col rounded-xl border border-accent/50 bg-accent/5 p-6"
                  : "flex flex-col rounded-xl border border-border bg-surface p-6"
              }
            >
              <div className="flex items-baseline justify-between gap-2">
                <h3 className="text-base font-semibold">{plan.nombre}</h3>
                {plan.destacado && (
                  <span className="rounded-full bg-accent px-2 py-0.5 text-[11px] font-medium text-accent-foreground">
                    Recomendado
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-muted">{plan.resumen}</p>

              {plan.precioNormal && (
                <p className="mt-4 flex items-baseline gap-2 text-sm">
                  <span className="text-muted line-through">{plan.precioNormal}</span>
                  <span className="rounded-full bg-accent-warm/15 px-2 py-0.5 text-[11px] font-semibold text-accent-warm-strong">
                    Precio de lanzamiento
                  </span>
                </p>
              )}
              <p className={plan.precioNormal ? "mt-1 flex items-baseline gap-1.5" : "mt-4 flex items-baseline gap-1.5"}>
                <span
                  className={
                    plan.disponible
                      ? "text-3xl font-bold tracking-tight text-success"
                      : "text-3xl font-bold tracking-tight"
                  }
                >
                  {plan.precio}
                </span>
                {plan.periodo && (
                  <span className="text-sm text-muted">{plan.periodo}</span>
                )}
              </p>
              {plan.alternativa && (
                <p className="mt-1 text-xs leading-relaxed text-muted">
                  {plan.alternativa}
                </p>
              )}

              <dl className="mt-4 flex flex-col gap-1.5 border-y border-border py-3 text-xs">
                <div className="flex justify-between gap-2">
                  <dt className="text-muted">Cobro</dt>
                  <dd className="text-right font-medium">{plan.facturacion}</dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt className="text-muted">Duración</dt>
                  <dd className="text-right font-medium">{plan.duracion}</dd>
                </div>
              </dl>

              <ul className="mt-4 flex flex-1 flex-col gap-2 text-sm text-muted">
                {plan.incluye.map((item) => (
                  <li key={item} className="flex gap-2">
                    <span aria-hidden className="text-accent">
                      ✓
                    </span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>

              <button
                type="button"
                disabled
                className="mt-6 w-full cursor-not-allowed rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-muted"
              >
                {plan.disponible ? "Es el plan actual" : "Disponible pronto"}
              </button>
            </div>
          ))}
        </div>

        <CodigoPromocional />
        <PremioPuntajeNacional />
      </div>
    </section>
  );
}

/**
 * Canje de código promocional.
 *
 * Va debajo de los planes y no dentro del checkout porque hoy no hay checkout:
 * quien llega con un código de un compañero necesita ver de inmediato que la
 * plataforma lo reconoce, aunque el cobro todavía no exista.
 */
function CodigoPromocional() {
  return (
    <div className="mt-10 rounded-xl border border-border bg-surface p-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="min-w-0">
          <h3 className="font-semibold tracking-tight">¿Tienes un código?</h3>
          <p className="mt-1 text-sm text-muted">
            Los códigos de compañero y los de sala se canjean acá. Cada uno tiene
            su propio plazo y sus condiciones.
          </p>
        </div>
        <form className="flex gap-2" aria-label="Canjear código promocional">
          <input
            name="codigo"
            placeholder="CAMILA-7F2A"
            aria-label="Código promocional"
            className="w-44 rounded-lg border border-border bg-background px-3 py-2 text-sm uppercase placeholder:normal-case placeholder:text-muted/60"
          />
          <button
            type="button"
            disabled
            title="Disponible cuando se activen los planes"
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-muted"
          >
            Canjear
          </button>
        </form>
      </div>
    </div>
  );
}

/**
 * El premio al puntaje nacional.
 *
 * Es una promoción con premio en dinero, así que el resumen enlaza a las bases
 * completas y ningún requisito queda insinuado: o está escrito, o no existe.
 * El tope de premios también va a la vista — una promoción sin límite declarado
 * es una obligación abierta contra la caja de un producto que todavía no cobra.
 */
function PremioPuntajeNacional() {
  return (
    <div className="mt-6 overflow-hidden rounded-xl border border-accent-warm/40 bg-accent-warm/5 p-6">
      <span className="rounded-full bg-accent-warm/15 px-2.5 py-1 text-[11px] font-semibold text-accent-warm-strong">
        Para estudiantes con plan Pro
      </span>
      <h3 className="mt-3 text-xl font-bold tracking-tight">
        $500.000 si sacas puntaje nacional
      </h3>
      <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">
        Si obtienes 1.000 puntos en cualquiera de las cinco pruebas PAES y
        preparaste esa prueba con nosotros, te entregamos medio millón de pesos.
        No es un sorteo: se gana rindiendo.
      </p>

      <ul className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {REQUISITOS_PREMIO.map((r) => (
          <li key={r.titulo} className="flex gap-2.5">
            <span aria-hidden className="mt-0.5 text-accent-warm-strong">
              ✓
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-medium">{r.titulo}</span>
              <span className="block text-xs leading-relaxed text-muted">
                {r.detalle}
              </span>
            </span>
          </li>
        ))}
      </ul>

      <p className="mt-5 text-xs leading-relaxed text-muted">
        Hasta 5 premios por proceso de admisión. Si hubiera más ganadores que
        cumplen todo, los $2.500.000 se reparten en partes iguales entre ellos.{" "}
        <Link
          href="/premio"
          className="font-medium text-accent underline-offset-4 hover:underline"
        >
          Ver las bases completas
        </Link>
        .
      </p>
    </div>
  );
}
