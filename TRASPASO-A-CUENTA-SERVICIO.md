# Traspaso de la infraestructura a la cuenta de servicio

**Hecho el 2026-08-14.** `milpaes-web` y `milpaes-api` ya viven en la cuenta
`1000paessoporte@gmail.com` (usuario `1000paessoporte-9167`). Antes colgaban de
la cuenta personal de Pablo, en contra de la regla del proyecto.

Este documento queda como registro de qué se movió y de qué hay que rehacer si
alguna vez se repite la operación.

## Qué viajó solo y qué no

Contra lo esperado, Vercel se llevó casi todo:

| Cosa | ¿Viajó? |
|---|---|
| Deployments e historial | Sí |
| **Variables de entorno**, incluidas las Sensitive | **Sí** |
| Dominios `1000paes.cl` y `www`, ya verificados | Sí |
| `rootDirectory`, framework, `installCommand` | Sí |
| Previews sin protección SSO | Sí |
| **Conexión con GitHub** | **No: hay que rehacerla** |

Producción no se cayó en ningún momento: durante toda la operación
`1000paes.cl` respondió 200 y el login siguió funcionando.

## Lo único que quedó pendiente

La cuenta nueva necesita **conectar GitHub como método de acceso** antes de que
se puedan reenlazar los proyectos. Es un paso OAuth en el navegador, no hay API:

1. Entrar a https://vercel.com/account con `1000paessoporte@gmail.com`.
2. En *Login Connections*, conectar **GitHub**.
3. Después, reenlazar ambos proyectos (o pedírselo a Claude):

```bash
cd <raiz-del-repo> && vercel git connect
cd apps/api && vercel git connect https://github.com/Pabloajnxka/paes-m1
```

**Mientras no esté conectado no hay deploys automáticos ni previews por PR**:
los deploys hay que hacerlos a mano con `vercel deploy --prod`.

---

## Procedimiento de referencia

Lo que sigue es el guion completo, por si hay que repetir la operación.

---

## 0. Antes de empezar

Ten abierto `HANDOFF-PRIVADO.md`: vas a necesitar los valores de
`DATABASE_URL` y `SECRET_KEY`, porque **Vercel no los deja leer** (están
marcados Sensitive) y hay que volver a cargarlos a mano en la cuenta nueva.

---

## 1. Crear la cuenta destino

1. Cierra sesión de Vercel en el navegador.
2. Entra a https://vercel.com/signup y regístrate con
   **`1000paessoporte@gmail.com`** (opción *Continue with Email*).
3. Anota el nombre de usuario que quede asignado: lo necesitas en el paso 2.

---

## 2. Transferir cada proyecto

Con la sesión de la cuenta de origen, para `milpaes-web` y después
para `milpaes-api`:

1. Proyecto → **Settings** → **Advanced** → *Transfer Project*.
2. Elige como destino la cuenta nueva.
3. Entra con la cuenta nueva y **acepta** la transferencia.

El código, los deployments y el historial viajan. Lo que **no** viaja y hay que
rehacer está en el paso 3.

---

## 3. Reconstruir lo que no viaja

### 3.1 Variables de entorno

Se pierden las marcadas Sensitive. Estas son todas las que deben existir:

**`milpaes-api`** (Production):

| Variable | Valor |
|---|---|
| `DATABASE_URL` | el connection string **pooled** (ver `HANDOFF-PRIVADO.md`) |
| `SECRET_KEY` | el de `HANDOFF-PRIVADO.md` |
| `ENVIRONMENT` | `production` |
| `FRONTEND_URL` | `https://1000paes.cl` |
| `CORS_ORIGINS` | los dominios de producción |
| `GOOGLE_CLIENT_ID` | `138500299819-kkte7enhf4ur30rheecl6t7puc6rsj63.apps.googleusercontent.com` |

**`milpaes-api`** (Preview):

