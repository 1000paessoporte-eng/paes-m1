# PAES M1 — Plataforma de preparación

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

Cuatro features core, cada una como módulo vertical en el backend:

| Feature | Estado | Descripción |
|---|---|---|
| **Árbol de Habilidades** | 🟡 Diseño conceptual, DB lista | Progreso por nodo desbloqueable, gamificado tipo RPG |
| **Modo Examen Focus** | 🟢 Funcional | Examen cronometrado (2h20m) de las 32 preguntas reales |
| **Smart Feedback / Autopsia del Error** | 🟢 Backend+dashboard implementado | Diagnóstico por sub-eje temático + justificación de cada distractor |
| **Analítica / Dashboard** | 🟢 Implementado | Panel de resultados y progreso |

## Arquitectura

Monorepo **Turborepo + pnpm workspaces**.

```
apps/web        Next.js (App Router, TS) — frontend
apps/api        FastAPI (Python, uv)     — backend
packages/ui      Design system compartido
packages/types    Tipos TS generados desde el OpenAPI schema de la API
packages/config   eslint/tsconfig/tailwind compartidos
packages/utils    Utilidades TS compartidas
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
modules/exam_focus/    Modo Examen
modules/feedback/      Smart Feedback / Autopsia del Error
modules/analytics/     Dashboard
modules/users/         Soporte (usuario demo, sin auth real aún)
modules/content/       Soporte (preguntas, alternativas, nodos)
all_models.py          Punto único de import de TODOS los modelos SQLAlchemy
                        (necesario para que resuelvan relaciones declaradas
                        por string; lo usan alembic/env.py, scripts/seed.py y main.py)
```

DB: PostgreSQL. Migraciones con Alembic. Seed real corrido: 15 nodos, 32
preguntas, 128 alternativas.

**Regla de seguridad de contenido**: los endpoints de examen (`start/get/answer/submit`
en `modules/exam_focus`) **nunca** exponen `is_correct` ni
`distractor_justification` mientras el examen está en curso.

### Frontend — `apps/web/`

```
app/(dashboard)/arbol/       UI Árbol de Habilidades
app/(dashboard)/examen/      UI Modo Examen
app/(dashboard)/feedback/    UI Smart Feedback
app/(dashboard)/analitica/   UI Dashboard
components/exam/exam-runner.tsx   SPA del examen: timer server-side,
                                   atajos de teclado, autosave por pregunta,
                                   resume via localStorage + GET /api/exam/{id}
lib/api.ts   Separa API_URL (server-side) de NEXT_PUBLIC_API_URL (browser)
```

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

## Pendiente

- Auth real (hoy hay un usuario demo hardcodeado, `get_or_create_demo_user`)
- UI real del Árbol de Habilidades y lógica de desbloqueo por nodo
- Motor de recomendación adaptativo (ML sobre progreso por nodo)
