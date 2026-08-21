import type { components, paths } from "@paes-m1/types";

// En el servidor (Server Components) usamos la URL interna, rápida y sin
// depender de red externa. En el navegador (Client Components) usamos la
// URL pública, que puede ser un túnel distinto al del propio host.
const API_URL =
  typeof window === "undefined"
    ? (process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    : (process.env.NEXT_PUBLIC_API_URL ?? "");

export type SkillNode =
  paths["/api/skill-tree"]["get"]["responses"][200]["content"]["application/json"][number];

export type Question =
  paths["/api/questions"]["get"]["responses"][200]["content"]["application/json"][number];

export type ExamStart =
  paths["/api/exam/start"]["post"]["responses"][200]["content"]["application/json"];

export type ExamOptions =
  paths["/api/exam/options"]["get"]["responses"][200]["content"]["application/json"];

export type AxisOption = ExamOptions["axes"][number];

export type ExamConfig = components["schemas"]["ExamConfigIn"];

export type Subject = components["schemas"]["Subject"];

export type Pace = components["schemas"]["Pace"];

export type BreakdownItem = components["schemas"]["BreakdownItemOut"];

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

export type Diagnostico =
  paths["/api/analytics/diagnostico"]["get"]["responses"][200]["content"]["application/json"];

/**
 * Qué hace mal el alumno y por qué.
 *
 * Sin cachear: cambia con cada respuesta que da, y es la pantalla que mira
 * justo después de rendir.
 */
export function getDiagnostico(token?: string): Promise<Diagnostico> {
  return apiFetch<Diagnostico>("/api/analytics/diagnostico", token);
}

export type AdminMetrics =
  paths["/api/admin/metrics"]["get"]["responses"][200]["content"]["application/json"];

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
    // Por defecto no se cachea: el árbol de habilidades y el examen cambian
    // por intento. Quien tenga un dato que sí sirva cacheado (las cifras
    // públicas del banco) lo pide explícitamente en su `init`.
    cache: init?.cache ?? "no-store",
  });
  if (!res.ok) {
    const detail = await res
      .json()
      .then((d) => (typeof d?.detail === "string" ? d.detail : undefined))
      .catch(() => undefined);
    throw new ApiError(res.status, path, detail);
  }
  // 204 (por ejemplo, borrar un intento) no trae cuerpo que parsear.
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export type RecommendedNode =
  paths["/api/skill-tree/recommended"]["get"]["responses"][200]["content"]["application/json"];

export type PracticeStart =
  paths["/api/practice/{code}/questions"]["get"]["responses"][200]["content"]["application/json"];

export type PracticeQuestion = PracticeStart["questions"][number];

export type PracticeAnswerResult =
  paths["/api/practice/{code}/answer"]["post"]["responses"][200]["content"]["application/json"];

export type ContentStats =
  paths["/api/questions/stats"]["get"]["responses"][200]["content"]["application/json"];

/**
 * Cifras del banco para la portada.
 *
 * Se cachean una hora: el banco no crece cada minuto y la portada es la página
 * más visitada del sitio. Si la API no responde, quien llama recibe el error y
 * decide — la portada prefiere no mostrar el dato antes que mostrar uno viejo
 * escrito a mano.
 */
export function getContentStats(): Promise<ContentStats> {
  return apiFetch<ContentStats>("/api/questions/stats", undefined, {
    cache: "force-cache",
    next: { revalidate: 3600 },
  });
}

export type LeccionIndice =
  paths["/api/skill-tree/lecciones"]["get"]["responses"][200]["content"]["application/json"][number];

/**
 * Los temas que ya tienen lección escrita.
 *
 * Público y cacheado un día: lo piden el índice de /aprender, el sitemap y el
 * prerenderizado de cada lección, y el contenido cambia cuando alguien escribe
 * una lección nueva, no cada minuto.
 */
export function getLecciones(): Promise<LeccionIndice[]> {
  return apiFetch<LeccionIndice[]>("/api/skill-tree/lecciones", undefined, {
    cache: "force-cache",
    next: { revalidate: 86400 },
  });
}

export type Lesson =
  paths["/api/skill-tree/{code}/leccion"]["get"]["responses"][200]["content"]["application/json"];

export function getSkillTree(
  token?: string,
  subject: string = "m1"
): Promise<SkillNode[]> {
  return apiFetch<SkillNode[]>(`/api/skill-tree?subject=${subject}`, token);
}

export type Carrera =
  paths["/api/meta/carreras"]["get"]["responses"][200]["content"]["application/json"][number];

