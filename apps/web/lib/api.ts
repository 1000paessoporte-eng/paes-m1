import type { paths } from "@paes-m1/types";

// En el servidor (Server Components) usamos la URL interna, rápida y sin
// depender de red externa. En el navegador (Client Components) usamos la
// URL pública, que puede ser un túnel distinto al del propio host.
const API_URL =
  typeof window === "undefined"
    ? (process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");

export type SkillNode =
  paths["/api/skill-tree"]["get"]["responses"][200]["content"]["application/json"][number];

export type Question =
  paths["/api/questions"]["get"]["responses"][200]["content"]["application/json"][number];

export type ExamStart =
  paths["/api/exam/start"]["post"]["responses"][200]["content"]["application/json"];

export type ExamState =
  paths["/api/exam/{attempt_id}"]["get"]["responses"][200]["content"]["application/json"];

export type ExamQuestion = ExamState["questions"][number];

export type ExamResult =
  paths["/api/exam/{attempt_id}/submit"]["post"]["responses"][200]["content"]["application/json"];

class ApiError extends Error {
  constructor(
    public status: number,
    path: string
  ) {
    super(`API ${path} respondió ${status}`);
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    // El árbol de habilidades y el examen cambian por intento; no cachear.
    cache: "no-store",
  });
  if (!res.ok) {
    throw new ApiError(res.status, path);
  }
  return res.json() as Promise<T>;
}

export function getSkillTree(): Promise<SkillNode[]> {
  return apiFetch<SkillNode[]>("/api/skill-tree");
}

export function getQuestions(skillNodeId?: number): Promise<Question[]> {
  const qs = skillNodeId != null ? `?skill_node_id=${skillNodeId}` : "";
  return apiFetch<Question[]>(`/api/questions${qs}`);
}

export function startExam(): Promise<ExamStart> {
  return apiFetch<ExamStart>("/api/exam/start", { method: "POST" });
}

export function getExamState(attemptId: number): Promise<ExamState> {
  return apiFetch<ExamState>(`/api/exam/${attemptId}`);
}

export function answerExamQuestion(
  attemptId: number,
  questionId: number,
  selectedAlternativeId: number | null,
  timeSpentMs: number
): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>(`/api/exam/${attemptId}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: questionId,
      selected_alternative_id: selectedAlternativeId,
      time_spent_ms: timeSpentMs,
    }),
  });
}

export function submitExam(attemptId: number): Promise<ExamResult> {
  return apiFetch<ExamResult>(`/api/exam/${attemptId}/submit`, { method: "POST" });
}
