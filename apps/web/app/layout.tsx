import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { PageViewTracker } from "@/components/metrics/page-view-tracker";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const BASE_URL = "https://1000paes.cl";
const TITLE = "1000paes — Prepara tu PAES";
const DESCRIPTION =
  "Ensayos PAES cronometrados con puntaje estimado, árbol de habilidades y seguimiento de tu progreso. Competencia Matemática M1 y M2 disponibles.";

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
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
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
