import type { MetadataRoute } from "next";

const BASE_URL = "https://1000paes.cl";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      // Paneles con datos de sesión (no aportan a SEO) y el link de reseteo
      // de contraseña (lleva un token en la URL: no debe quedar indexado).
      disallow: [
        "/arbol",
        "/examen",
        "/historial",
        "/analitica",
        "/perfil",
        "/practicar/",
        "/restablecer-contrasena",
      ],
    },
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
