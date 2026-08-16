import type { Metadata } from "next";
import { Geist_Mono, Inter, Plus_Jakarta_Sans } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { PageViewTracker } from "@/components/metrics/page-view-tracker";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

// Dos fuentes con trabajos distintos: la geométrica para titulares y números
// grandes, la de lectura para todo lo demás. `display: swap` deja el texto
// visible mientras cargan, que en móvil con red mala es la diferencia entre
// leer y esperar.
const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const BASE_URL = "https://1000paes.cl";
const TITLE = "1000paes — Prepara tu PAES";
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

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es"
      className={`${jakarta.variable} ${inter.variable} ${geistMono.variable} h-full antialiased`}
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
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
