import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, listExamAttempts } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { HistoryView } from "@/components/history/history-view";

export const metadata = {
  title: "Mi progreso",
  description: "Todos tus ensayos con la evolución de tu puntaje.",
};


export default async function HistorialPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let attempts: Awaited<ReturnType<typeof listExamAttempts>> = [];
  try {
    attempts = await listExamAttempts(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/historial");
  }

  // Solo los ensayos terminados tienen puntaje; los en curso no son historial.
  const rendidos = attempts.filter((a) => a.status === "submitted");

  return <HistoryView intentos={rendidos} />;
}
