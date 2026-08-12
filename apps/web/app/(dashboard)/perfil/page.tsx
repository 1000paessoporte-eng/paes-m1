import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, getAnalyticsSummary, getMe, getSkillTree, listExamAttempts } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { ProfileForm } from "@/components/profile/profile-form";

const DATE_FMT = new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "long", year: "numeric" });

export default async function PerfilPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let user, nodes, attempts, summary;
  try {
    [user, nodes, attempts, summary] = await Promise.all([
      getMe(token ?? ""),
      getSkillTree(token),
      listExamAttempts(token),
      getAnalyticsSummary(token),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login");
    throw err;
  }

  const masteredCount = nodes.filter((n) => n.status === "mastered").length;
  const submittedAttempts = attempts.filter((a) => a.status === "submitted").length;

  return (
    <div>
      <h1 className="text-2xl font-semibold">Mi perfil</h1>
      <p className="mt-1 text-sm text-muted">
        Miembro desde {DATE_FMT.format(new Date(user.created_at))}.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatBox label="Nodos dominados" value={`${masteredCount}/${nodes.length}`} />
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
        <ProfileForm initialName={user.name} email={user.email} />
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
