import type { MetadataRoute } from "next";
import { getCarrerasCatalogo, getLecciones } from "@/lib/api";
import { slugCarrera, slugUniversidad } from "@/lib/carreras";

const BASE_URL = "https://1000paes.cl";

/**
 * El sitemap.
 *
 * Hasta que existió el catálogo público esto eran nueve URLs estáticas, y las
 * 1.855 carreras que ya estaban en la base no las veía Google. Ahora el
 * sitemap se arma con el catálogo real, así que crece solo cuando el DEMRE
 * publica una oferta nueva.
 *
 * Se revalida cada día porque las ponderaciones cambian una vez por proceso de
 * admisión, y porque un sitemap que se regenera en cada request es una
 * consulta a la base por cada visita de un rastreador.
 */
export const revalidate = 86400;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const estaticas: MetadataRoute.Sitemap = [
    { url: BASE_URL, changeFrequency: "weekly", priority: 1 },
    { url: `${BASE_URL}/carreras`, changeFrequency: "monthly", priority: 0.9 },
    // Las lecciones son el otro contenido que existe para ser encontrado
    // buscando: la teoría de cada tema del temario, legible sin cuenta.
    { url: `${BASE_URL}/aprender`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE_URL}/demo`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${BASE_URL}/planes`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE_URL}/registro`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${BASE_URL}/sobre-nosotros`, changeFrequency: "monthly", priority: 0.7 },
    {
      url: `${BASE_URL}/preguntas-frecuentes`,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    // Las bases del premio se indexan: una promoción con premio en dinero
    // tiene que ser públicamente consultable, no solo alcanzable desde un
    // enlace dentro de la página de planes.
    { url: `${BASE_URL}/premio`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE_URL}/login`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE_URL}/terminos`, changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/privacidad`, changeFrequency: "yearly", priority: 0.3 },
  ];

  // Cada índice cae por su cuenta: que el catálogo no responda no puede dejar
  // las lecciones fuera del sitemap, ni al revés.
  let lecciones: MetadataRoute.Sitemap = [];
  try {
    lecciones = (await getLecciones()).map((l) => ({
      url: `${BASE_URL}/aprender/${l.node_code}`,
      changeFrequency: "monthly" as const,
      priority: 0.8,
    }));
  } catch {
    lecciones = [];
  }

  let catalogo;
  try {
    catalogo = await getCarrerasCatalogo();
  } catch {
    // Si la API no responde, un sitemap con las páginas estáticas es mucho
    // mejor que un 500: Google reintenta, pero un error repetido le enseña a
    // pedirlo menos seguido.
    return [...estaticas, ...lecciones];
  }

  const universidades = [...new Set(catalogo.map((c) => c.universidad))].map(
    (universidad) => ({
      url: `${BASE_URL}/carreras/${slugUniversidad(universidad)}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })
  );

  const carreras = catalogo.map((c) => ({
    url: `${BASE_URL}/carrera/${slugCarrera(c)}`,
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }));

  return [...estaticas, ...lecciones, ...universidades, ...carreras];
}
