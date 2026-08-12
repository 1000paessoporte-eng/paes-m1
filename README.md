# milpaes — Plataforma de preparación PAES M1

> La plataforma se llama **milpaes** de cara al usuario. Los paquetes internos
> del monorepo siguen llamándose `@paes-m1/*` y el repo `paes-m1`: renombrarlos
> no aporta nada al producto y rompería imports y rutas.

> Nota para IAs/agentes: este README resume el proyecto para que no necesites
> explorar todo el repo. Lee esto primero; solo entra a los archivos
> mencionados si necesitas el detalle de implementación.

## La idea

Plataforma web para preparar la prueba **PAES M1** (Competencia Matemática 1,
Chile). No es un banco de preguntas plano: el temario (Números, Álgebra,
Geometría, Probabilidad) se presenta como un **Árbol de Habilidades estilo
RPG** — el estudiante empieza en nivel 1 y los nodos superiores (ej. Ecuaciones
Cuadráticas) quedan bloqueados hasta lograr un % mínimo de acierto en los
nodos previos (ej. Álgebra Lineal). El objetivo de largo plazo es que la API
recomiende automáticamente en qué nodo débil enfocarse (motor adaptativo con
pandas/scikit-learn), y que cada error del estudiante tenga una explicación
conceptual precisa de por qué se equivocó (no solo "incorrecto").

Features core, cada una como módulo vertical en el backend:

| Feature | Estado | Descripción |
|---|---|---|
| **Árbol de Habilidades** | 🟡 Diseño conceptual, DB lista | Progreso por nodo desbloqueable, gamificado tipo RPG |
| **Modo Ensayo** | 🟢 Funcional | Ensayo configurable (ejes, cantidad, ritmo) con tiempo proporcional al oficial |
| **Puntaje y revisión** | 🟢 Funcional | Puntaje PAES estimado, desglose por eje/dificultad/nodo y justificación de cada distractor |
| **Historial de progreso** | 🟢 Funcional | Evolución del puntaje, mejor/promedio/último, borrado y respaldo JSON |
| **Analítica / Dashboard** | 🟢 Implementado | Panel de resultados y progreso |

### Modo Ensayo

El estudiante arma el ensayo: elige ejes temáticos, cuántas preguntas y el
ritmo (`oficial` / `exigente` / `relajado`). La duración se calcula desde la
razón oficial de la prueba — 140 min / 65 preguntas ≈ 2 min 9 s por pregunta —
multiplicada por la cantidad elegida y el factor del ritmo.

Como la selección es aleatoria y proporcional por eje, el set de cada intento
se **persiste** en `exam_attempt_questions`: sin eso, un GET posterior (resume
tras refresh, o la revisión meses después) no podría reconstruir el mismo
ensayo. Los intentos anteriores a esa tabla caen al comportamiento antiguo
(todas las preguntas), que es exactamente el examen que rindieron.

El puntaje se estima con la tabla de conversión de `modules/exam_focus/scoring.py`
(escala 100-1000, valores referenciales): la proporción de aciertos se escala a
la base de 60 preguntas puntuadas y se interpola. Siempre se presenta como
"puntaje estimado".

## Arquitectura

Monorepo **Turborepo + pnpm workspaces**.

```
apps/web        Next.js (App Router, TS) — frontend
apps/api        FastAPI (Python, uv)     — backend
packages/types    Tipos TS generados desde el OpenAPI schema de la API
packages/utils    Utilidades TS compartidas (cn)
```

**Por qué FastAPI y no Node**: el backend necesita afinidad con
pandas/scikit-learn para el futuro motor de recomendación de nodos débiles.
Los tipos compartidos frontend↔backend se generan desde el schema OpenAPI de
FastAPI (`openapi-typescript`) hacia `packages/types` — la API es la fuente de
verdad de los tipos, no al revés.

### Backend — `apps/api/src/paes_api/`

Organizado por módulos verticales, uno por feature core, más dominios de
soporte:

```
modules/skill_tree/    Árbol de Habilidades
modules/exam_focus/    Modo Ensayo (config, runner, puntaje, revisión, historial)
  └ scoring.py         Tabla de conversión a puntaje PAES y ritmo oficial
modules/analytics/     Dashboard
modules/users/         Soporte (auth real: registro, login, perfil)
modules/content/       Soporte (preguntas, alternativas, nodos)
all_models.py          Punto único de import de TODOS los modelos SQLAlchemy
                        (necesario para que resuelvan relaciones declaradas
                        por string; lo usan alembic/env.py, scripts/seed.py y main.py)
```

