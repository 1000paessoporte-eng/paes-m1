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

export type ExamAttemptSummary =
  paths["/api/exam"]["get"]["responses"][200]["content"]["application/json"][number];

export type ExamReview =
  paths["/api/exam/{attempt_id}/review"]["get"]["responses"][200]["content"]["application/json"];

export type ReviewQuestion = ExamReview["questions"][number];
export type NodeDiagnosis = ExamReview["node_diagnosis"][number];

export type AnalyticsSummary =
  paths["/api/analytics/summary"]["get"]["responses"][200]["content"]["application/json"];

export type AuthUserOut =
  paths["/api/auth/me"]["get"]["responses"][200]["content"]["application/json"];

export type TokenOut =
  paths["/api/auth/login"]["post"]["responses"][200]["content"]["application/json"];

export class ApiError extends Error {
  constructor(
    public status: number,
    path: string,
    public detail?: string
  ) {
    super(`API ${path} respondió ${status}`);
  }
}

async function apiFetch<T>(path: string, token?: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    // El árbol de habilidades y el examen cambian por intento; no cachear.
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res
      .json()
      .then((d) => (typeof d?.detail === "string" ? d.detail : undefined))
      .catch(() => undefined);
    throw new ApiError(res.status, path, detail);
  }
  return res.json() as Promise<T>;
}

export type RecommendedNode =
  paths["/api/skill-tree/recommended"]["get"]["responses"][200]["content"]["application/json"];

export type PracticeStart =
  paths["/api/practice/{code}/questions"]["get"]["responses"][200]["content"]["application/json"];

export type PracticeQuestion = PracticeStart["questions"][number];

export type PracticeAnswerResult =
  paths["/api/practice/{code}/answer"]["post"]["responses"][200]["content"]["application/json"];

export function getSkillTree(token?: string): Promise<SkillNode[]> {
  return apiFetch<SkillNode[]>("/api/skill-tree", token);
}

export function getRecommendedNode(token?: string): Promise<RecommendedNode> {
  return apiFetch<RecommendedNode>("/api/skill-tree/recommended", token);
}

export function getPracticeQuestions(code: string, token?: string): Promise<PracticeStart> {
  return apiFetch<PracticeStart>(`/api/practice/${code}/questions`, token);
}

export function answerPractice(
  code: string,
  questionId: number,
  selectedAlternativeId: number,
  token?: string
): Promise<PracticeAnswerResult> {
  return apiFetch<PracticeAnswerResult>(`/api/practice/${code}/answer`, token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: questionId,
      selected_alternative_id: selectedAlternativeId,
    }),
  });
}

export function getQuestions(skillNodeId?: number, token?: string): Promise<Question[]> {
  const qs = skillNodeId != null ? `?skill_node_id=${skillNodeId}` : "";
  return apiFetch<Question[]>(`/api/questions${qs}`, token);
}

export function startExam(token?: string): Promise<ExamStart> {
  return apiFetch<ExamStart>("/api/exam/start", token, { method: "POST" });
}

export function getExamState(attemptId: number, token?: string): Promise<ExamState> {
  return apiFetch<ExamState>(`/api/exam/${attemptId}`, token);
}

export function answerExamQuestion(
  attemptId: number,
  questionId: number,
  selectedAlternativeId: number | null,
  timeSpentMs: number,
  token?: string
): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>(`/api/exam/${attemptId}/answer`, token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: questionId,
      selected_alternative_id: selectedAlternativeId,
      time_spent_ms: timeSpentMs,
    }),
  });
}

export function submitExam(attemptId: number, token?: string): Promise<ExamResult> {
  return apiFetch<ExamResult>(`/api/exam/${attemptId}/submit`, token, { method: "POST" });
}

export function listExamAttempts(token?: string): Promise<ExamAttemptSummary[]> {
  return apiFetch<ExamAttemptSummary[]>("/api/exam", token);
}

export function getExamReview(attemptId: number, token?: string): Promise<ExamReview> {
  return apiFetch<ExamReview>(`/api/exam/${attemptId}/review`, token);
}

export function getAnalyticsSummary(token?: string): Promise<AnalyticsSummary> {
  return apiFetch<AnalyticsSummary>("/api/analytics/summary", token);
}

export function registerUser(email: string, password: string, name: string): Promise<TokenOut> {
  return apiFetch<TokenOut>("/api/auth/register", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
}

export function loginUser(email: string, password: string): Promise<TokenOut> {
  return apiFetch<TokenOut>("/api/auth/login", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function getMe(token: string): Promise<AuthUserOut> {
  return apiFetch<AuthUserOut>("/api/auth/me", token);
}

export type UpdateMeIn =
  paths["/api/auth/me"]["patch"]["requestBody"]["content"]["application/json"];

export function updateMe(payload: UpdateMeIn, token?: string): Promise<AuthUserOut> {
  return apiFetch<AuthUserOut>("/api/auth/me", token, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
