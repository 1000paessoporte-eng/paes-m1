# 1000paes — Plataforma de preparación PAES

**Producción: https://1000paes.cl**

> La plataforma se llama **1000paes** de cara al usuario. Los paquetes internos
> del monorepo siguen llamándose `@paes-m1/*`, el repo `paes-m1` y los proyectos
> de Vercel `milpaes-web` / `milpaes-api`: renombrarlos no aporta nada al
> producto y rompería imports, rutas y el deploy.

> **Nota para IAs/agentes**: este README resume el proyecto para que no
> necesites explorar todo el repo. Léelo primero; entra a los archivos
> mencionados solo si necesitas el detalle de implementación. Presta especial
> atención a la sección **Deploy** — hay dos formas fáciles de romper
> producción ahí.
>
> **¿Tomas el proyecto ahora?** Lee **[`HANDOFF.md`](HANDOFF.md)**: cuentas,
> infraestructura, project IDs de Vercel, puesta en marcha en una máquina nueva,
> rutina de trabajo y pendientes por impacto. Está todo ahí salvo los secretos.
>
> **Los secretos** (contraseña de Neon y `SECRET_KEY`) no están en este repo y
> no deben estarlo: el repo es **público**, y un `postgresql://…` con contraseña
> lo encuentran los bots que rastrean GitHub en minutos. Se piden por canal
> privado y viven solo en `apps/api/.env` local, que está gitignored.

---

## 1. Qué es

Plataforma web chilena para preparar la **PAES** (Prueba de Acceso a la
Educación Superior). Cubre **las cinco pruebas**: Competencia Lectora,
Competencia Matemática M1 y M2, Historia y Ciencias Sociales, y Ciencias. Cada
una con su tabla de puntaje oficial DEMRE, su duración y sus ejes propios.

El banco no está parejo entre pruebas: matemática tiene 282 preguntas y las
otras tres recién empiezan. Ver "Contenido actual".

No es un banco de preguntas plano. Las piezas:

| Feature | Estado | Qué hace |
|---|---|---|
| **Modo Ensayo** | 🟢 Funcional | Ensayo configurable: prueba (las cinco), ejes, cantidad y ritmo. Tiempo proporcional al oficial. |
| **Puntaje y revisión** | 🟢 Funcional | Puntaje 100-1000 con tablas oficiales DEMRE, desglose por eje/dificultad/nodo, desarrollo paso a paso de cada pregunta. |
| **Árbol de Habilidades** | 🟢 Funcional | Temario de las cinco pruebas como grafo de nodos con prerrequisitos (`/arbol?prueba=`). Cada nodo trae su lección en `/aprender/[code]` --las cinco pruebas, no solo M1--: teoría, ejemplo resuelto paso a paso y el error típico, antes de practicar. |
| **Mi meta** | 🟢 Funcional | `/meta`: lista de hasta 10 preferencias con las ponderaciones oficiales del DEMRE, puntaje ponderado, simulador, ritmo contra la fecha de la PAES y plan de práctica. |
| **Práctica por nodo** | 🟢 Funcional | `/practicar/[code]`: una pregunta a la vez con corrección inmediata. |
| **Historial** | 🟢 Funcional | Evolución del puntaje, mejor/promedio/último, borrado por intento, respaldo JSON. |
| **Analítica** | 🟢 Funcional | Racha, precisión global, tiempo invertido, gráficos SVG propios. |
| **Demo sin cuenta** | 🟢 Funcional | `/demo`: 5 preguntas, sin auth y sin persistir nada. |
| **Panel de administración** | 🟢 Funcional | `/admin`: usuarios, entradas, visitas (incluidas anónimas) y uso del contenido. Solo cuentas con rol admin. |
| **Cobros / planes** | 🟡 Funciona, sin encender | Pasarela **Flow** integrada (`modules/billing`): catálogo con el precio en el servidor, `/plan/pagar`, confirmación por webhook y diagnóstico para admin. Hay una compra real completada. Los topes del plan Gratis se informan pero **no bloquean** mientras `LIMITES_ACTIVOS` esté apagado -- salvo el de carreras en Mi meta, que sí corta. |

