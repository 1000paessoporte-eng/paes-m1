# PAES M1 — Plataforma de preparación

Monorepo (Turborepo + pnpm) para la plataforma de preparación de la prueba
PAES M1 (Competencia Matemática, Chile).

## Estructura

- `apps/web` — Next.js (App Router) + Tailwind + Framer Motion
- `apps/api` — FastAPI (Python, gestionado con `uv`)
- `packages/ui` — Design system compartido
- `packages/types` — Tipos TS generados desde el schema OpenAPI de la API
- `packages/config` — Config compartida (eslint, tsconfig, tailwind)
- `packages/utils` — Utilidades TS compartidas

## Desarrollo

```bash
pnpm install
pnpm dev
```

El backend se maneja por separado con `uv` dentro de `apps/api` (ver su README).
