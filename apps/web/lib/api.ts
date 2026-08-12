import type { paths } from "@paes-m1/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type SkillNode =
  paths["/api/skill-tree"]["get"]["responses"][200]["content"]["application/json"][number];

export type Question =
  paths["/api/questions"]["get"]["responses"][200]["content"]["application/json"][number];

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    // El árbol de habilidades cambia con cada intento del alumno; no cachear.
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`API ${path} respondió ${res.status}`);
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