### Contenido actual

Cifras verificadas contra la base de producción el **2026-08-24**. Si esta
sección vuelve a quedar vieja, se consulta con `scripts/verificar_banco.py` o
directo a la base: es más barato que discutirla.

- **52 nodos** de habilidad y **52 lecciones**, una por nodo. Las cinco
  pruebas tienen teoría escrita, no solo M1.
- **2.911 preguntas** con **11.644 alternativas**, y cada alternativa
  incorrecta trae su `distractor_justification`.

  | Prueba | Preguntas | Un ensayo pide | Nodos |
  |---|---:|---:|---:|
  | Matemática M1 | 1.088 | 65 | 17 |
  | Competencia Lectora | 1.103 | 65 | 12 |
  | Ciencias | 312 | 80 | 14 |
  | Matemática M2 | 213 | 55 | 15 |
  | Historia y Cs. Sociales | 195 | 65 | 6 |

  Las cinco superan tres veces lo que pide un ensayo completo. **Ampliar el
  banco ya no es el cuello de botella**; lo era cuando esta sección decía 344
  preguntas. (M2 reutiliza los nodos de M1, así que un ensayo de M2 elige entre
  1.301 preguntas, no 213.)

- **108 textos fuente** (`reading_passages`): 87 de Competencia Lectora y 21 de
  Historia.

El desbalance que quedaba era de **nodos**, no de preguntas, y **Lectora ya se
resolvió**: el 2026-08-26 pasó de 3 nodos a los 12 que salen de las *tareas
lectoras* que el temario enumera dentro de cada habilidad, con una lección por
nodo. El eje sigue siendo la habilidad, así que en pantalla son los mismos tres
grupos con doce nodos dentro.

**Queda Historia**: 195 preguntas en 6 nodos, contra los 17 de M1. Ahí el "qué
estudiar después" sólo puede recomendar una de seis cosas, y es donde el árbol
rinde menos de lo que promete.
- **1.855 carreras** con sus ponderaciones oficiales, extraídas del PDF del
  DEMRE con `scripts/extraer_carreras.py`. **Se re-extraen cada proceso de
  admisión**: las ponderaciones cambian todos los años. Varias preguntas comparten un mismo texto, igual que en la
  prueba real.
- M2 reutiliza el banco de M1 (`SUBJECT_INCLUDES` en `exam_focus/service.py`),
  porque el temario DEMRE dice que M2 evalúa *"todos los conocimientos de M1,
  además de"* contenido propio. Por eso el pool de M2 es M1 ∪ M2 = 282.

**Los bancos nuevos son chicos y hay que decirlo:** un ensayo oficial de
Historia son 65 preguntas y hay 9. Sirven para probar el flujo completo, no
todavía para practicar en serio.

**Qué NO cubre el banco de Historia y Ciencias:** preguntas de memoria pura.
Las de Historia y Formación ciudadana se apoyan en fuentes escritas por el
proyecto y se responden analizándolas — un test lo exige
(`test_historia_no_afirma_hechos_sin_fuente`). Publicar contenido factual sin
que lo revise un profesor rompería la primera regla del proyecto.

Todo el contenido vive en `apps/api/src/paes_api/seed_data.py` y se carga con
`scripts/seed.py` (idempotente: solo inserta preguntas cuyo `stem` no exista).

---

## 2. Arquitectura

Monorepo **Turborepo + pnpm workspaces**.

```
apps/web          Next.js 16 (App Router, TS) — frontend
apps/api          FastAPI (Python, uv)        — backend
packages/types    Tipos TS generados desde el OpenAPI de la API
packages/utils    Utilidades TS compartidas (cn)
```

**Por qué FastAPI y no Node**: afinidad con pandas/scikit-learn para el motor
de recomendación. Los tipos se generan desde el schema OpenAPI hacia
`packages/types` — **la API es la fuente de verdad de los tipos**, no al revés:

```bash
# con la API corriendo en :8000
cd packages/types && pnpm generate
```

### Backend — `apps/api/src/paes_api/`

Módulos verticales, uno por feature:

