import type { MetadataRoute } from "next";

const BASE_URL = "https://1000paes.cl";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: BASE_URL, changeFrequency: "weekly", priority: 1 },
    { url: `${BASE_URL}/demo`, changeFrequency: "monthly", priority: 0.8 },
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
}