DB: PostgreSQL. Migraciones con Alembic. Seed real corrido: 15 nodos, 36
preguntas.

**Regla de seguridad de contenido**: los endpoints de ensayo (`start/get/answer/submit`
en `modules/exam_focus`) **nunca** exponen `is_correct` ni
`distractor_justification` mientras el ensayo está en curso. Esos datos solo
aparecen en `/review`, que exige el intento ya finalizado.

### Frontend — `apps/web/`

```
app/(dashboard)/arbol/       UI Árbol de Habilidades
app/(dashboard)/examen/      UI Modo Ensayo
app/(dashboard)/historial/   UI Mi progreso (historial + gráfico)
app/(dashboard)/analitica/   UI Dashboard
components/exam/exam-config.tsx   Pantalla de configuración del ensayo
components/exam/exam-runner.tsx   SPA del ensayo: timer contra la hora límite,
                                   marcar preguntas, navegador, atajos de
                                   teclado, autosave por pregunta, resume via
                                   localStorage + GET /api/exam/{id}
components/exam/exam-results.tsx  Puntaje, desgloses y revisión con explicaciones
components/history/               Historial y gráfico SVG de evolución
components/texto-rico.tsx         Renderiza LaTeX ($...$) con KaTeX y tablas markdown
lib/api.ts   Separa API_URL (server-side) de NEXT_PUBLIC_API_URL (browser)
```

El tema es claro (fondo blanco) y se define con variables CSS en
`app/globals.css`; los componentes usan los tokens (`bg-surface`, `text-muted`,
`border-border`…), así que cambiar la paleta es editar solo `:root`.

## Desarrollo

```bash
pnpm install
pnpm dev          # levanta web + api vía turbo
```

El backend también se puede correr solo con `uv` dentro de `apps/api`.
Variables de entorno reales en `apps/api/.env` (gitignored, ver `.env.example`).

### Exponer fuera de la LAN

Se usan dos túneles `cloudflared` (uno para :3000 web, otro para :8000 api).
El dominio del túnel web debe agregarse a `next.config.ts` → `allowedDevOrigins`
y a `cors_origins` en la config de la API.

### Inicio de sesión con Google

Flujo de ID token de Google Identity Services: el navegador obtiene un JWT
firmado por Google y lo manda a `POST /api/auth/google`, que verifica firma,
expiración y **audiencia** (que el token sea para nuestro client ID) antes de
crear la sesión. Sin esa última comprobación, un token válido de cualquier otra
app serviría para entrar.

Se configura con el mismo client ID en dos variables: `GOOGLE_CLIENT_ID`
(apps/api/.env) y `NEXT_PUBLIC_GOOGLE_CLIENT_ID` (apps/web/.env.local). Si
están vacías, el botón no se muestra y `/api/auth/google` responde 401: la web
sigue funcionando con correo y contraseña. Las cuentas de Google se guardan con
`google_sub` y sin contraseña (`hashed_password` NULL); si el correo ya existía
registrado con contraseña, se **enlaza** en vez de duplicar, conservando el
historial.

**Restricción de Google**: los orígenes autorizados no admiten IPs privadas.
`http://192.168.1.15:3000` no sirve; solo `http://localhost:3000` o un dominio
con HTTPS. `NEXT_PUBLIC_*` se incrusta en tiempo de build, así que **hay que
reconstruir** (`pnpm build`) después de configurar el client ID.

### Servir en la LAN

`apps/web/next.config.ts` reenvía `/api/*` al backend, y `NEXT_PUBLIC_API_URL`
va vacío en `.env.local` para que el navegador use rutas relativas. Así basta
con abrir el puerto 3000: no hay CORS de por medio ni la IP del host queda
quemada en el bundle del cliente.

## Pendiente

- UI real del Árbol de Habilidades y lógica de desbloqueo por nodo
- Motor de recomendación adaptativo (ML sobre progreso por nodo)
- Ampliar el banco de preguntas (hoy 36) y agregar enunciados con LaTeX