```
modules/skill_tree/    Árbol de Habilidades (grafo de prerequisitos, desbloqueo)
modules/exam_focus/    Modo Ensayo (config, runner, puntaje, revisión, historial)
  └ scoring.py         Tablas de conversión a puntaje PAES, parametrizadas por prueba
modules/practice/      Práctica por nodo individual
modules/analytics/     Dashboard
modules/demo/          Demo pública sin auth
modules/users/         Auth (registro, login, Google, reset de contraseña, perfil)
modules/metrics/       Ingesta pública de visitas (POST /metrics/pageview)
modules/admin/         Panel: agregados de usuarios, sesiones, visitas y contenido
modules/content/       Preguntas, alternativas
modules/colegios/      Plan Colegios: curso, código de seis letras, panel del
                       profesor, ejes del curso y ensayos agendados. El plan se
                       activa por fecha desde /admin (se vende con factura, no
                       con tarjeta) y mientras esté al día cada alumno del curso
                       tiene los límites del plan Pro.
modules/errores/       Errores de JavaScript reportados por el navegador,
                       agrupados por mensaje y ruta. Se ven en /admin.
all_models.py          Import único de TODOS los modelos SQLAlchemy. Necesario
                       para resolver relaciones declaradas por string; lo usan
                       alembic/env.py, scripts/seed.py y main.py.
seed_data.py           SKILL_NODES (M1), SKILL_NODES_M2 y QUESTIONS
```

**Regla de seguridad de contenido**: los endpoints de ensayo
(`start`/`get`/`answer`/`submit`) **nunca** exponen `is_correct` ni
`distractor_justification` mientras el ensayo está en curso. Esos datos solo
aparecen en `/review`, que exige el intento ya finalizado.

### Administración y métricas

`User.is_admin` da acceso a `/admin`. **No hay forma de volverse admin desde la
web**: el panel muestra datos de todas las cuentas, así que el rol se otorga a
mano con acceso a la base:

```bash
cd apps/api
uv run python scripts/make_admin.py correo@ejemplo.cl      # otorgar
uv run python scripts/make_admin.py correo@ejemplo.cl --quitar
uv run python scripts/make_admin.py --listar
```

Contra producción hay que exportar antes la `DATABASE_URL` **directa** de Neon,
igual que para alembic y el seed.

**Hoy el único rol admin es la cuenta del proyecto, `1000paessoporte@gmail.com`.**
Conviene que se registre desde la web (así elige su propia contraseña) y recién
después se le otorgue el rol con el script; `--crear` existe para entornos
locales, no para producción.

`/api/admin/metrics` responde **404 y no 403** a las cuentas sin rol: una cuenta
normal no debe enterarse de que el panel existe. La página `/admin` hace lo
mismo. El enlace en el header se oculta por comodidad, no por seguridad — la
API vuelve a comprobar el rol en cada llamada, así que editar la cookie no
sirve de nada.

De dónde salen los números:

- **Usuarios**: tabla `users`.
- **Entradas**: tabla `login_events`, una fila por inicio de sesión (incluido
  el registro, que deja la sesión abierta). `users.last_login_at` guarda solo
  la última: se usan las dos porque el campo suelto no puede responder
  "cuánta gente entró esta semana".
- **Visitas**: tabla `page_views`, alimentada por `PageViewTracker` en el
  layout raíz. Guarda la ruta (sin query string: el token de restablecer
  contraseña viaja ahí) y un identificador aleatorio de navegador guardado en
  localStorage. **No se guarda IP ni user agent** — está declarado así en
  `/privacidad`, y cambiarlo obliga a actualizar esa página.
- **Contenido**: `exam_answers` (correcta o no vía la alternativa elegida) más
  `practice_answers`. Las respuestas en blanco no entran al cálculo de
  acierto, y los rankings exigen un mínimo de 5 respuestas para que una
  pregunta contestada una sola vez no aparezca como "la peor".

Esto convive con Vercel Analytics sin reemplazarlo: aquel mide rendimiento y
tráfico, este alimenta las tablas que el panel cruza con registros y ensayos.

### El concepto `subject` (prueba PAES)

Añadido para soportar M2 sin duplicar el árbol de M1:

