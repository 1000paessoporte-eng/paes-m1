import type { Metadata } from "next";
import { DemoRunner } from "@/components/demo/demo-runner";

export const metadata: Metadata = {
  title: "Prueba sin cuenta",
  alternates: { canonical: "/demo" },
};

export default function DemoPage() {
  return (
    <main className="flex flex-1 flex-col px-6 py-16">
      <DemoRunner />
    </main>
  );
}
