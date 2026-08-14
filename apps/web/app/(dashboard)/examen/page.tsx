import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getExamOptions, getRepaso, listExamAttempts } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { ExamRunner } from "@/components/exam/exam-runner";

export const metadata = {
  title: "Modo Ensayo",
  description: "Arma un ensayo con el tiempo proporcional al de la prueba real.",
};


export default async function ModoEnsayoPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let attempts: Awaited<ReturnType<typeof listExamAttempts>> = [];
  try {
    attempts = await listExamAttempts(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/examen");
  }

  const [
    optionsM1,
    repasoM1,
    optionsM2,
    repasoM2,
    optionsLectora,
    repasoLectora,
    optionsCiencias,
    repasoCiencias,
    optionsHistoria,
    repasoHistoria,
  ] =
    await Promise.all([
      getExamOptions(token, "m1"),
      getRepaso(token, "m1"),
      getExamOptions(token, "m2"),
      getRepaso(token, "m2"),
      getExamOptions(token, "lectora"),
      getRepaso(token, "lectora"),
      getExamOptions(token, "ciencias"),
      getRepaso(token, "ciencias"),
      getExamOptions(token, "historia"),
      getRepaso(token, "historia"),
    ]);

  const pastAttempts = attempts.filter((a) => a.status === "submitted");
  // Se pasa también el subject: el ensayo pendiente puede ser de otra prueba
  // que la elegida en pantalla, y retomarlo cambia de prueba. Hay que decirlo.
  const enCurso = attempts.find((a) => a.status === "in_progress");

  return (
    <ExamRunner
      optionsBySubject={{
        m1: optionsM1,
        m2: optionsM2,
        lectora: optionsLectora,
        ciencias: optionsCiencias,
        historia: optionsHistoria,
      }}
      repasoBySubject={{
        m1: repasoM1,
        m2: repasoM2,
        lectora: repasoLectora,
        ciencias: repasoCiencias,
        historia: repasoHistoria,
      }}
      pastAttempts={pastAttempts}
      resumable={
        enCurso ? { attemptId: enCurso.attempt_id, subject: enCurso.subject } : null
      }
    />
  );
}