- `SkillNode.subject` y `ExamAttempt.subject` (enum `Subject`: `m1` | `m2`).
- `scoring.SCORING_BY_SUBJECT` guarda, por prueba, cuántas preguntas trae
  oficialmente, cuántas puntúan, cuánto dura y su tabla de conversión real
  del DEMRE. **No inventes tablas**: si agregas una prueba, consíguela en
  demre.cl.
- `/arbol` filtra a M1 a propósito (no hay UI de árbol para M2 todavía), pero
  el **cálculo de desbloqueos corre sobre todos los nodos** — los nodos de M2
  tienen prerequisitos en M1 y romper eso rompería el progreso.

### Frontend — `apps/web/`

```
app/page.tsx                      Portada: landing pública o panel según sesión
app/sobre-nosotros/               Quiénes somos
app/preguntas-frecuentes/         FAQ
app/terminos/, app/privacidad/    Legales
app/demo/                         Demo sin cuenta
app/(auth)/                       login, registro, olvide/restablecer contraseña
app/(dashboard)/                  arbol, examen, historial, analitica, perfil, practicar, admin
app/sitemap.ts, app/robots.ts     SEO
app/opengraph-image.tsx           Card de preview para redes/WhatsApp

components/auth/auth-panel.tsx        Entrar / crear cuenta en una sola pantalla
components/metrics/page-view-tracker.tsx  Avisa cada cambio de ruta al backend
components/home/landing-publica.tsx   Portada sin sesión
components/home/panel-inicio.tsx      Portada con sesión
components/site-header.tsx            Header global
components/site-footer.tsx            Footer global (columnas + redes sociales)
components/exam/exam-config.tsx       Config del ensayo (selector de prueba M1/M2)
components/exam/exam-runner.tsx       SPA del ensayo: timer, autosave, resume, atajos
components/texto-rico.tsx             LaTeX ($...$) con KaTeX y tablas markdown
lib/api.ts                            API_URL (server) vs NEXT_PUBLIC_API_URL (browser)
lib/redes-sociales.ts                 URLs de RRSS — ver abajo
```

**Redes sociales**: las cuentas todavía no existen. `lib/redes-sociales.ts`
tiene las llaves con string vacío y el footer **solo renderiza las que tengan
URL**, así no queda ningún link roto. Cuando existan, pegar la URL ahí y listo.

**Tema**: claro, definido con variables CSS en `app/globals.css`. Los
componentes usan tokens (`bg-surface`, `text-muted`, `border-border`…), así que
cambiar la paleta es editar solo `:root`.

---

## 3. Desarrollo local

```bash
pnpm install
pnpm dev            # web (:3000) + api (:8000) vía turbo
```

El backend solo: `cd apps/api && uv run uvicorn paes_api.main:app --reload`

Requiere PostgreSQL local. Variables en `apps/api/.env` (gitignored, ver
`.env.example`).

### Verificación antes de commitear

```bash
cd apps/api && uv run pytest tests/ -q && uv run ruff check src/
cd apps/web && pnpm typecheck && pnpm build
```

**Errores preexistentes conocidos** (no son regresiones tuyas, no los "arregles"
sin querer al revisar):

- `pnpm lint` falla con 2 errores: `app/page.tsx:21` (JSX dentro de try/catch)
  y `components/exam/exam-runner.tsx:71` (ref durante render).
- `uv run mypy src/` reporta 1 error en `exam_focus/router.py:42`.

---

## 4. Deploy ⚠️

**Todo cambio se cierra con: commit → push → deploy.** El deploy es explícito.

```bash
git add -A && git commit -m "..." && git push origin main

# Frontend — SIEMPRE desde la RAÍZ del repo
cd /ruta/al/repo && vercel deploy --prod --yes

# Backend — desde apps/api
cd apps/api && vercel deploy --prod --yes
```

Dos trampas que ya causaron problemas:

1. **Pushear a GitHub NO despliega nada.** No hay integración Git ↔ Vercel en
   este proyecto (verificado: los deployments no tienen `gitSource`). Si solo
   pusheas, producción sigue con el código viejo.
