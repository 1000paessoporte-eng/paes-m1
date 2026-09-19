import Link from "next/link";

export const metadata = {
  title: "Premio Puntaje Nacional",
  description:
    "Bases del premio de $500.000 para estudiantes con plan Pro que obtengan puntaje nacional en la PAES regular de la Admisión 2028.",
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
 *
 * Rige para la Admisión 2028 y no la 2027: el plan Pro se pudo contratar
 * recién en agosto de 2026, así que para la PAES de noviembre de ese año nadie
 * alcanzaba a juntar los 6 meses. Anunciar un premio que nadie puede ganar es
 * publicidad engañosa (Ley 19.496, art. 28).
 *
 * Pendiente: definir con un contador quién paga los impuestos del premio.
 */

const SECCIONES = [
  {
    titulo: "1. Quién organiza y a quién aplica",
    parrafos: [
      "El premio lo organiza y lo paga 1000PAES SpA, RUT 78.516.038-K, sociedad chilena con domicilio en la Región del Maule (en adelante, 1000paes), a estudiantes que rindan la PAES regular del proceso de Admisión 2028, que se rinde a fines de 2027, y que cumplan TODOS los requisitos de la sección 3.",
      "Solo cuenta el puntaje de la PAES regular. La PAES de invierno no participa.",
      "El titular de la cuenta debe ser la misma persona que rinde la prueba. Las cuentas compartidas entre varios estudiantes quedan fuera, porque el requisito de práctica dejaría de significar algo.",
      "Si el estudiante es menor de edad, el premio se entrega a su madre, padre o apoderado, quien deberá aceptar las bases.",
    ],
  },
  {
    titulo: "2. Qué se premia",
    parrafos: [
      "$500.000 (quinientos mil pesos chilenos) por obtener 1.000 puntos —puntaje nacional— en la PAES regular, en cualquiera de las cinco pruebas: Competencia Lectora, Competencia Matemática M1, Competencia Matemática M2, Ciencias, o Historia y Ciencias Sociales.",
      "El premio se entrega una sola vez por persona, aunque obtenga puntaje nacional en más de una prueba.",
      "No es un sorteo ni depende del azar: se obtiene por el resultado de la prueba.",
    ],
  },
  {
    titulo: "3. Requisitos",
    lista: [
      "Haber tenido plan Pro o superior activo por al menos 6 meses, sumados, dentro de los 12 meses anteriores al primer día de la PAES regular. No necesitan ser consecutivos.",
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
    titulo: "6. Publicación de resultados",
    parrafos: [
      "Dentro de los 60 días corridos siguientes a la publicación oficial de resultados del DEMRE, 1000paes publicará en esta página cuántos premios se entregaron y el monto pagado a cada ganador.",
      "Los nombres de los ganadores se publican solo con su autorización escrita o, si es menor de edad, con la de su madre, padre o apoderado.",
    ],
  },
  {
    titulo: "7. Vigencia y cambios",
    parrafos: [
      "Estas bases rigen desde el 21 de septiembre de 2026 para el proceso de Admisión 2028, y estarán publicadas en esta página durante toda su vigencia.",
      "Las bases solo pueden modificarse para ampliar plazos, bajar requisitos o aumentar el premio. Ningún cambio puede perjudicar a quien participa.",
      "Si la promoción terminara antes de tiempo, quienes hayan contratado el plan Pro durante su vigencia conservan el derecho a participar con las bases vigentes al momento de contratar.",
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
        Este premio es para quienes rinden la PAES regular a fines de 2027. Si
        rindes la PAES este año (2026), no alcanzas a cumplir los 6 meses de
        plan Pro que se piden, y preferimos decírtelo claro desde ahora.
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
