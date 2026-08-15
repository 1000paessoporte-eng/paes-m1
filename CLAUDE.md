# 1000paes — reglas del proyecto

Plataforma chilena de preparación PAES, las cinco pruebas. **Está en
producción y con usuarios reales**: https://1000paes.cl

Trabajan dos socios, cada uno con su propia cuenta de Claude Code. Este archivo
es el contrato común: lo que diga acá vale para ambos, aunque la sesión de al
lado no se haya enterado.

Antes de tocar nada, lee `README.md` (arquitectura y estado de cada feature) y
`HANDOFF.md` (cuentas, infraestructura, puesta en marcha).

## 1. Reglas duras

1. **Cero datos inventados.** Puntajes, tiempos y cantidad de preguntas salen
   del DEMRE (demre.cl). La landing no muestra logos de instituciones ni
   testimonios porque no existen.
2. **Las preguntas nuevas se verifican antes de subirlas**, con
   `uv run python scripts/verificar_banco.py` desde `apps/api`. Comprueba
   estructura y recalcula la aritmética de cada pregunta. Si agregas preguntas,
   agrega también su comprobación en `COMPROBACIONES`.
3. **No se copian preguntas liberadas del DEMRE.** Son material con derechos de
   la Universidad de Chile y este producto va a cobrar. Se replica su temario,
   formato y nivel; no su contenido literal.
4. **Las credenciales nunca entran al repo.** Es público
   (`github.com/1000paessoporte-eng/paes-m1`). Viven en
   `apps/api/.env` (gitignored) y en `HANDOFF-PRIVADO.md`, que se entrega a
   mano entre los socios.

## 2. Cómo se trabaja en paralelo

`main` está protegida: **no se pushea directo**. El ciclo es:

```bash
git switch -c pablo/lo-que-sea     # o mati/lo-que-sea
# ... trabajar ...
```

Y para cerrar, la skill `/ship` hace el resto: corre tests, revisa el diff,
commitea, pushea y abre el PR. `/review` revisa un PR antes de mergear.

Cada PR genera su propia URL de preview en Vercel. **Prueba ahí, no en
producción.** Al mergear a `main`, Vercel despliega a producción solo.

Los previews usan la base `paes_preview`, no la de producción: se puede romper
lo que sea sin tocar los datos de ningún estudiante. El frontend de preview
habla con `milpaes-api-preview.vercel.app`, un alias estable del backend de
pruebas. **Si tu PR cambia la API**, reapunta ese alias a tu despliegue para
probar contra tu propio backend:

```bash
vercel alias set <url-del-deployment-de-preview> milpaes-api-preview.vercel.app
```

Si los dos van a tocar la misma zona del código, díganlo antes: el repo
resuelve conflictos de texto, no de diseño.

## 3. Deploy: las trampas que ya rompieron producción

1. **Si tocaste modelos, aplica la migración a producción ANTES de desplegar la
   API.** Pasó el 2026-08-14: un commit agregó columnas a `users`, la migración
   nunca se aplicó, y al desplegar la API el login empezó a devolver 500 porque
   el modelo pedía columnas que la base no tenía.

   ```bash
   cd apps/api
   DATABASE_URL="<string directo, ver HANDOFF-PRIVADO.md>" uv run alembic upgrade head
   ```

   El string **directo** (sin `-pooler`) es el que sirve para alembic y seed;
   el *pooled* es para el runtime.

2. **El frontend se despliega desde la RAÍZ del repo**, nunca desde `apps/web`.
   Hacerlo desde ahí crea un proyecto Vercel nuevo y roto.

3. **Contenido nuevo del banco no llega solo.** Agregar preguntas a
   `seed_data.py` y desplegar no basta: hay que correr `scripts/seed.py` contra
   producción. Es idempotente, no duplica.

## 4. Verificar antes de pedir merge

```bash
cd apps/api && uv run pytest tests/ -q && uv run ruff check src/ scripts/
cd apps/api && uv run python scripts/verificar_banco.py
cd apps/web && pnpm typecheck && pnpm build
```

**Errores preexistentes conocidos** — no son regresiones, no los persigas:
- `pnpm lint` falla con 1 error (`exam-runner.tsx:78`, acceso a un ref durante el render).
- `uv run mypy src/` reporta 1 error en `exam_focus/router.py:42`.

## 4.1 Trampas que ya costaron tiempo

- **`uvicorn --reload` no siempre recarga** en este entorno. Si un cambio del
  backend no aparece, mata el proceso y relánzalo antes de buscar un bug que no
  existe.
- **`next dev` deja un lock** en `.next/dev-server.json`. Si dice que ya hay un
  servidor corriendo, bórralo y mata `next-server`.
- **Los componentes cliente deben pasar `getClientToken()`** en cada llamada: la
  API autentica con Bearer, no con la cookie. Sin eso devuelve 401.
- **Una columna NOT NULL nueva sobre una tabla con filas va en tres pasos**:
  nullable, `UPDATE` para rellenar, y recién ahí `NOT NULL`. Si además mueves
  datos entre tablas, cópialos ANTES de borrar la columna vieja.
- **Los datos derivados se derivan solos**, con un listener
  `before_insert`/`before_update`. La columna de búsqueda de carreras se llenaba
  en el seed y cualquier fila creada por otro camino quedaba invisible.
- **Buscar texto en español**: sin tildes y por palabras sueltas. Nadie escribe
  "ENFERMERÍA" con tilde en un buscador.

## 5. Desarrollo local

La API y la web se levantan por separado (`pnpm dev` en la raíz choca de puerto
si ya hay una API corriendo):

```bash
cd apps/api && uv run uvicorn paes_api.main:app --reload --port 8000
pnpm --filter @paes-m1/web dev        # desde la raíz
```

Abre **`localhost:3000`**, no `127.0.0.1:3000`: Next bloquea los assets de dev
por origen y la página carga sin JavaScript, con los formularios haciendo
submit nativo y ningún error visible en el navegador.

No corras `pnpm build` mientras el dev server está arriba: pisa `.next` y el
dev empieza a devolver 404 en sus chunks.

## 6. Estructura

- `apps/web` — Next.js (App Router). `/` es la portada pública; `/panel` es el
  panel del alumno, con su propio guard.
- `apps/api` — FastAPI por módulos verticales (`skill_tree`, `exam_focus`,
  `practice`, `analytics`, `users`, `admin`).
- `packages/types` — tipos TS generados desde el OpenAPI de FastAPI.
- El concepto `subject`: M2 no duplica los nodos de M1, los reutiliza. El banco
  de M2 es M1 ∪ M2 (`SUBJECT_INCLUDES` en `exam_focus/service.py`).

## 7. Contacto

Dudas de infraestructura o credenciales: ver `HANDOFF.md` y, para los valores
reales, `HANDOFF-PRIVADO.md` (fuera de git, se pide al otro socio).
