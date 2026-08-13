import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Preguntas frecuentes",
  description:
    "Cómo funciona 1000paes: qué pruebas cubre, cómo se calcula el puntaje estimado, si es gratis y qué necesitas para empezar.",
};

/**
 * Todas las respuestas describen lo que la plataforma hace HOY. Si cambia el
 * producto (pruebas disponibles, tamaño del banco, planes), hay que
 * actualizarlas acá: es la página que la gente lee antes de registrarse.
 */
const PREGUNTAS = [
  {
    q: "¿1000paes es gratis?",
    a: "Sí. Hoy todo lo que ves está disponible sin costo y sin pedir tarjeta: ensayos, puntaje estimado, resolución de cada ejercicio, árbol de habilidades e historial. Estamos en beta. Más adelante van a existir planes de pago con funciones adicionales, y los precios se anunciarán en la propia página antes de cobrar nada.",
  },
  {
    q: "¿Qué pruebas de la PAES puedo practicar?",
    a: "Hoy están disponibles Competencia Matemática M1 y Competencia Matemática M2. Competencia Lectora, Historia y Ciencias Sociales, y Ciencias aparecen en el selector como \"Próximamente\": la plataforma está pensada para cubrir las cinco pruebas, y las vamos habilitando a medida que su banco de preguntas está listo.",
  },
  {
    q: "¿Cómo se calcula el puntaje estimado?",
    a: "Con las tablas de transformación que publica el DEMRE para cada prueba, no con una fórmula inventada. Como puedes rendir ensayos más cortos que la prueba oficial, tu proporción de aciertos se escala a la cantidad de preguntas que puntúan en la prueba real y se interpola en esa tabla. Es una estimación referencial: el puntaje real depende de la forma que te toque y del proceso de admisión de ese año.",
  },
  {
    q: "¿El tiempo del ensayo es el mismo que el de la prueba real?",
    a: "Sí, proporcional. Cada prueba tiene su propia razón de minutos por pregunta según el temario oficial (M1 son 65 preguntas en 140 minutos; M2 son 55 preguntas en 140 minutos), y el cronómetro la respeta según cuántas preguntas elijas. Además puedes elegir el ritmo: oficial, exigente (20% menos de tiempo, para entrenar bajo presión) o relajado (25% más, para estudiar con calma).",
  },
  {
    q: "¿Necesito crear una cuenta?",
    a: "Para rendir ensayos completos y que se guarde tu progreso, sí. Puedes registrarte con tu correo o entrar directamente con tu cuenta de Google. Si solo quieres ver de qué se trata, hay una demo de 5 preguntas que no pide cuenta ni guarda nada.",
  },
  {
    q: "¿Qué pasa si cierro la pestaña en medio de un ensayo?",
    a: "No pierdes nada. Cada respuesta se guarda sola apenas la marcas, así que al volver a entrar puedes retomar el ensayo justo donde lo dejaste, con el tiempo que te quedaba. Funciona incluso desde otro dispositivo, porque el intento vive en tu cuenta y no en el navegador.",
  },
  {
    q: "¿Puedo ver por qué me equivoqué en una pregunta?",
    a: "Sí, y es el punto central de la plataforma. Al terminar el ensayo ves el desarrollo paso a paso de cada ejercicio: no solo cuál era la alternativa correcta, sino el razonamiento completo para llegar a ella. Además obtienes el desglose de tu desempeño por eje temático, por dificultad y por tema específico.",
  },
  {
    q: "¿Qué es el Árbol de Habilidades?",
    a: "Es el temario presentado como un mapa de nodos conectados en vez de una lista plana. Cada nodo es un tema (por ejemplo, Teorema de Pitágoras) y se desbloquea cuando demuestras dominio en los temas que le sirven de base. Así sabes en qué orden conviene estudiar, y no te encuentras con un tema avanzado antes de tener los fundamentos.",
  },
  {
    q: "¿Puedo practicar un tema puntual sin rendir un ensayo completo?",
    a: "Sí. Desde el Árbol de Habilidades puedes entrar a un nodo específico y practicarlo pregunta por pregunta, con corrección inmediata después de cada respuesta. Sirve para reforzar algo puntual sin comprometer los 140 minutos de un ensayo completo.",
  },
  {
    q: "¿1000paes tiene relación con el DEMRE?",
    a: "No. 1000paes es una plataforma independiente y no tiene relación con el DEMRE ni con ninguna institución oficial del proceso de admisión. Usamos como referencia los temarios y las tablas de puntaje que el DEMRE publica públicamente, pero las preguntas de los ensayos son de elaboración propia.",
  },
  {
    q: "¿Puedo borrar mis datos?",
    a: "Sí. Puedes borrar cualquier ensayo de tu historial cuando quieras, y también descargar un respaldo de tu progreso en formato JSON antes de hacerlo. Los detalles de qué guardamos y por qué están en la política de privacidad.",
  },
] as const;

export default function PreguntasFrecuentesPage() {
  return (
    <>
      <main className="flex-1 px-6 py-16">
        <article className="mx-auto max-w-2xl">
          <h1 className="text-3xl font-bold tracking-tight">Preguntas frecuentes</h1>
          <p className="mt-3 text-muted">
            Todo lo que suelen preguntar antes de empezar. Si te queda una duda
            que no está acá, escríbenos por nuestras redes.
          </p>

          <div className="mt-10 flex flex-col gap-3">
            {PREGUNTAS.map((item) => (
              <details
                key={item.q}
                className="group rounded-xl border border-border bg-surface p-5 open:bg-surface"
              >
                <summary className="flex cursor-pointer list-none items-start justify-between gap-4 font-semibold text-foreground">
                  {item.q}
                  <span className="mt-0.5 shrink-0 text-muted transition-transform group-open:rotate-45">
                    <PlusIcon />
                  </span>
                </summary>
                <p className="mt-3 text-sm leading-relaxed text-muted">{item.a}</p>
              </details>
            ))}
          </div>

          <div className="mt-12 rounded-xl border border-accent/40 bg-accent/5 p-6 text-center">
            <h2 className="font-semibold">¿Listo para tu primer ensayo?</h2>
            <p className="mt-1.5 text-sm text-muted">
              Crear la cuenta toma un minuto y es gratis.
            </p>
            <Link
              href="/registro"
              className="btn-glow mt-4 inline-flex rounded-lg px-6 py-3 text-sm font-semibold text-accent-foreground"
            >
              Empezar gratis →
            </Link>
          </div>
        </article>
      </main>
      <SiteFooter />
    </>
  );
}

function PlusIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}