export type Meta = paths["/api/meta"]["get"]["responses"][200]["content"]["application/json"];
export type Postulacion = Meta["postulaciones"][number];

export function buscarCarreras(q: string, token?: string): Promise<Carrera[]> {
  return apiFetch<Carrera[]>(`/api/meta/carreras?q=${encodeURIComponent(q)}`, token);
}

export function getMeta(token?: string): Promise<Meta> {
  return apiFetch<Meta>("/api/meta", token);
}

const JSON_HEADERS = { "Content-Type": "application/json" };

export function agregarPostulacion(carrera_id: number, token?: string): Promise<Meta> {
  return apiFetch<Meta>("/api/meta/postulaciones", token, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ carrera_id }),
  });
}

export function quitarPostulacion(carrera_id: number, token?: string): Promise<Meta> {
  return apiFetch<Meta>(`/api/meta/postulaciones/${carrera_id}`, token, {
    method: "DELETE",
  });
}

export function reordenarPostulaciones(
  carrera_ids: number[],
  token?: string
): Promise<Meta> {
  return apiFetch<Meta>("/api/meta/orden", token, {
    method: "PUT",
    headers: JSON_HEADERS,
    body: JSON.stringify({ carrera_ids }),
  });
}

export function guardarNotas(
  payload: { puntaje_nem: number | null; puntaje_ranking: number | null },
  token?: string
): Promise<Meta> {
  return apiFetch<Meta>("/api/meta/notas", token, {
    method: "PUT",
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  });
}

export type MiPlan = paths["/api/plan"]["get"]["responses"][200]["content"]["application/json"];

export function getMiPlan(token?: string): Promise<MiPlan> {
  return apiFetch<MiPlan>("/api/plan", token);
}

export type Productos =
  paths["/api/plan/productos"]["get"]["responses"][200]["content"]["application/json"];

export function getProductos(): Promise<Productos> {
  return apiFetch<Productos>("/api/plan/productos");
}

/** Devuelve la URL de Flow a la que hay que enviar al usuario. */
export function iniciarPago(
  producto: string,
  token?: string
): Promise<{ url: string; orden: string }> {
  return apiFetch("/api/plan/pagar", token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ producto }),
  });
}

export function canjearCodigo(codigo: string, token?: string): Promise<MiPlan> {
  return apiFetch<MiPlan>("/api/plan/canjear", token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo }),
  });
}

export type Onboarding =
  paths["/api/auth/onboarding"]["get"]["responses"][200]["content"]["application/json"];

export function getOnboarding(token?: string): Promise<Onboarding> {
  return apiFetch<Onboarding>("/api/auth/onboarding", token);
}

/**
 * Guarda lo que el estudiante haya querido contar.
 *
 * Todos los campos son opcionales porque el guardado es parcial de verdad: el
 * servidor solo pisa los que recibe (`users/service.py`), y marca el
 * cuestionario como respondido aunque no venga ninguno. Eso permite que el
 * modal de bienvenida pregunte una sola cosa y que /perfil complete el resto
 * después, sin que ninguno de los dos tenga que mandar campos vacíos que
 * pisarían lo ya guardado.
 */