2. **El deploy del frontend se corre desde la raíz del repo, no desde
   `apps/web`.** Hacerlo desde `apps/web` crea un proyecto Vercel nuevo y roto
   (falla con `npm install` porque pierde el contexto del monorepo). El
   `.vercel/project.json` de la raíz apunta a `milpaes-web`.

### Proyectos Vercel

| Proyecto | Root | Qué sirve |
|---|---|---|
| `milpaes-web` | raíz del repo | Next.js. Alias: `1000paes.cl`, `www.1000paes.cl` |
| `milpaes-api` | `apps/api` | FastAPI como función serverless (`api/index.py`) |

La web reenvía `/api/*` al backend vía `next.config.ts` → `rewrites` usando la
env var `API_URL` (server-side). Por eso el navegador solo habla con
`1000paes.cl`: no hace falta subdominio de API ni CORS en producción, y
`NEXT_PUBLIC_API_URL` va **vacío** para que el browser use rutas relativas.

Región: ambos en `gru1` (São Paulo), igual que la DB. Tenerlos en regiones
distintas agregó ~700ms por request en su momento.

### Cuentas 🔑

**Todo este proyecto vive en `1000paessoporte@gmail.com`** (Vercel, Neon,
dominio). No usar cuentas personales para servicios del proyecto.

### Base de datos

PostgreSQL en **Neon**, región `sa-east-1`. Dos connection strings:

- **Pooled** (host con `-pooler`): para el runtime de la API → `DATABASE_URL` en Vercel.
- **Directa** (sin `-pooler`): para Alembic y `scripts/seed.py`.

La forma de ambos está documentada en [`HANDOFF.md`](HANDOFF.md), con la
contraseña como `<PASSWORD_NEON>`. El valor real se pide por canal privado y
vive solo en `apps/api/.env` local. Nunca en este README ni en ningún archivo
rastreado por git: el repo es público y los bots que rastrean GitHub encuentran
un `postgresql://…` con contraseña en minutos.

> ⚠️ `DATABASE_URL` en Vercel está marcada como **Sensitive**: es de solo
> escritura, nadie puede volver a leerla (ni el dueño). Si se pierden esas dos
> copias locales, la única salida es rotar la base. Ya pasó una vez.

Aplicar cambios de esquema y contenido a producción:

```bash
cd apps/api
export DATABASE_URL="<connection string DIRECTA>"
uv run alembic upgrade head
uv run python scripts/seed.py
```

---

## 5. Detalles que muerden

**Inicio de sesión con Google.** El browser obtiene un ID token firmado por
Google y lo manda a `POST /api/auth/google`, que verifica firma, expiración y
**audiencia** (que el token sea para nuestro client ID) antes de crear sesión.
Sin esa última comprobación, un token de cualquier otra app serviría para
entrar. Se configura con el mismo client ID en `GOOGLE_CLIENT_ID` (api) y
`NEXT_PUBLIC_GOOGLE_CLIENT_ID` (web). Si están vacías, el botón no se muestra y
el endpoint responde 401: la web sigue andando con correo y contraseña.
`NEXT_PUBLIC_*` se incrusta en build time, así que **hay que reconstruir**
después de cambiarlo. Google no acepta IPs privadas como origen autorizado.

El `<Script>` de Google usa **`onReady` y no `onLoad`**. `onLoad` corre solo la
primera vez que el script se descarga: al navegar dentro del sitio y volver, el
script ya está cargado, `onLoad` no vuelve a dispararse y el botón quedaba sin
renderizar (un hueco vacío en la portada y en registro). `onReady` corre también
en cada re-montaje del componente. No cambiarlo de vuelta.

**Entrar y crear cuenta son una sola pantalla** (`components/auth/auth-panel.tsx`),
con pestañas. `/login` y `/registro` siguen existiendo porque hay enlaces
repartidos por el sitio y el sitemap; cada ruta solo decide qué pestaña abre, y
cambiar de pestaña actualiza la URL con `replace`. Aceptan `?next=` para volver
a donde estaba la persona, y solo admiten rutas internas (un `next` con `http://`
o `//` permitiría usar 1000paes como trampolín a un sitio ajeno). Las páginas del
dashboard mandan su propia ruta al redirigir por 401. **Salvedad conocida**: el
gate de `app/(dashboard)/layout.tsx` corre sin sesión y no puede saber la ruta
(Next 16 no la expone por cabeceras, verificado), así que quien entra sin haber
iniciado sesión nunca cae en `/examen`, que es el comportamiento de siempre.

