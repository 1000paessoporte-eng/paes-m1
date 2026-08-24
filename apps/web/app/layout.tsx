import type { Metadata } from "next";
import { Bricolage_Grotesque, Instrument_Sans, Source_Serif_4 } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { DatosEstructurados } from "@/components/datos-estructurados";
import { PageViewTracker } from "@/components/metrics/page-view-tracker";
import { ReporteroErrores } from "@/components/reportero-errores";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

/* Tres fuentes, tres trabajos. Ninguna está por gusto.
 *
 * BRICOLAGE GROTESQUE para titulares y números. Es una grotesca variable con
 * carácter: ancha, con remates cortados y un eje óptico que aprieta las
 * mayúsculas cuando el tamaño sube. Reemplaza a Plus Jakarta, que es la fuente
 * con la que se ve la mitad de internet y no decía nada de esta prueba.
 *
 * INSTRUMENT SANS para la interfaz y el texto corriente. Altura de x grande
 * --clave para leer enunciados en un teléfono-- y figuras tabulares para los
 * relojes y los puntajes.
 *
 * SOURCE SERIF para los textos de Competencia Lectora y la teoría de las
 * lecciones. No es decoración: son los dos lugares donde se lee de corrido y
 * en pantalla, y una serif marca "esto es un texto para leer", distinto del
 * cromo de la interfaz que lo rodea.
 *
 * Se fue la monoespaciada: `tabular-nums` alinea el reloj igual de bien y sin
 * una cuarta familia que descargar en un 4G chileno.
 *
 * `display: swap` deja el texto visible mientras cargan, que en móvil con red
 * mala es la diferencia entre leer y esperar.
 */
const bricolage = Bricolage_Grotesque({
  variable: "--fuente-display",
  subsets: ["latin"],
  display: "swap",
});

const instrument = Instrument_Sans({
  variable: "--fuente-ui",
  subsets: ["latin"],
  display: "swap",
});

const sourceSerif = Source_Serif_4({
  variable: "--fuente-lectura",
  subsets: ["latin"],
  display: "swap",
});

const BASE_URL = "https://1000paes.cl";
//: El título es lo que se lee en el resultado de Google, así que nombra lo
//: que la gente escribe en el buscador —"ensayos PAES", "puntaje"— y no el
//: nombre del producto, que nadie busca todavía. Antes decía "1000paes —
//: Prepara tu PAES": correcto y sin una sola palabra por la que alguien
//: pudiera encontrarnos. La marca va al final, donde no ocupa el espacio que
//: Google recorta.
const TITLE = "Ensayos PAES gratis con puntaje oficial — 1000paes";
const DESCRIPTION =
  "Ensayos PAES cronometrados con puntaje estimado, árbol de habilidades y seguimiento de tu progreso. Las cinco pruebas: Competencia Lectora, Matemática M1 y M2, Ciencias, e Historia.";

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),
  title: {
    default: TITLE,
    template: "%s — 1000paes",
  },
  description: DESCRIPTION,
  keywords: ["PAES", "PAES M1", "PAES M2", "ensayo PAES", "puntaje PAES", "admisión universitaria Chile"],
  openGraph: {
    type: "website",
    locale: "es_CL",
    url: BASE_URL,
    siteName: "1000paes",
    title: TITLE,
    description: DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

/**
 * Quiénes somos, para Google.
 *
 * Va en el layout y no en la portada porque describe al sitio entero: es lo
 * que le permite a Google saber que 1000paes es una organización con un sitio,
 * y no una página suelta.
 *
 * Lleva `SearchAction` desde que existe el buscador público de carreras: es lo
 * que permite que Google ofrezca esa caja dentro del propio resultado de
 * búsqueda. Apunta a /carreras?q=, que es una búsqueda real y sin sesión; si
 * ese buscador desapareciera, esto tiene que salir con él, porque anunciar una
 * acción que no funciona es un dato inventado como cualquier otro.
 */
const DATOS_DEL_SITIO = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${BASE_URL}/#organizacion`,
      name: "1000paes",
      url: BASE_URL,
      description: DESCRIPTION,
      areaServed: { "@type": "Country", name: "Chile" },
    },
    {
      "@type": "WebSite",
      "@id": `${BASE_URL}/#sitio`,
      url: BASE_URL,
      name: "1000paes",
      inLanguage: "es-CL",
      publisher: { "@id": `${BASE_URL}/#organizacion` },
      potentialAction: {
        "@type": "SearchAction",
        target: {
          "@type": "EntryPoint",
          urlTemplate: `${BASE_URL}/carreras?q={search_term_string}`,
        },
        "query-input": "required name=search_term_string",
      },
    },
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es"
      className={`${bricolage.variable} ${instrument.variable} ${sourceSerif.variable} h-full antialiased`}
      // El scroll suave es nuestro y deliberado; sin este atributo Next avisa
      // en cada carga que podría interferir con sus transiciones de ruta.
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <head>
        {/* El tema se aplica ANTES de pintar. Sin esto, quien eligió modo
            oscuro ve un fogonazo blanco en cada carga: el HTML llega claro y
            React recién corrige después de hidratar. Es un script mínimo y
            síncrono a propósito. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem("tema");if(t==="dark"||t==="light"){document.documentElement.setAttribute("data-theme",t)}}catch(e){}})()`,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col text-foreground">
        <SiteHeader />
        {children}
        <PageViewTracker />
        <ReporteroErrores />
        <DatosEstructurados datos={DATOS_DEL_SITIO} />
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
