# 🤝 HANDOFF — 1000paes

> **Documento de traspaso.** Todo lo que necesitas para tomar este proyecto y
> seguir trabajándolo: arquitectura, cuentas, infraestructura, puesta en marcha
> y pendientes.
>
> **Este archivo es público y NO contiene secretos.** Donde veas
> `<PASSWORD_NEON>`, `<SECRET_KEY>` o `<pedir a Pablo...>`, ese valor se pide
> por canal privado (gestor de contraseñas, llamada) y se guarda **solo** en
> tu `.env` local, que está gitignored. Nunca lo commitees acá.

---

## 0. Para la IA que está leyendo esto

Estás tomando un proyecto en marcha. Contexto mínimo antes de tocar nada:

- **Qué es**: `1000paes` — plataforma web chilena para preparar la PAES (prueba
  de admisión universitaria). Está **en producción y con usuarios**:
  https://1000paes.cl
- **Quiénes**: proyecto de dos socios. Pablo Ortega lo desarrolló hasta acá
  (con Claude Code); tú continúas desde la cuenta del socio.
- **Lee primero el `README.md`** del repo: ahí está la arquitectura completa,
  el estado de cada feature y las trampas del deploy. Este archivo solo agrega
  lo que no puede ir en un repo público: las credenciales.
- **Reglas de trabajo que el proyecto ya tiene** (respétalas):
  1. Cada cambio de código se cierra con **rama `nombre/loquesea` → PR → squash
     merge**. `main` está protegida y **el deploy es automático desde el
     2026-08-14**: Vercel está conectado a GitHub, así que un push a una rama
     con PR levanta un preview con URL propia y el merge a `main` publica
     producción. Ya no hace falta `vercel deploy --prod` ni ningún token.
  2. Si alguna vez hay que desplegar a mano, el deploy del **frontend se corre
     desde la raíz del repo**, nunca desde `apps/web` (hacerlo ahí crea un
     proyecto Vercel roto).
  3. **Cero datos inventados**. Las tablas de puntaje, los tiempos y la
     cantidad de preguntas salen del DEMRE (demre.cl). Las preguntas nuevas se
     verifican matemáticamente antes de subirlas. La landing no muestra logos
     de instituciones ni testimonios porque no existen.
  4. Las cuentas de servicio del proyecto usan `1000paessoporte@gmail.com`,
     nunca correos personales. Vercel y GitHub ya están ahí (se migraron el
     2026-08-14). **La excepción que queda es Neon**: la base de producción
     sigue viviendo en la cuenta personal de Pablo — ver sección 2.

---

## 1. Cuentas

| Servicio | Cuenta | Para qué |
|---|---|---|
| Vercel | cuenta de servicio `1000paessoporte@gmail.com` — usuario `1000paessoporte-9167` (plan **Hobby**) | Hosting y deploy (`milpaes-web`, `milpaes-api`) |
| Google / Gmail | `1000paessoporte@gmail.com` | Cuenta raíz del proyecto: entra a Vercel y a Neon |
| Neon | **cuenta personal de Pablo** (verificado 2026-08-16) | PostgreSQL de producción — endpoint `ep-broad-glade-acd1vxdw` |
| GitHub | `1000paessoporte-eng/paes-m1` (**público**) | Código |
| Dominio | `1000paes.cl` | DNS en AWS Route53 (lo administra el papá de Pablo) |

**Contraseña de `1000paessoporte@gmail.com`:** _(Pablo: escríbela acá antes de
enviar este archivo, o compártela por un gestor de contraseñas)_

```
CONTRASEÑA_GMAIL = <pedir a Pablo por canal privado>
```

