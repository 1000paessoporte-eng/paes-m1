import type { Metadata } from "next";
import { DemoRunner } from "@/components/demo/demo-runner";
import type { Subject } from "@/lib/api";

export const metadata: Metadata = {
  title: "Prueba sin cuenta",
  alternates: { canonical: "/demo" },
};

/** Las cinco pruebas. Cualquier otra cosa en la URL cae en M1. */
const PRUEBAS: Subject[] = ["lectora", "m1", "m2", "ciencias", "historia"];

export default async function DemoPage({ searchParams }: PageProps<"/demo">) {
  // La portada enlaza directo a la prueba que el visitante eligió, así que la
  // demo abre ya en esa. El valor viene de la URL: se valida contra la lista
  // en vez de confiar, porque de ahí sale la llamada a la API.
  const { prueba } = await searchParams;
  const pedida = Array.isArray(prueba) ? prueba[0] : prueba;
  const inicial = PRUEBAS.find((p) => p === pedida) ?? "m1";

  return (
    <main className="flex flex-1 flex-col px-6 py-16">
      <DemoRunner inicial={inicial} />
    </main>
  );
}
