import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import {
  ApiError,
  getAlumnosDelCurso,
  getEjesDelCurso,
  getEnsayosDelCurso,
  getMiColegio,
  type AlumnoDelCurso,
  type EjeDelCurso,
  type EnsayoProgramado,
} from "@/lib/api";
import { TOKEN_COOKIE } from "@/lib/auth";
import { PanelProfesor } from "@/components/colegio/panel-profesor";
import { SinCurso } from "@/components/colegio/sin-curso";
import { VistaAlumno } from "@/components/colegio/vista-alumno";

/** Desde cuántos días sin rendir un alumno cuenta como "hay que ir a buscarlo". */
const DIAS_PERDIDO = 7;

export const metadata = {
  title: "Mi curso",
  description: "El avance del curso y los ensayos programados.",
};

/**
 * El plan Colegios, del lado del profesor y del alumno.
 *
 * Una sola ruta para los dos roles a propósito: el profesor de un curso es
 * también alguien que puede rendir ensayos, y partir la navegación en dos
 * secciones obligaría a explicar cuál es cuál. Lo que cambia es lo que se ve
 * adentro, y eso lo decide el servidor con `es_profesor`.
 */
export default async function ColegioPage() {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (!token) redirect("/login?next=/colegio");

  let colegio;
  try {
    colegio = await getMiColegio(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login?next=/colegio");
    throw err;
  }

  if (!colegio) return <SinCurso />;

  // La agenda la ven los dos roles; la tabla y los ejes, solo el profesor.
  let ensayos: EnsayoProgramado[] = [];
  let alumnos: AlumnoDelCurso[] = [];
  let ejes: EjeDelCurso[] = [];
  try {
    if (colegio.es_profesor) {
      [ensayos, alumnos, ejes] = await Promise.all([
        getEnsayosDelCurso(token),
        getAlumnosDelCurso(token),
        getEjesDelCurso(token),
      ]);
    } else {
      ensayos = await getEnsayosDelCurso(token);
    }
  } catch {
    // Un fallo acá deja la página con el curso y sin los datos, que es mucho
    // mejor que una pantalla de error: el código del curso --lo único que el
    // profesor necesita con urgencia-- ya está cargado.
  }

  // Cuántos no aparecen hace más de una semana: es la pregunta con la que un
  // profesor abre esta página, y contarla a ojo en una lista de treinta no se
  // puede. Los días los cuenta la API: leer el reloj mientras se dibuja un
  // componente da un número distinto en cada render, y React lo prohíbe.
  const perdidos = alumnos.filter(
    (a) => a.dias_sin_rendir == null || a.dias_sin_rendir > DIAS_PERDIDO
  ).length;

  return colegio.es_profesor ? (
    <PanelProfesor
      colegio={colegio}
      alumnos={alumnos}
      ejes={ejes}
      ensayos={ensayos}
      perdidos={perdidos}
    />
  ) : (
    <VistaAlumno colegio={colegio} ensayos={ensayos} />
  );
}