> **Para el deploy no hace falta ninguna de las dos cosas.** Desde el
> 2026-08-14 Vercel despliega solo al mergear a `main`, así que no se necesita
> ni la contraseña de la cuenta ni un token. La contraseña sigue siendo útil
> para entrar a la consola de Vercel (variables de entorno, logs, dominios).
>
> Si alguna vez hiciera falta desplegar a mano con un token revocable
> (https://vercel.com/account/tokens), el scope es el del **team de servicio**:
>
> ```bash
> vercel deploy --prod --yes --token=EL_TOKEN --scope=1000paessoporte-9167s-projects
> ```
>
> El scope `pablos-projects-27637841` que decía este archivo quedó obsoleto con
> el traspaso: ahí ya no vive ninguno de los dos proyectos.

---

## 2. Base de datos (Neon / PostgreSQL)

Proyecto Neon en la región `sa-east-1` (São Paulo), usuario `neondb_owner`.
Hay **dos bases** dentro del mismo proyecto:

| Base | Para qué | Quién la usa |
|---|---|---|
| `neondb` | Producción, con datos de estudiantes reales | `1000paes.cl` |
| `paes_preview` | Pruebas: mismo esquema y las mismas 282 preguntas, sin datos reales | los previews de cada PR |

Los previews **nunca** apuntan a `neondb`: sus variables de entorno en Vercel
son de tipo Preview y traen el string de `paes_preview`. Por eso se puede
romper lo que sea en un PR sin tocar a nadie.

Para obtener el string de `paes_preview`, se toma el de producción y se cambia
`/neondb?` por `/paes_preview?`.

**Hay dos connection strings y NO son intercambiables:**

**Pooled** — para el runtime de la API (es la que está en Vercel como `DATABASE_URL`):
```
postgresql://neondb_owner:<PASSWORD_NEON>@ep-broad-glade-acd1vxdw-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Directa** (sin `-pooler`) — para Alembic y `scripts/seed.py`:
```
postgresql+psycopg://neondb_owner:<PASSWORD_NEON>@ep-broad-glade-acd1vxdw.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

> ⚠️ En Vercel, `DATABASE_URL` está marcada como **Sensitive**: es de solo
> escritura. Nadie puede volver a leerla desde el dashboard ni por CLI, ni
> siquiera el dueño. **Este archivo es la única copia recuperable.** Ya se
> perdió una vez y hubo que rotar la base entera.

### Aplicar migraciones o cargar contenido nuevo a producción

```bash
cd apps/api
export DATABASE_URL="postgresql+psycopg://neondb_owner:<PASSWORD_NEON>@ep-broad-glade-acd1vxdw.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
uv run alembic upgrade head      # esquema
uv run python scripts/seed.py    # contenido (idempotente: no duplica)
```

### Cuenta de prueba

```
demo@paes-m1.cl / demo1234
```

---

## 3. Vercel — proyectos y variables

| Proyecto | Root del deploy | Sirve | Project ID |
|---|---|---|---|
| `milpaes-web` | **raíz del repo** | Next.js. Alias `1000paes.cl` y `www.1000paes.cl` | `prj_pNtav9y32SQRpZxy43A6Hp6Z4cKg` |
| `milpaes-api` | `apps/api` | FastAPI serverless | `prj_7edSJGd2ofYW8oW0MuJZTnVD5mBR` |

Los proyectos se transfirieron el 2026-08-14 desde la cuenta personal de Pablo
a la cuenta de servicio; el detalle está en `TRASPASO-A-CUENTA-SERVICIO.md`.

Ambos proyectos están conectados a `github.com/1000paessoporte-eng/paes-m1`, con
`main` como rama de producción y `apps/web` / `apps/api` como directorio raíz
respectivamente.

Ambos corren en la región **`gru1`** (São Paulo), igual que la base de datos.
Tenerlos en regiones distintas agregó ~700 ms por request en su momento — no
los muevas.

### Variables de entorno en `milpaes-api` (producción)

| Variable | Valor |
|---|---|
| `DATABASE_URL` | el connection string **pooled** de arriba |
| `SECRET_KEY` | `<SECRET_KEY>` |
| `ENVIRONMENT` | `production` |
| `FRONTEND_URL` | `https://1000paes.cl` |
| `CORS_ORIGINS` | los dominios de producción |
| `GOOGLE_CLIENT_ID` | **vacío** (login con Google no configurado todavía) |

> El `SECRET_KEY` de arriba es el que está en el `.env` local de Pablo. En
> Vercel la variable también está marcada Sensitive, así que no se puede
> confirmar que sea idéntica. Si el login empieza a fallar con sesiones
> inválidas, es porque difieren: en ese caso resetea la de Vercel con este
> valor (`vercel env rm SECRET_KEY production` y luego `vercel env add`).

### Variables en `milpaes-web`

| Variable | Valor |
|---|---|
| `API_URL` | la URL de producción de `milpaes-api` |
| `NEXT_PUBLIC_API_URL` | **vacío a propósito** — así el navegador usa rutas relativas que `next.config.ts` reenvía a la API. Si le pones un valor, rompes el login. |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | vacío |

---

## 4. Puesta en marcha desde cero (máquina nueva)

```bash
# 1. Herramientas
#    Node 20+, pnpm, uv (Python), y la CLI de Vercel:
npm i -g pnpm vercel        # o: brew install pnpm vercel
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Código
git clone https://github.com/1000paessoporte-eng/paes-m1.git
cd paes-m1
pnpm install

# 3. Autenticar Vercel (login: 1000paessoporte@gmail.com, o el token de la seccion 1)
vercel login
vercel link --yes                      # enlaza milpaes-web (desde la raíz)
cd apps/api && vercel link --yes       # enlaza milpaes-api

# 4. Variables locales
#    apps/api/.env y apps/web/.env.local NO están en git. Créalos:
```

`apps/api/.env` (desarrollo local, con Postgres local):
```
DATABASE_URL=postgresql+psycopg://paes:paes@localhost:5432/paes_m1
SECRET_KEY=<SECRET_KEY>
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000"]
GOOGLE_CLIENT_ID=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=1000paes <no-responder@1000paes.cl>
```

`apps/web/.env.local`:
```
API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_GOOGLE_CLIENT_ID=
```

```bash
# 5. Base local: crea la DB en Postgres y aplica esquema + contenido
cd apps/api
uv run alembic upgrade head
uv run python scripts/seed.py

# 6. Levantar todo
cd ../.. && pnpm dev     # web :3000 + api :8000
```

**Atajo si no quieres montar Postgres local**: puedes apuntar el `.env` local a
la base de producción (connection string directo). Sirve para ver datos reales,
pero **cualquier cosa que escribas afecta a producción**. Úsalo solo para leer.

---

## 5. Rutina de trabajo

`main` está protegida: **no se pushea directo**, todo entra por Pull Request.
Cada socio trabaja en su propia rama.

```bash
git switch -c pablo/lo-que-sea      # o mati/lo-que-sea
# ... trabajar ...

# Verificar antes de pedir merge
cd apps/api && uv run pytest tests/ -q && uv run ruff check src/ scripts/
cd apps/api && uv run python scripts/verificar_banco.py
cd apps/web && pnpm typecheck && pnpm build

git push -u origin <tu-rama>        # o la skill /ship, que hace todo esto
```

### El deploy es automático (desde 2026-08-14)

Los proyectos de Vercel están conectados al repo de GitHub:

| Qué pasa | Qué despliega Vercel |
|---|---|
| Push a una rama con PR | Un **preview** por proyecto, con URL propia |
| Merge a `main` | **Producción**: `1000paes.cl` y la API |

Ya **no** hay que correr `vercel deploy --prod` a mano. Si alguna vez hace falta
(por ejemplo, para forzar un redeploy), el frontend se despliega desde la
**raíz** del repo y nunca desde `apps/web`.

Los previews son públicos, para que ambos socios puedan abrirlos sin tener
cuenta en la misma cuenta de Vercel.

### La regla que ya rompió producción

**Si tocaste modelos de datos, aplica la migración a producción ANTES de que se
despliegue la API.** El 2026-08-14 un commit agregó columnas a `users`, la
migración nunca se aplicó, y al desplegar la API el login empezó a devolver 500
porque el modelo pedía columnas inexistentes.

```bash
cd apps/api
DATABASE_URL="<string directo>" uv run alembic upgrade head
```

Y si agregaste preguntas al banco, no basta con desplegar: hay que sembrarlas.

```bash
DATABASE_URL="<string directo>" uv run python scripts/seed.py
```

**Errores preexistentes conocidos** — no son regresiones, no los persigas:
- `pnpm lint` falla con 2 errores (`app/page.tsx:21`, `exam-runner.tsx:71`).
- `uv run mypy src/` reporta 1 error en `exam_focus/router.py:42`.

---

## 6. Qué falta hacer (por impacto)

1. **Pasarela de pago** (Webpay/Transbank, Flow o MercadoPago). Los planes Pro
   y Colegios hoy son vitrina: no se puede cobrar.
2. **Más preguntas.** Hay 144 (111 M1 + 33 M2). Un ensayo M1 completo son 65,
   así que todavía hay poco margen antes de que se repitan.
3. **Las otras 3 pruebas PAES.** Ojo: Competencia Lectora **no encaja** en el
   modelo actual de nodos por eje — necesita pasajes de lectura con preguntas
   asociadas, o sea otro diseño de datos. Historia y Ciencias sí encajan, pero
   necesitan contenido factual verificado.
4. **UI del Árbol de Habilidades para M2** (hoy `/arbol` solo muestra M1).
5. **Redes sociales**: las cuentas no existen. Cuando estén, se pegan las URLs
   en `apps/web/lib/redes-sociales.ts` y el footer las muestra solo.
6. **Limpieza**: quedó un proyecto Vercel llamado `web`, vacío, creado por un
   deploy mal ejecutado. Se puede borrar.
7. **Correo `hola@1000paes.cl`**: aparece en los Términos y en la Privacidad
   como contacto para eliminar cuentas. Verificar que esa casilla exista de
   verdad, o cambiar el texto.

---

## 7. Si se filtran estas credenciales

En orden:

1. **Neon**: dashboard → el proyecto → Roles → resetear la contraseña de
   `neondb_owner`. Después actualiza `DATABASE_URL` en Vercel
   (`vercel env rm DATABASE_URL production` + `vercel env add`) y redespliega
   `milpaes-api`. Actualiza también este archivo.
2. **Vercel**: revoca el token en https://vercel.com/account/tokens y cambia la
   contraseña de la cuenta Google.
3. **`SECRET_KEY`**: genera uno nuevo (`openssl rand -base64 48`) y reemplázalo
   en Vercel. Ojo: esto **cierra la sesión de todos los usuarios**, porque
   invalida los JWT emitidos. Es el precio correcto si hubo filtración.

## Recordatorios por correo

El sistema está construido y **no envía nada todavía**: sin `SMTP_HOST`, cada
correo se escribe en el log del servidor en vez de salir. Es a propósito, para
poder probar el flujo completo antes de contratar un proveedor.

Para activarlo hacen falta dos variables en el proyecto `milpaes-api` de Vercel:

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` — de
  Resend, Brevo o el proveedor que se elija. El plan gratuito de cualquiera de
  los dos alcanza de sobra para el volumen actual.
- `CRON_SECRET` — cualquier cadena larga y aleatoria. Sin ella el endpoint
  `/api/reminders/run` responde 404 y no se puede disparar desde fuera.

El cron ya está declarado en `apps/api/vercel.json` y corre todos los días a las
22:00 UTC (19:00 en Chile continental). El día que existan esas variables,
empieza a mandar correos sin tocar código.

Reglas que el sistema respeta, y que conviene no relajar: nunca escribe a quien
apagó los recordatorios en su perfil, nunca dos veces en menos de dos días,
nunca a quien ya rindió hoy, y nunca a una cuenta con más de 45 días sin
actividad. Cada correo lleva el enlace para apagarlos.
