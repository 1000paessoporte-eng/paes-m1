import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { DatosEstructurados } from "@/components/datos-estructurados";
import { SiteFooter } from "@/components/site-footer";
import { LeccionView } from "@/components/skill-tree/leccion-view";
import { ApiError, getLecciones, getLesson, type Lesson } from "@/lib/api";

/**
 * La teoría de un nodo del árbol: lo que se estudia antes de practicar.
 *
 * PÚBLICA y estática. Vivía dentro de (dashboard), así que solo la leía quien
 * ya tenía cuenta — y es el único contenido del proyecto que alguien puede
 * encontrar buscando "cómo se resuelve una ecuación de primer grado". Son 17
 * lecciones ya escritas que Google no veía. Lo que sigue detrás del login es
 * practicar y medirse, que es el producto.
 *
 * No lee la cookie de sesión: una página que la lee no se puede prerenderizar,
 * y estas existen sobre todo para quien llega de Google sin cuenta. Lo que
 * depende de la sesión lo resuelve `LeccionView` en el navegador.
 */
export const revalidate = 86400;

async function leccionDe(code: string): Promise<Lesson | null> {
  try {
    return await getLesson(code);
  } catch (err) {
    // 404 es un nodo sin lección escrita todavía, no un error del servidor.
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function generateStaticParams() {
  // Se prerenderizan todas en el build. Si la API no responde, el build no se
  // cae: las páginas se sirven bajo demanda y se cachean igual.
  try {
    return (await getLecciones()).map((l) => ({ code: l.node_code }));
  } catch {
    return [];
  }
}

export async function generateMetadata({
  params,
}: PageProps<"/aprender/[code]">): Promise<Metadata> {
  const { code } = await params;
  const leccion = await leccionDe(code).catch(() => null);
  if (!leccion) {
    return { title: "Lección no encontrada", alternates: { canonical: `/aprender/${code}` } };
  }

  // La descripción sale de la intro de la lección, que es exactamente la
  // respuesta a "¿para qué me sirve esto?". Nada escrito a mano que envejezca.
  const descripcion = leccion.intro.slice(0, 155);
  return {
    title: `${leccion.node_name} — PAES`,
    description: descripcion,
    alternates: { canonical: `/aprender/${code}` },
    openGraph: {
      title: `${leccion.node_name} — PAES`,
      description: descripcion,
      type: "article",
    },
  };
}

export default async function AprenderNodoPage({
  params,
}: PageProps<"/aprender/[code]">) {
  const { code } = await params;
  const leccion = await leccionDe(code);

  // Un nodo sin lección no es una página vacía: es una URL que no existe. El
  // 404 lo dice, en vez de dejar a Google indexando una cáscara.
  if (leccion === null) notFound();

  // Los vecinos en el índice, que ya viene ordenado por prueba y por posición
  // en el árbol. Si la API no responde, la lección se muestra sin la
  // navegación: es un extra, no puede tumbar la página.
  const indice = await getLecciones().catch(() => []);
  const posicion = indice.findIndex((l) => l.node_code === code);
  const anterior = posicion > 0 ? indice[posicion - 1] : null;
  const siguiente =
    posicion >= 0 && posicion < indice.length - 1 ? indice[posicion + 1] : null;

  return (
    <>
      <main className="flex-1 px-6 py-12">
        <LeccionView leccion={leccion} anterior={anterior} siguiente={siguiente} />
      </main>
      <SiteFooter />

      {/* Datos estructurados: le dice a Google que esto es material de
          estudio de un tema concreto, no una página cualquiera del sitio. */}
      <DatosEstructurados
        datos={{
          "@context": "https://schema.org",
          "@type": "LearningResource",
          name: leccion.node_name,
          description: leccion.intro,
          learningResourceType: "Lección",
          educationalLevel: "Educación media",
          inLanguage: "es-CL",
          isAccessibleForFree: true,
          teaches: leccion.node_name,
          provider: { "@type": "Organization", name: "1000paes" },
        }}
      />
    </>
  );
}