export function guardarOnboarding(
  payload: {
    pruebas_objetivo?: string[];
    curso?: string | null;
    primera_vez?: boolean | null;
    puntaje_anterior?: number | null;
    horas_semana?: number | null;
  },
  token?: string
): Promise<Onboarding> {
  return apiFetch<Onboarding>("/api/auth/onboarding", token, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** Un nodo con el progreso del estudiante. */
export function getSkillNode(code: string, token?: string): Promise<SkillNode> {
  return apiFetch<SkillNode>(`/api/skill-tree/${code}`, token);
}

/** La teoría de un nodo. Lanza ApiError 404 si el tema aún no tiene lección. */
/**
 * La teoría de un tema. Pública, y por eso cacheada.
 *
 * Sin `force-cache` la página de la lección no se puede prerenderizar: una
 * ruta que hace un fetch sin cachear pasa a renderizarse en cada visita, que
 * es justo lo contrario de lo que necesitan 17 páginas idénticas para todo el
 * mundo y pensadas para que Google las visite.
 *
 * No lleva token a propósito: el contenido es el mismo con sesión o sin ella,
 * y una petición cacheada que arrastre una cabecera de autorización es la
 * forma de servirle a alguien la respuesta de otro.
 */
export function getLesson(code: string): Promise<Lesson> {
  return apiFetch<Lesson>(`/api/skill-tree/${code}/leccion`, undefined, {
    cache: "force-cache",
    next: { revalidate: 86400 },
  });
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

export function getExamOptions(
  token?: string,
  subject: Subject = "m1"
): Promise<ExamOptions> {
  return apiFetch<ExamOptions>(`/api/exam/options?subject=${subject}`, token);
}

export type Repaso =
  paths["/api/exam/repaso"]["get"]["responses"][200]["content"]["application/json"];

export function getRepaso(token?: string, subject: Subject = "m1"): Promise<Repaso> {
  return apiFetch<Repaso>(`/api/exam/repaso?subject=${subject}`, token);
}

export function startExam(config: ExamConfig, token?: string): Promise<ExamStart> {
  return apiFetch<ExamStart>("/api/exam/start", token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
}

export function getExamResult(attemptId: number, token?: string): Promise<ExamResult> {
  return apiFetch<ExamResult>(`/api/exam/${attemptId}/result`, token);
}

export function deleteExamAttempt(attemptId: number, token?: string): Promise<void> {
  return apiFetch<void>(`/api/exam/${attemptId}`, token, { method: "DELETE" });
}

export function getExamState(attemptId: number, token?: string): Promise<ExamState> {
  return apiFetch<ExamState>(`/api/exam/${attemptId}`, token);
}

/**
 * Cuánto se espera por un autoguardado antes de darlo por perdido.
 *
 * Sin límite, una conexión que acepta la conexión pero no responde --un portal
 * cautivo de wifi, una red que se cayó a medias-- deja la promesa colgada:
 * medido, tardó 30 segundos en fallar. Durante el ensayo eso solo retrasa el
 * reintento, pero al enviar el alumno se queda mirando "Enviando..." sin saber
 * si su ensayo se fue. Ocho segundos es de sobra para un POST de cuatro
 * campos, y fallar rápido es lo que permite reintentar.
 */
const TIMEOUT_AUTOGUARDADO_MS = 8000;

export function answerExamQuestion(
  attemptId: number,
  questionId: number,
  selectedAlternativeId: number | null,
  timeSpentMs: number,
  flagged: boolean,
  token?: string
): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>(`/api/exam/${attemptId}/answer`, token, {
    method: "POST",
    signal: AbortSignal.timeout(TIMEOUT_AUTOGUARDADO_MS),
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: questionId,
      selected_alternative_id: selectedAlternativeId,
      time_spent_ms: timeSpentMs,
      flagged,
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

/**
 * Cancela la renovación de la suscripción.
 *
 * No corta el acceso: lo ya pagado se respeta hasta su fecha de término.
 */
export function cancelarSuscripcion(token?: string): Promise<MiPlan> {
  return apiFetch<MiPlan>("/api/plan/cancelar", token, { method: "POST" });
}

/**
 * Borra la cuenta y todo lo que cuelga de ella. Irreversible.
 *
 * La contraseña va aunque haya sesión: borrar no puede depender solo de que
 * alguien dejó la sesión abierta. Las cuentas de Google no tienen, así que
 * ahí se manda sin ella.
 */
export function eliminarCuenta(password: string | null, token?: string): Promise<void> {
  return apiFetch<void>("/api/auth/me", token, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
}

export function getAdminMetrics(token?: string): Promise<AdminMetrics> {
  return apiFetch<AdminMetrics>("/api/admin/metrics", token);
}

/**
 * Registra una visita. Silencia cualquier error a propósito: medir nunca debe
 * romper la navegación de quien está usando el sitio.
 */
export type Utm = {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_content?: string;
};

export function trackPageView(
  path: string,
  visitorId: string,
  token?: string,
  referrer?: string,
  utm?: Utm
): void {
  apiFetch<void>("/api/metrics/pageview", token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, visitor_id: visitorId, referrer, ...utm }),
  }).catch(() => {});
}

export function registerUser(email: string, password: string, name: string): Promise<TokenOut> {
  return apiFetch<TokenOut>("/api/auth/register", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
}

export type AuthConfig =
  paths["/api/auth/config"]["get"]["responses"][200]["content"]["application/json"];

export function getAuthConfig(): Promise<AuthConfig> {
  return apiFetch<AuthConfig>("/api/auth/config");
}

/** `credential` es el ID token que entrega Google Identity Services. */
export function loginWithGoogle(credential: string): Promise<TokenOut> {
  return apiFetch<TokenOut>("/api/auth/google", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential }),
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

export function forgotPassword(email: string): Promise<void> {
  return apiFetch<void>("/api/auth/forgot-password", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
}

export function resetPassword(token: string, newPassword: string): Promise<void> {
  return apiFetch<void>("/api/auth/reset-password", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

// ── Demo pública, sin cuenta ────────────────────────────────────────────

export type DemoQuestion =
  paths["/api/demo/questions"]["get"]["responses"][200]["content"]["application/json"][number];

export type DemoGradeResult =
  paths["/api/demo/grade"]["post"]["responses"][200]["content"]["application/json"];

export function getDemoQuestions(subject: Subject = "m1"): Promise<DemoQuestion[]> {
  return apiFetch<DemoQuestion[]>(`/api/demo/questions?subject=${subject}`);
}

export function gradeDemo(
  answers: { question_id: number; selected_alternative_id: number | null }[]
): Promise<DemoGradeResult> {
  return apiFetch<DemoGradeResult>("/api/demo/grade", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
}

/**
 * Busca carreras sin sesión. La usa el buscador público de /carreras.
 *
 * Sin cachear: cada búsqueda es distinta y el resultado se pide desde el
 * navegador mientras la persona escribe.
 */
export function buscarCarrerasPublico(q: string): Promise<CarreraCatalogo[]> {
  return apiFetch<CarreraCatalogo[]>(`/api/carreras/buscar?q=${encodeURIComponent(q)}`);
}

export type Universidad =
  paths["/api/carreras/universidades"]["get"]["responses"][200]["content"]["application/json"][number];

/**
 * Las universidades del catálogo, con cuántas carreras tiene cada una.
 *
 * Son 47 filas: se puede pedir desde la portada sin el costo de bajarse las
 * 1.855 del catálogo completo. Mismo día de caché que el catálogo, porque el
 * dato cambia una vez por proceso de admisión.
 */
export function getUniversidades(): Promise<Universidad[]> {
  return apiFetch<Universidad[]>("/api/carreras/universidades", undefined, {
    cache: "force-cache",
    next: { revalidate: 86400 },
  });
}

export type LeadSource = components["schemas"]["LeadSource"];

/**
 * Deja el correo de alguien que todavía no tiene cuenta.
 *
 * Nunca lanza hacia arriba por un correo repetido: la API responde igual haya
 * o no una fila nueva, así que quien lo deja dos veces no ve un error por algo
 * que para él es la misma acción.
 */
export function dejarCorreo(email: string, source: LeadSource): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>("/api/leads", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, source }),
  });
}

export type UsoPublico =
  paths["/api/metrics/uso"]["get"]["responses"][200]["content"]["application/json"];

/**
 * Cuánto se usa la plataforma. La portada lo muestra como prueba social.
 *
 * Se cachea diez minutos: es un dato que cambia de a poco y la portada es la
 * página más visitada, así que no tiene sentido contar la base en cada visita.
 */
export function getUsoPublico(): Promise<UsoPublico> {
  return apiFetch<UsoPublico>("/api/metrics/uso", undefined, {
    cache: "force-cache",
    next: { revalidate: 600 },
  });
}

export type CarreraPublica =
  paths["/api/carreras/{codigo}"]["get"]["responses"][200]["content"]["application/json"];

export type CarreraCatalogo =
  paths["/api/carreras/catalogo"]["get"]["responses"][200]["content"]["application/json"][number];

/**
 * El catálogo entero de carreras.
 *
 * Lo piden el sitemap y el índice navegable, o sea las dos páginas que existen
 * para que Google encuentre las 1.855 fichas. Se cachea un día: las
 * ponderaciones las publica el DEMRE una vez por proceso de admisión, no
 * cambian dentro de la jornada.
 */
export function getCarrerasCatalogo(): Promise<CarreraCatalogo[]> {
  return apiFetch<CarreraCatalogo[]>("/api/carreras/catalogo", undefined, {
    cache: "force-cache",
    next: { revalidate: 86400 },
  });
}

/**
 * La ficha pública de una carrera por su código del DEMRE.
 *
 * Lanza `ApiError` con 404 cuando el código no existe, que es lo que convierte
 * la página en un notFound() en vez de un error 500 — la URL la puede escribir
 * cualquiera.
 */
export function getCarrera(codigo: string): Promise<CarreraPublica> {
  return apiFetch<CarreraPublica>(`/api/carreras/${encodeURIComponent(codigo)}`, undefined, {
    cache: "force-cache",
    next: { revalidate: 86400 },
  });
}
