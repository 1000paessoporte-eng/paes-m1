import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";
import { EMAIL_CONTACTO } from "@/lib/redes-sociales";
import { AUDITORIA_CONTENIDO } from "@/lib/legal";

export const metadata: Metadata = {
  title: "Información legal",
  description:
    "Documentos legales de 1000paes: origen del contenido, propiedad intelectual, términos, privacidad y canal de reclamos.",
  alternates: { canonical: "/legal" },
};

/**
 * Sección legal del sitio.
 *
 * Existe por una razón concreta: 1000paes prepara para una prueba cuyas
 * preguntas liberadas tienen derechos de la Universidad de Chile, y cobra por
 * hacerlo. La defensa de un producto así no se improvisa el día que llega una
 * carta; se escribe antes, y se apoya en algo medible.
 *
 * Por eso esta página no se limita a decir "nuestro contenido es original".
 * Declara QUÉ se usa de fuentes oficiales y por qué es legítimo usarlo, QUÉ no
 * se usa, y CÓMO se comprueba, con una cifra y una fecha que salen de un script
 * versionado en el repositorio (`apps/api/scripts/auditar_derechos.py`). Una
 * afirmación verificable vale mucho más que una promesa.
 *
 * El canal de reclamos del final es igual de deliberado: le da a cualquier
 * titular de derechos una vía rápida y sin abogados para plantear un problema.
 * La mayoría de los conflictos de propiedad intelectual terminan ahí cuando esa
 * vía existe, y no existe cuando nadie la escribió.
 */

const DOCUMENTOS = [
  {
    href: "/terminos",
    titulo: "Términos y condiciones",
    resumen:
      "Qué es el servicio, cómo funcionan los planes y los cobros, el derecho a retracto, la cancelación y las reglas para estudiantes menores de edad.",
  },
  {
    href: "/privacidad",
    titulo: "Política de privacidad",
    resumen:
      "Qué datos se recogen, con qué finalidad y base legal, dónde se alojan, cuánto se conservan y cómo ejercer tus derechos sobre ellos.",
  },
  {
    href: "/premio",
    titulo: "Bases del premio",
    resumen:
      "Condiciones completas del premio a puntaje nacional: requisitos, plazos, tope de premios y forma de entrega.",
  },
];

