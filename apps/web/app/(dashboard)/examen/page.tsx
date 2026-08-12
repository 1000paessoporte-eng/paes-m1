import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getExamOptions, listExamAttempts } from "@/lib/api";
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

  const options = await getExamOptions(token);

  const pastAttempts = attempts.filter((a) => a.status === "submitted");
  const resumableAttemptId =
    attempts.find((a) => a.status === "in_progress")?.attempt_id ?? null;

  return (
    <ExamRunner
      options={options}
      pastAttempts={pastAttempts}
      resumableAttemptId={resumableAttemptId}
    />
  );
}