**Set de preguntas persistido.** Como la selección del ensayo es aleatoria y
proporcional por eje, el set de cada intento se guarda en
`exam_attempt_questions`. Sin eso, un GET posterior (resume tras refresh, o la
revisión meses después) no podría reconstruir el mismo ensayo. Los intentos
anteriores a esa tabla caen al comportamiento antiguo (todas las preguntas del
subject), que es exactamente el ensayo que rindieron.

**Contenido: nada de datos inventados.** Las tablas de puntaje, la cantidad de
preguntas y los tiempos salen del DEMRE. Las preguntas nuevas se verifican
matemáticamente antes de commitear (checklist: 4 alternativas, exactamente 1
correcta, sin texto duplicado, `skill_node` existente). La landing no muestra
logos de instituciones ni testimonios porque no los tenemos.

**Analytics.** `@vercel/analytics` y `@vercel/speed-insights` están montados en
`app/layout.tsx`. Las métricas se ven en el dashboard de Vercel.

---

## 6. Pendiente

Ordenado por impacto:

1. **Cobro del plan Colegios.** El producto ya existe (`modules/colegios`) y el
   acceso se activa a mano desde `/admin` poniendo la fecha hasta la que quedó
   pagado. Falta el circuito comercial: factura, orden de compra y renovación.
   Se decidió así a propósito —un colegio no compra con tarjeta— pero significa
   que alguien tiene que acordarse de renovar la fecha cada año.
2. **Huecos concretos del banco**, ya no su tamaño. Las cinco pruebas superan
   tres veces lo que pide un ensayo completo (ver §1), así que lo que falta son
   tramos precisos del temario, no volumen:

   - **Lectora, recursos lingüísticos y no lingüísticos.** Es una de las
     catorce tareas lectoras oficiales y tiene **cero** preguntas. Nuestros
     textos son sólo texto: no hay infografías, gráficos, color ni tipografía
     significativa, y el DEMRE sí los evalúa. Pide textos nuevos, no sólo
     preguntas.
   - **Lectora, dos nodos flacos**: *Idea central y jerarquía* (10 preguntas) y
     *Aplicar el texto a un caso nuevo* (12), contra 237 del mayor.
   - **Historia**: 195 preguntas repartidas en 6 nodos. Es la prueba que le
     queda al desbalance de nodos después de arreglar Lectora.
3. **Contenido factual con revisión de profesor.** Historia y Biología de
   memoria siguen fuera del banco a propósito: ningún script puede verificar
   que una afirmación histórica sea cierta. Ese tramo entra cuando alguien con
   la formación lo revise.
4. **Puntajes de corte de admisión.** `/meta` muestra hoy el *mínimo de
   postulación*, que viene en el PDF del DEMRE. El corte real —el puntaje del
   último seleccionado— lo publica cada universidad tras el proceso y no lo
   tenemos. Sin él, la pantalla dice "tu ponderado es 682" pero no "te faltan
   24 puntos para Medicina en la Chile". Es trabajo de recolección de datos,
   no de código, y **no se estima**: un corte inventado es alguien decidiendo
   su matrícula con información falsa.
5. **Lecciones para las otras cuatro pruebas.** Hoy solo M1 tiene teoría; el
   resto de los nodos lleva directo a practicar y el árbol lo dice en pantalla.
4. **Lecciones para las otras cuatro pruebas.** Hoy la teoría está escrita para los 15 nodos de M1; el resto lleva directo a practicar.
5. **Motor de recomendación real.** Hoy `get_recommended_node()` es un ranking
   ponderado con pandas (accuracy 60% + impacto 30% + nunca intentado 40%), no
   un modelo entrenado.
6. **Limpieza**: hay un proyecto Vercel llamado `web` creado por error en un
   deploy mal ejecutado. Está vacío y se puede borrar.