export default function LegalPage() {
  return (
    <>
      <main className="flex-1 px-6 py-16">
        <article className="mx-auto max-w-2xl">
          <h1 className="text-2xl font-semibold tracking-tight">
            Información legal
          </h1>
          <p className="mt-2 text-sm text-muted">
            Última actualización: septiembre de 2026.
          </p>

          <div className="mt-8 flex flex-col gap-6 text-sm leading-relaxed text-muted [&_h2]:text-base [&_h2]:font-semibold [&_h2]:text-foreground [&_h3]:text-sm [&_h3]:font-semibold [&_h3]:text-foreground [&_p]:mt-2 [&_ul]:mt-2 [&_ul]:list-disc [&_ul]:pl-5 [&_li]:mt-1">
            <section>
              <h2>Documentos</h2>
              <ul className="!list-none !pl-0">
                {DOCUMENTOS.map((d) => (
                  <li key={d.href} className="!mt-3">
                    <Link
                      href={d.href}
                      className="font-medium text-accent hover:underline"
                    >
                      {d.titulo}
                    </Link>
                    <span className="block">{d.resumen}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section>
              <h2>Declaración sobre el contenido</h2>
              <p>
                Esta sección explica de dónde viene cada cosa que ves en
                1000paes. Está escrita para que cualquier persona —incluido un
                titular de derechos— pueda verificarla, y no solo creerla.
              </p>

              <h3 className="!mt-5">Las preguntas son de elaboración propia</h3>
              <p>
                Todas las preguntas, alternativas, explicaciones y figuras de la
                plataforma están escritas para 1000paes.{" "}
                <strong>
                  No son reproducciones, traducciones ni adaptaciones de
                  preguntas de pruebas oficiales
                </strong>
                , cuyos derechos pertenecen a la Universidad de Chile.
              </p>

              <h3 className="!mt-5">Qué sí usamos de fuentes oficiales</h3>
              <ul>
                <li>
                  <strong>El temario publicado por el DEMRE.</strong> Es el
                  listado de contenidos y habilidades que la prueba evalúa. El
                  DEMRE lo publica precisamente para que quienes rinden se
                  preparen, y los contenidos de una materia no son objeto de
                  derecho de autor: lo que la ley protege es la forma de
                  expresarlos, no el hecho de que la estequiometría entre en la
                  prueba.
                </li>
                <li>
                  <strong>El formato y el nivel de dificultad.</strong> Número
                  de preguntas, alternativas por pregunta, duración y reparto
                  por eje. Son características funcionales del examen, no
                  expresión protegible.
                </li>
                <li>
                  <strong>
                    Las tablas de transformación de puntaje del DEMRE.
                  </strong>{" "}
                  Son datos oficiales y se usan solo para estimar un puntaje
                  referencial. En el código de la plataforma cada tabla lleva
                  indicado el proceso y la publicación de la que proviene.
                </li>
                <li>
                  <strong>
                    La oferta de carreras, vacantes y ponderaciones.
                  </strong>{" "}
                  Es información pública del proceso de admisión. Cada ficha de
                  carrera enlaza a la publicación oficial de la que salió el
                  dato.
                </li>
              </ul>

              <h3 className="!mt-5">Qué no usamos</h3>
              <p>
                Preguntas, enunciados, textos base, gráficos ni figuras de las
                pruebas oficiales, ni siquiera parafraseados. Los textos de
                Competencia Lectora son originales de 1000paes o de dominio
                público, y cada uno declara su origen en la propia pantalla
                donde se lee.
              </p>

              <h3 className="!mt-5">Cómo lo comprobamos</h3>
              <p>
                No basta con afirmarlo. El repositorio incluye un script que
                compara el banco completo contra los folletos oficiales
                liberados por el DEMRE y mide la secuencia de palabras
                consecutivas más larga que ambos comparten, después de
                normalizar el texto para que un cambio cosmético no esconda una
                copia.
              </p>
              <p>
                Resultado de la última ejecución, del{" "}
                <strong>{AUDITORIA_CONTENIDO.fecha}</strong>, sobre{" "}
                <strong>{AUDITORIA_CONTENIDO.piezas}</strong> piezas del banco
                y {AUDITORIA_CONTENIDO.folletos} folletos oficiales de las cinco
                pruebas:
              </p>
              <ul>
                <li>
                  <strong>
                    Cero coincidencias de {AUDITORIA_CONTENIDO.umbral} palabras
                    consecutivas o más.
                  </strong>
                </li>
                <li>
                  La coincidencia más larga encontrada es de{" "}
                  {AUDITORIA_CONTENIDO.maximo} palabras, en{" "}
                  {AUDITORIA_CONTENIDO.piezasEnElMaximo} piezas.
                </li>
                <li>
                  {AUDITORIA_CONTENIDO.sinCoincidencia} piezas no comparten
                  ninguna secuencia de seis palabras con las pruebas oficiales.
                </li>
              </ul>
              <p>
                Lo poco que coincide es lenguaje propio de cualquier prueba de
                selección múltiple —«¿cuál es la probabilidad de que…?», «de
                acuerdo con el texto leído»— y expresiones de uso corriente que
                no constituyen creación protegible.
              </p>
              <p>
                La comprobación se repite cada vez que el banco crece y el
                informe queda archivado con su fecha. Si eres titular de
                derechos y quieres revisarlo, escríbenos y te lo enviamos.
              </p>

              <h3 className="!mt-5">Marcas y afiliación</h3>
              <p>
                «PAES» y «DEMRE» son denominaciones de terceros y se usan aquí
                solo de manera descriptiva, para identificar la prueba para la
                que esta plataforma prepara.{" "}
                <strong>
                  1000paes no está afiliado, patrocinado ni respaldado por el
                  DEMRE, por la Universidad de Chile, por el Ministerio de
                  Educación ni por ninguna institución del proceso de admisión.
                </strong>{" "}
                No usamos sus logotipos ni sugerimos vínculo alguno con ellos.
              </p>
            </section>

            <section>
              <h2>Reclamos sobre propiedad intelectual</h2>
              <p>
                Si eres titular de un derecho y crees que algún contenido de
                1000paes lo infringe, escríbenos a{" "}
                <a
                  href={`mailto:${EMAIL_CONTACTO}?subject=${encodeURIComponent(
                    "Reclamo de propiedad intelectual"
                  )}`}
                  className="text-accent hover:underline"
                >
                  {EMAIL_CONTACTO}
                </a>{" "}
                indicando:
              </p>
              <ul>
                <li>Qué contenido específico reclamas y dónde está.</li>
                <li>Qué derecho invocas y sobre qué obra.</li>
                <li>Tus datos de contacto.</li>
              </ul>
              <p>
                Nos comprometemos a{" "}
                <strong>responder dentro de 5 días hábiles</strong> y, si el
                reclamo tiene fundamento,{" "}
                <strong>retirar o reescribir el contenido</strong> sin necesidad
                de que medie una acción judicial. Preferimos corregir a discutir.
              </p>
            </section>

            <section>
              <h2>Responsable del sitio y reclamos de consumo</h2>
              <p>
                1000paes es operado desde Chile y se rige por la ley chilena.
                Para cualquier consulta, reclamo o solicitud sobre el servicio,
                los cobros o tus datos, el canal es{" "}
                <a
                  href={`mailto:${EMAIL_CONTACTO}`}
                  className="text-accent hover:underline"
                >
                  {EMAIL_CONTACTO}
                </a>
                . Respondemos dentro de 5 días hábiles.
              </p>
              <p>
                Esto no reemplaza tus derechos como consumidor: puedes acudir
                siempre al Servicio Nacional del Consumidor (SERNAC) o a los
                tribunales que correspondan.
              </p>
            </section>
          </div>
        </article>
      </main>
      <SiteFooter />
    </>
  );
}
