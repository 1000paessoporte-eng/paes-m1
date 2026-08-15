import type { Metadata } from "next";
import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";
import { ApiError, getAdminMetrics } from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { SerieChart } from "@/components/admin/serie-chart";
import { StatTile } from "@/components/analytics/stat-tile";

export const metadata: Metadata = {
  title: "Panel de administración",
  // No tiene sentido que esta pantalla aparezca en buscadores.
  robots: { index: false, follow: false },
};

const FECHA = new Intl.DateTimeFormat("es-CL", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

function fecha(iso: string | null | undefined): string {
  return iso ? FECHA.format(new Date(iso)) : "nunca";
}

function porcentaje(valor: number | null | undefined): string {
  return valor == null ? "—" : `${Math.round(valor * 100)}%`;
}

export default async function AdminPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;

  let m;
  try {
    m = await getAdminMetrics(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/admin");
    // La API responde 404 a las cuentas sin rol admin: la pantalla hace lo
    // mismo, para no confirmar que el panel existe.
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold">Panel de administración</h1>
      <p className="mt-1 text-sm text-muted">
        Datos de toda la plataforma. Solo lo ven las cuentas con rol admin.
      </p>

      {/* ── Resumen ──────────────────────────────────────────────────── */}
      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Cuentas registradas" value={String(m.usuarios.registros.total)} icon={<IconoPersonas />} />
        <StatTile label="Entraron esta semana" value={String(m.sesiones.activos_7)} icon={<IconoEntrada />} />
        <StatTile label="Visitantes esta semana" value={String(m.visitas.visitantes.ultimos_7)} icon={<IconoOjo />} />
        <StatTile label="Se registran" value={porcentaje(m.embudo.tasa_registro)} icon={<IconoCheck />} />
      </div>


      {/* ── Embudo ───────────────────────────────────────────────────── */}
      <Seccion titulo="Embudo de conversión (30 días)">
        <p className="mb-3 text-xs leading-relaxed text-muted">
          Dónde deja de avanzar la gente. Un total de visitas no dice nada si no
          se sabe en qué paso se pierde.
        </p>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Paso
            label="Visitaron"
            valor={m.embudo.visitantes}
            nota="Navegadores distintos"
          />
          <Paso
            label="Se registraron"
            valor={m.embudo.registrados}
            nota={`${porcentaje(m.embudo.tasa_registro)} de quienes visitaron`}
          />
          <Paso
            label="Rindieron un ensayo"
            valor={m.embudo.con_ensayo}
            nota={`${porcentaje(m.embudo.tasa_activacion)} de quienes se registraron`}
          />
          <Paso
            label="Lo terminaron"
            valor={m.embudo.con_ensayo_terminado}
            nota={`${porcentaje(m.embudo.tasa_finalizacion)} de quienes lo empezaron`}
          />
        </div>
        <p className="mt-3 text-xs leading-relaxed text-muted">
          Además, {m.embudo.visitantes_convertidos}{" "}
          {m.embudo.visitantes_convertidos === 1 ? "navegador estuvo" : "navegadores estuvieron"}{" "}
          sin sesión y después {m.embudo.visitantes_convertidos === 1 ? "apareció" : "aparecieron"}{" "}
          con cuenta iniciada. Es la única conversión que se puede observar
          directamente; no se guarda nada que identifique a la persona.
        </p>
      </Seccion>

      {/* ── Retención ────────────────────────────────────────────────── */}
      <Seccion titulo="Retención">
        <p className="mb-3 text-xs leading-relaxed text-muted">
          Si vuelven. Un registro que entra una vez y no regresa es un registro
          perdido, aunque siga contando en el total.
        </p>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Dato label="Entraron 1 solo día" valor={m.retencion.un_dia} />
          <Dato label="Entraron 2 o 3 días" valor={m.retencion.dos_a_tres} />
          <Dato label="Entraron 4 días o más" valor={m.retencion.cuatro_o_mas} />
          <Dato
            label="Volvieron tras registrarse"
            valor={
              m.retencion.base_volvieron === 0
                ? "—"
                : `${m.retencion.volvieron} de ${m.retencion.base_volvieron}`
            }
          />
        </div>
        {m.retencion.base_volvieron === 0 && (
          <p className="mt-3 text-xs leading-relaxed text-muted">
            Todavía no hay nadie registrado hace más de una semana, así que no se
            puede medir si vuelven. Se mostrará solo cuando el dato exista.
          </p>
        )}
      </Seccion>

      {/* ── Ensayos ──────────────────────────────────────────────────── */}
      <Seccion titulo="Ensayos">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Dato label="Iniciados" valor={m.ensayos.iniciados} />
          <Dato label="Terminados" valor={m.ensayos.terminados} />
          <Dato label="Abandonados" valor={m.ensayos.abandonados} />
          <Dato
            label="Duración mediana"
            valor={
              m.ensayos.duracion_mediana_min == null
                ? "—"
                : `${m.ensayos.duracion_mediana_min} min`
            }
          />
        </div>

        <Tabla
          titulo="Uso por prueba"
          cabeceras={["Prueba", "Iniciados", "Terminados", "Puntaje promedio"]}
          filas={m.ensayos.por_prueba.map((u) => [
            u.subject.toUpperCase(),
            String(u.iniciados),
            String(u.terminados),
            u.puntaje_promedio == null ? "—" : String(u.puntaje_promedio),
          ])}
          vacio="Todavía no se ha rendido ningún ensayo."
        />
      </Seccion>

      {/* ── Banco ────────────────────────────────────────────────────── */}
      <Seccion titulo="Cobertura del banco">
        <p className="mb-3 text-xs leading-relaxed text-muted">
          Si el contenido alcanza para lo que la portada ofrece. Bajo 1,0 la
          prueba no arma ni un ensayo completo, aunque aparezca en el menú.
        </p>
        <Tabla
          titulo="Preguntas por prueba"
          cabeceras={["Prueba", "Banco", "Oficiales", "Ensayos completos", "Sin responder"]}
          filas={m.banco.por_prueba.map((c) => [
            c.subject.toUpperCase(),
            String(c.banco),
            String(c.oficiales),
            <span
              key="e"
              className={c.ensayos_completos < 1 ? "font-semibold text-danger" : ""}
            >
              {c.ensayos_completos.toFixed(2)}×
            </span>,
            String(c.nunca_respondidas),
          ])}
          vacio="Sin datos de banco."
        />
        {m.banco.nodos_flacos.length > 0 && (
          <p className="mt-3 text-xs leading-relaxed text-muted">
            Nodos con menos de 5 preguntas ({m.banco.nodos_flacos.length}):{" "}
            <code className="text-xs">{m.banco.nodos_flacos.join(", ")}</code>. Se
            ven practicables en el árbol y se agotan al primer intento.
          </p>
        )}
      </Seccion>

      {/* ── Usuarios ─────────────────────────────────────────────────── */}
      <Seccion titulo="Usuarios">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Dato label="Nuevos hoy" valor={m.usuarios.registros.hoy} />
          <Dato label="Nuevos 7 días" valor={m.usuarios.registros.ultimos_7} />
          <Dato label="Nuevos 30 días" valor={m.usuarios.registros.ultimos_30} />
          <Dato label="Total" valor={m.usuarios.registros.total} />
        </div>

        <div className="mt-4">
          <SerieChart
            titulo="Registros por día"
            descripcion="Cuentas nuevas en los últimos 30 días"
            datos={m.usuarios.nuevos_por_dia}
          />
        </div>

        <Tabla
          titulo="Últimas cuentas creadas"
          cabeceras={["Cuenta", "Registro", "Última entrada", "Ensayos"]}
          filas={m.usuarios.ultimos.map((u) => [
            <span key="u" className="block">
              <span className="font-medium text-foreground">{u.name}</span>
              <span className="block text-xs text-muted">{u.email}</span>
            </span>,
            fecha(u.created_at),
            fecha(u.last_login_at),
            String(u.ensayos),
          ])}
          vacio="Todavía no hay cuentas registradas."
        />
      </Seccion>

      {/* ── Sesiones ─────────────────────────────────────────────────── */}
      <Seccion titulo="Inicios de sesión">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Dato label="Entradas hoy" valor={m.sesiones.entradas.hoy} />
          <Dato label="Entradas 7 días" valor={m.sesiones.entradas.ultimos_7} />
          <Dato label="Cuentas activas 7 días" valor={m.sesiones.activos_7} />
          <Dato label="Cuentas activas 30 días" valor={m.sesiones.activos_30} />
        </div>

        <p className="mt-3 text-xs text-muted">
          &quot;Entradas&quot; cuenta cada inicio de sesión; &quot;cuentas activas&quot; cuenta
          personas distintas, así que entrar cinco veces no infla el número.
          {Object.keys(m.sesiones.por_metodo).length > 0 && (
            <>
              {" "}
              Por método (30 días):{" "}
              {Object.entries(m.sesiones.por_metodo)
                .map(([metodo, total]) => `${metodo === "google" ? "Google" : "contraseña"} ${total}`)
                .join(", ")}
              .
            </>
          )}
        </p>

        <div className="mt-4">
          <SerieChart
            titulo="Entradas por día"
            descripcion="Inicios de sesión en los últimos 30 días"
            datos={m.sesiones.entradas_por_dia}
          />
        </div>
      </Seccion>

      {/* ── Visitas ──────────────────────────────────────────────────── */}
      <Seccion titulo="Visitas">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Dato label="Vistas hoy" valor={m.visitas.vistas.hoy} />
          <Dato label="Vistas 7 días" valor={m.visitas.vistas.ultimos_7} />
          <Dato label="Visitantes 7 días" valor={m.visitas.visitantes.ultimos_7} />
          <Dato label="Vistas sin sesión 7 días" valor={m.visitas.anonimas_7} />
        </div>

        <p className="mt-3 text-xs text-muted">
          Incluye a quienes todavía no tienen cuenta. Un visitante es un
          navegador distinto, identificado con un número aleatorio: no se guarda
          IP ni user agent.
        </p>

        <div className="mt-4">
          <SerieChart
            titulo="Vistas por día"
            descripcion="Páginas abiertas en los últimos 30 días"
            datos={m.visitas.vistas_por_dia}
          />
        </div>

        <Tabla
          titulo="Páginas más visitadas (7 días)"
          cabeceras={["Ruta", "Vistas", "Visitantes"]}
          filas={m.visitas.top_rutas.map((r) => [
            <code key="r" className="text-xs">{r.path}</code>,
            String(r.visitas),
            String(r.visitantes),
          ])}
          vacio="Sin visitas registradas todavía."
        />
      </Seccion>

      {/* ── Contenido ────────────────────────────────────────────────── */}
      <Seccion titulo="Uso del contenido">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Dato label="Ensayos 7 días" valor={m.contenido.ensayos.ultimos_7} />
          <Dato label="Ensayos totales" valor={m.contenido.ensayos.total} />
          <Dato
            label="Puntaje promedio"
            valor={m.contenido.puntaje_promedio ?? "—"}
          />
          <Dato
            label="Acierto global"
            valor={porcentaje(m.contenido.tasa_acierto_global)}
          />
        </div>

        <p className="mt-3 text-xs text-muted">
          Junta las respuestas de Modo Ensayo y Modo Práctica. Las preguntas
          dejadas en blanco no entran al cálculo de acierto: omitir no es lo
          mismo que equivocarse. Los rankings piden un mínimo de 5 respuestas
          para que una pregunta contestada una vez no aparezca como la peor.
        </p>

        <Tabla
          titulo="Preguntas que más se fallan"
          cabeceras={["Pregunta", "Eje", "Respuestas", "Acierto"]}
          filas={m.contenido.preguntas_mas_falladas.map((p) => [
            <span key="p" className="block max-w-md text-xs">{p.stem}</span>,
            p.axis,
            String(p.respuestas),
            porcentaje(p.tasa_acierto),
          ])}
          vacio="Faltan respuestas para armar el ranking."
        />

        <Tabla
          titulo="Nodos con peor rendimiento"
          cabeceras={["Nodo", "Código", "Respuestas", "Acierto"]}
          filas={m.contenido.nodos_mas_flojos.map((n) => [
            n.name,
            <code key="c" className="text-xs">{n.code}</code>,
            String(n.respuestas),
            porcentaje(n.tasa_acierto),
          ])}
          vacio="Faltan respuestas para armar el ranking."
        />
      </Seccion>
    </div>
  );
}

function Seccion({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <section className="mt-10">
      <h2 className="mb-3 text-sm font-semibold tracking-wide text-muted uppercase">
        {titulo}
      </h2>
      {children}
    </section>
  );
}

function Paso({
  label,
  valor,
  nota,
}: {
  label: string;
  valor: number;
  nota: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight tabular-nums">{valor}</p>
      <p className="mt-1 text-xs text-muted">{nota}</p>
    </div>
  );
}

function Dato({ label, valor }: { label: string; valor: number | string }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight">{valor}</p>
    </div>
  );
}

function Tabla({
  titulo,
  cabeceras,
  filas,
  vacio,
}: {
  titulo: string;
  cabeceras: string[];
  filas: React.ReactNode[][];
  vacio: string;
}) {
  return (
    <div className="mt-4 rounded-xl border border-border bg-surface p-5">
      <h3 className="text-sm font-semibold">{titulo}</h3>
      {filas.length === 0 ? (
        <p className="mt-4 text-xs text-muted">{vacio}</p>
      ) : (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border">
                {cabeceras.map((c) => (
                  <th key={c} className="pb-2 pr-4 text-xs font-medium text-muted">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filas.map((fila, i) => (
                <tr key={i} className="border-b border-border/50 last:border-0">
                  {fila.map((celda, j) => (
                    <td key={j} className="py-2 pr-4 align-top">
                      {celda}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function IconoPersonas() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
    </svg>
  );
}

function IconoEntrada() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" />
    </svg>
  );
}

function IconoOjo() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function IconoCheck() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </svg>
  );
}
