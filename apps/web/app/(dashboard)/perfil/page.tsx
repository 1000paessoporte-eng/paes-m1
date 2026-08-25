import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import {
  ApiError,
  getAnalyticsSummary,
  getMe,
  getMiPlan,
  getProductos,
  getOnboarding,
  getSkillTree,
  listExamAttempts,
} from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { ProfileForm } from "@/components/profile/profile-form";
import { ZonaPeligro } from "@/components/profile/zona-peligro";
import { MiPlanPanel } from "@/components/plan/mi-plan";
import { MisDatos } from "@/components/onboarding/mis-datos";

export const metadata = {
  title: "Mi perfil",
  description: "Tus datos de cuenta y tus estadísticas.",
};


/** Las cinco pruebas, para el alumno que no respondió el cuestionario. */
const TODAS_LAS_PRUEBAS = ["lectora", "m1", "m2", "ciencias", "historia"];

const DATE_FMT = new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "long", year: "numeric" });

export default async function PerfilPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let user, attempts, summary, plan, onboarding;
  try {
    [user, attempts, summary, plan, onboarding] = await Promise.all([
      getMe(token ?? ""),
      listExamAttempts(token),
      getAnalyticsSummary(token),
      getMiPlan(token),
      getOnboarding(token),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/perfil");
    throw err;
  }

  // Los productos van aparte del Promise.all: si el catálogo falla, la página
  // debe seguir cargando sin el bloque de compra en vez de caerse entera.
  let productos;
  try {
    productos = await getProductos();
  } catch {
    productos = undefined;
  }

  // El árbol de TODAS las pruebas que el alumno va a rendir, no solo de M1.
  //
  // `getSkillTree(token)` trae M1 por defecto, así que el perfil decía
  // "Nodos dominados 1/16" con un denominador de una prueba, rotulado como si
  // fuera el total. Hay 52 nodos repartidos en las cinco. Y sumar las cinco a
  // secas tampoco sirve: quien rinde Lectora, M1 y Ciencias vería en el
  // denominador los temas de M2 e Historia que no va a estudiar nunca.
  //
  // Las pruebas salen de lo que el propio alumno declaró en el cuestionario,
  // que es lo que esta misma página le muestra más abajo en "Pruebas que voy
  // a rendir". Si no respondió, se cuentan las cinco.
  const pruebasObjetivo =
    onboarding?.pruebas_objetivo && onboarding.pruebas_objetivo.length > 0
      ? onboarding.pruebas_objetivo
      : TODAS_LAS_PRUEBAS;
  const arboles = await Promise.all(
    pruebasObjetivo.map((prueba) => getSkillTree(token, prueba).catch(() => []))
  );
  const nodosObjetivo = arboles.flat();
  const masteredCount = nodosObjetivo.filter((n) => n.status === "mastered").length;

  // Solo los que cuentan. Un ensayo entregado sin responder ninguna pregunta
  // no es un simulacro completado, y el historial ya los excluye: acá seguían
  // sumando. Ver `_es_representativo` en exam_focus/service.py.
  const submittedAttempts = attempts.filter(
    (a) => a.status === "submitted" && a.representativo !== false
  ).length;

  return (
    <div>
      <h1 className="text-2xl font-semibold">Mi perfil</h1>
      <p className="mt-1 text-sm text-muted">
        Miembro desde {DATE_FMT.format(new Date(user.created_at))}.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatBox
          label="Nodos dominados"
          value={`${masteredCount}/${nodosObjetivo.length}`}
        />
        <StatBox label="Simulacros completados" value={String(submittedAttempts)} />
        <StatBox label="Racha actual" value={`${summary.current_streak_days} d`} />
        <StatBox
          label="Precisión global"
          value={
            summary.overall_accuracy != null
              ? `${Math.round(summary.overall_accuracy * 100)}%`
              : "—"
          }
        />
      </div>

      <div className="mt-8 max-w-lg">
        <MisDatos inicial={onboarding} />
      </div>

      <div className="mt-5 max-w-lg">
        <MiPlanPanel inicial={plan} productos={productos} />
      </div>

      <div className="mt-5 max-w-lg">
        <ProfileForm
          initialName={user.name}
          email={user.email}
          initialRecordatorios={user.recordatorios_email ?? true}
        />

        {/* Cancelar y borrar viven acá, al final y con el borde de aviso: son
            las dos acciones que nadie debería tocar por accidente, y hasta hoy
            solo existían como "escríbenos a hola@". */}
        <ZonaPeligro
          // Solo Pro: el plan Colegios lo paga el establecimiento y esta
          // cuenta no tiene ninguna suscripción que cancelar. Ofrecérselo
          // llevaba a un 409 "No tienes una suscripción activa".
          tienePlanActivo={plan.plan === "pro"}
          // has_password es el dato exacto: una cuenta de Google no tiene
          // contraseña que confirmar.
          usaGoogle={!user.has_password}
        />
      </div>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-1 text-xl font-semibold text-foreground">{value}</p>
    </div>
  );
}