| Variable | Valor |
|---|---|
| `DATABASE_URL` | el connection string pooled de **`paes_preview`** |
| `SECRET_KEY` | cualquiera nuevo: `openssl rand -base64 48` |
| `ENVIRONMENT` | `preview` |

**`milpaes-web`** (Production):

| Variable | Valor |
|---|---|
| `API_URL` | la URL de producción de `milpaes-api` |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | el mismo client id de arriba |

**`milpaes-web`** (Preview):

| Variable | Valor |
|---|---|
| `API_URL` | `https://milpaes-api-preview.vercel.app` |

> `NEXT_PUBLIC_API_URL` va **vacía a propósito**. Si le pones un valor, rompes
> el login: el navegador debe usar rutas relativas que `next.config.ts` reenvía.

### 3.2 Ajustes de cada proyecto

| Proyecto | rootDirectory | framework | installCommand |
|---|---|---|---|
| `milpaes-web` | `apps/web` | nextjs | (por defecto) |
| `milpaes-api` | `apps/api` | fastapi | **`pip install -r requirements.txt`** |

El `installCommand` de la API **no es opcional**: `apps/api` tiene un
`package.json` (wrapper de turbo) y sin eso Vercel lo trata como proyecto Node,
no instala `requirements.txt` y la API cae con
`ModuleNotFoundError: No module named 'fastapi'`.

Ambos corren en la región **`gru1`** (São Paulo), definido en
`apps/api/vercel.json`. No los muevas: con la base en São Paulo, otra región
agregó ~700 ms por request.

### 3.3 Dominios

Volver a agregar en `milpaes-web` y reverificar:

- `1000paes.cl`
- `www.1000paes.cl`

El DNS está en Route53 y no cambia (apunta a `76.76.21.21`), pero Vercel pedirá
verificar la propiedad de nuevo en la cuenta nueva.

### 3.4 Conexión con GitHub y previews

1. Reconectar ambos proyectos al repo `Pabloajnxka/paes-m1`, rama de producción
   `main`.
2. Desactivar la protección SSO de los previews (si no, el socio no los puede
   abrir sin cuenta en esa cuenta de Vercel).
3. Reapuntar el alias del backend de pruebas:
   `vercel alias set <deployment-preview-api> milpaes-api-preview.vercel.app`

---

## 4. Neon

**Primero confirma en qué cuenta está.** Entra a https://console.neon.tech con
`1000paessoporte@gmail.com` y busca el proyecto con el endpoint
`ep-broad-glade-acd1vxdw` (región `sa-east-1`).

- Si aparece: no hay nada que transferir.
- Si no aparece: está en otra cuenta. Entra con esa y usa
  Settings → *Transfer project*.

---

## 5. Después de transferir

En la máquina de cada socio hay que reautenticar la CLI:

```bash
vercel logout
vercel login          # con 1000paessoporte@gmail.com
cd <raiz-del-repo> && vercel link
cd apps/api && vercel link
```

Y verificar que producción sigue en pie:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://1000paes.cl/
curl -s -X POST https://1000paes.cl/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@paes-m1.cl","password":"demo1234"}' -w "\n%{http_code}\n"
```

Ambos deben responder 200. Si el login falla, casi siempre es `DATABASE_URL` o
`SECRET_KEY` mal cargadas en el paso 3.1.

---

## 6. El acceso del socio sigue pendiente

Transferir a la cuenta de servicio **no** le da acceso a Mati: el plan Hobby
tiene un solo asiento. Las opciones siguen siendo:

1. **Team Pro** (~US$20 al mes por miembro): cada uno con su cuenta, permisos y
   registro de quién hizo qué. Es lo correcto para dos socios.
2. **Token de Vercel** revocable, generado en
   https://vercel.com/account/tokens: le permite desplegar sin entrar a la
   cuenta, pero sin dashboard.
3. Compartir el login de la cuenta de servicio: funciona, pero no se puede
   auditar ni revocar por persona.
