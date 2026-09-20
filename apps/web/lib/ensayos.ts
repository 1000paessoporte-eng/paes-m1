import type { ExamAttemptSummary } from "@/lib/api";

/**
 * Los ensayos que cuentan como rendidos.
 *
 * Un ensayo entregado sin responder nada, o contestado tan rápido que no dio
 * tiempo de leer, no dice nada de lo que el alumno sabe. El panel ya los
 * excluía, el perfil los filtraba a medias y la pantalla de Modo Ensayo los
 * contaba todos: la misma cuenta daba 11, 12 y 35 en tres pantallas distintas,
 * y el alumno no tiene cómo saber cuál es la buena.
 *
 * La regla vive acá para que exista una sola. La comprobación de `answered`
 * es necesaria además de la bandera: los ensayos entregados antes de que la
 * regla existiera quedaron marcados como representativos aunque estén vacíos.
 */
export function ensayosQueCuentan(
  attempts: ExamAttemptSummary[]
): ExamAttemptSummary[] {
  return attempts.filter(
    (a) => a.status === "submitted" && a.representativo !== false && a.answered > 0
  );
}
