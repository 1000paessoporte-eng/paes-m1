import Link from "next/link";

export const metadata = {
  title: "Premio Puntaje Nacional",
  description:
    "Bases del premio de $500.000 para estudiantes con plan Pro que obtengan puntaje nacional en la PAES.",
  alternates: { canonical: "/premio" },
};

/**
 * Bases del premio.
 *
 * Una promoción con premio en dinero obliga a tener bases públicas, completas y
 * accesibles antes de anunciarla (Ley 19.496). Esta página es esa obligación, y
 * también la protección del propio producto: cada condición que no esté escrita
 * acá es una discusión perdida de antemano con quien reclame el premio.
 *
 * El tope de premios es lo más importante de todo el documento. Una promoción
 * sin límite declarado es una deuda de monto desconocido contra la caja de un
 * producto que todavía no cobra.
 */

const SECCIONES = [
  {
    titulo: "1. Quién organiza y a quién aplica",
    parrafos: [
      "El premio lo entrega 1000paes a estudiantes que rindan la PAES del proceso de admisión vigente en Chile y que cumplan TODOS los requisitos de la sección 3.",
      "El titular de la cuenta debe ser la misma persona que rinde la prueba. Las cuentas compartidas entre varios estudiantes quedan fuera, porque el requisito de práctica dejaría de significar algo.",
      "Si el estudiante es menor de edad, el premio se entrega a su madre, padre o apoderado, quien deberá aceptar las bases.",
    ],
  },
  {
    titulo: "2. Qué se premia",
    parrafos: [
      "$500.000 (quinientos mil pesos chilenos) por obtener 1.000 puntos —puntaje nacional— en cualquiera de las cinco pruebas PAES: Competencia Lectora, Competencia Matemática M1, Competencia Matemática M2, Ciencias, o Historia y Ciencias Sociales.",
      "El premio se entrega una sola vez por persona, aunque obtenga puntaje nacional en más de una prueba.",
      "No es un sorteo ni depende del azar: se obtiene por el resultado de la prueba.",
    ],
  },
  {
    titulo: "3. Requisitos",
    lista: [
      "Haber tenido plan Pro o superior activo por al menos 6 meses, sumados, dentro de los 12 meses anteriores al día de la prueba. No necesitan ser consecutivos.",
      "Haber rendido y terminado al menos 30 ensayos de 34 preguntas o más en la plataforma. Los ensayos cortos, la práctica por tema y los intentos abandonados no cuentan.",
      "Haber practicado en al menos 90 días distintos, entendiendo por día practicado aquel en que se respondieron 10 o más preguntas.",
      "Haber alcanzado una racha de al menos 15 días seguidos rindiendo ensayos. Se considera la racha MÁS LARGA lograda en el periodo, no la que esté activa al momento de la prueba: enfermarse un día no puede dejar a nadie fuera del premio.",
      "Que al menos 10 de esos ensayos correspondan a la misma prueba en la que se obtuvo el puntaje nacional.",
      "Presentar el certificado oficial de resultados del DEMRE, a nombre del titular de la cuenta y con el mismo RUT registrado.",
      "Que la cuenta no haya sido suspendida por uso compartido, automatización o cualquier forma de manipulación de los registros de práctica.",
    ],
  },
  {
    titulo: "4. Cuántos premios hay",
    parrafos: [
      "Hasta 5 premios por proceso de admisión, es decir un máximo de $2.500.000 en total.",
      "Si más de 5 estudiantes cumplieran todos los requisitos, ese monto total se reparte en partes iguales entre todos quienes cumplan. Nadie queda fuera por haber llegado después.",
      "Este tope existe para que la promoción sea sostenible y se declara de antemano, no se aplica después.",
    ],
  },
  {
    titulo: "5. Cómo se reclama",
    parrafos: [
      "Escribiendo a 1000paessoporte@gmail.com dentro de los 30 días corridos siguientes a la publicación oficial de resultados del DEMRE, adjuntando el certificado de puntajes.",
      "1000paes verificará el cumplimiento de los requisitos con los registros de la cuenta y responderá dentro de 15 días hábiles.",
      "El pago se hace por transferencia bancaria a nombre del titular o de su apoderado, dentro de los 30 días hábiles siguientes a la confirmación.",
    ],
  },
  {
    titulo: "6. Vigencia y cambios",
    parrafos: [
      "Estas bases rigen para el proceso de admisión 2027 y estarán publicadas en esta página durante toda su vigencia.",
      "1000paes puede modificar o terminar la promoción avisando en esta misma página, pero los cambios no afectan a quien ya cumplía los requisitos al momento del aviso.",
      "El premio no es transferible ni canjeable por otro beneficio.",
    ],
  },
] as const;

export default function PremioPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-16">
      <p className="text-xs font-medium tracking-wide text-accent uppercase">
        Bases de la promoción
      </p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight">
        $500.000 por puntaje nacional
      </h1>
      <p className="mt-3 text-base leading-relaxed text-muted">
        Si obtienes 1.000 puntos en cualquiera de las cinco pruebas PAES y
        preparaste esa prueba con nosotros, te entregamos medio millón de pesos.
        Acá está todo lo que hay que cumplir, sin letra chica.
      </p>

      <div className="mt-10 flex flex-col gap-8">
        {SECCIONES.map((seccion) => (
          <section key={seccion.titulo}>
            <h2 className="text-lg font-semibold tracking-tight">{seccion.titulo}</h2>
            {"parrafos" in seccion &&
              seccion.parrafos.map((p) => (
                <p key={p} className="mt-2 text-sm leading-relaxed text-muted">
                  {p}
                </p>
              ))}
            {"lista" in seccion && (
              <ul className="mt-3 flex flex-col gap-2">
                {seccion.lista.map((item) => (
                  <li key={item} className="flex gap-2.5 text-sm leading-relaxed">
                    <span aria-hidden className="mt-0.5 shrink-0 text-accent">
                      ✓
                    </span>
                    <span className="text-muted">{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </div>

      <p className="mt-10 rounded-xl border border-border bg-surface p-5 text-sm leading-relaxed text-muted">
        La promoción empieza a correr cuando el plan Pro esté disponible para
        contratar. Hasta entonces estas bases son informativas: ningún requisito
        de meses pagados puede cumplirse todavía.
      </p>

      <p className="mt-8 text-center text-sm">
        <Link
          href="/#planes"
          className="text-accent underline-offset-4 hover:underline"
        >
          ← Volver a los planes
        </Link>
      </p>
    </main>
  );
}
