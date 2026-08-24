import type { MetadataRoute } from "next";

/**
 * Lo que Android necesita para tratar 1000paes como una app.
 *
 * Sin manifiesto, "Agregar a la pantalla de inicio" guarda un acceso directo
 * sin nombre propio ni color, y el navegador nunca ofrece instalar la web. Para
 * un producto que se usa desde el teléfono mientras se estudia, ese atajo es la
 * diferencia entre volver mañana y no volver.
 *
 * `display: "standalone"` la abre sin barra de direcciones: cuando alguien está
 * rindiendo un ensayo cronometrado, la barra solo ofrece formas de salirse.
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "1000paes — Ensayos PAES",
    short_name: "1000paes",
    description:
      "Ensayos PAES cronometrados con puntaje estimado, árbol de habilidades y seguimiento de tu progreso.",
    start_url: "/",
    display: "standalone",
    lang: "es-CL",
    // Papel y grafito, los dos colores de la marca. El color de las pruebas no
    // entra acá: significa "qué prueba es", y la marca es acromática.
    background_color: "#ffffff",
    theme_color: "#2b2b33",
    icons: [
      { src: "/favicon.ico", sizes: "any", type: "image/x-icon" },
      { src: "/apple-icon", sizes: "180x180", type: "image/png" },
    ],
  };
}
