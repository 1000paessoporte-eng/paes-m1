import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getExamOptions, getRepaso, listExamAttempts } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { ExamRunner } from "@/components/exam/exam-runner";

export default async function ModoEnsayoPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let attempts: Awaited<ReturnType<typeof listExamAttempts>> = [];
  try {
    attempts = await listExamAttempts(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login");
  }

  const [optionsM1, repasoM1, optionsM2, repasoM2] = await Promise.all([
    getExamOptions(token, "m1"),
    getRepaso(token, "m1"),
    getExamOptions(token, "m2"),
    getRepaso(token, "m2"),
  ]);

  const pastAttempts = attempts.filter((a) => a.status === "submitted");
  const resumableAttemptId =
    attempts.find((a) => a.status === "in_progress")?.attempt_id ?? null;

  return (
    <ExamRunner
      optionsBySubject={{ m1: optionsM1, m2: optionsM2 }}
      repasoBySubject={{ m1: repasoM1, m2: repasoM2 }}
      pastAttempts={pastAttempts}
      resumableAttemptId={resumableAttemptId}
    />
  );
}
