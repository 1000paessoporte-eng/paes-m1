from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import paes_api.all_models  # noqa: F401 — registra todos los modelos en Base.metadata
from paes_api.core.config import get_settings
from paes_api.core.limiter import limiter
from paes_api.modules.admin.router import router as admin_router
from paes_api.modules.analytics.router import router as analytics_router
from paes_api.modules.billing.router import router as billing_router
from paes_api.modules.carreras.router import router as carreras_router
from paes_api.modules.colegios.router import router as colegios_router
from paes_api.modules.content.router import router as content_router
from paes_api.modules.correos.router import router as correo_router
from paes_api.modules.demo.router import router as demo_router
from paes_api.modules.errores.router import router as errores_router
from paes_api.modules.exam_focus.router import router as exam_router
from paes_api.modules.goals.router import router as goals_router
from paes_api.modules.leads.router import router as leads_router
from paes_api.modules.metrics.router import router as metrics_router
from paes_api.modules.practice.router import router as practice_router
from paes_api.modules.reminders.router import router as reminders_router
from paes_api.modules.reportes.router import router as reportes_router
from paes_api.modules.skill_tree.router import router as skill_tree_router
from paes_api.modules.users.router import router as users_router

settings = get_settings()

# En produccion la documentacion interactiva se apaga. /docs, /redoc y
# /openapi.json le entregan a cualquiera el mapa completo de la API --cada
# ruta, cada parametro, cada schema-- sin pedir nada. Es reconocimiento
# regalado para quien busca por donde entrar. En desarrollo siguen abiertas,
# que es donde sirven.
_es_prod = settings.environment.lower() == "production"

app = FastAPI(
    title="PAES M1 API",
    version="0.1.0",
    docs_url=None if _es_prod else "/docs",
    redoc_url=None if _es_prod else "/redoc",
    openapi_url=None if _es_prod else "/openapi.json",
)


@app.middleware("http")
async def _cabeceras_de_seguridad(request, call_next):
    """Cabeceras de endurecimiento en cada respuesta de la API.

    La web ya las manda (ver next.config.ts), pero la API es un dominio
    aparte y respondia solo con HSTS. Estas tres son las baratas y sin
    efectos secundarios: no adivinar el tipo de contenido, no dejarse
    enmarcar, y no filtrar la URL completa como referer."""
    respuesta = await call_next(request)
    respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
    respuesta.headers.setdefault("X-Frame-Options", "DENY")
    respuesta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return respuesta


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api")
app.include_router(skill_tree_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(exam_router, prefix="/api")
app.include_router(goals_router, prefix="/api")
app.include_router(practice_router, prefix="/api")
app.include_router(reminders_router, prefix="/api")
app.include_router(correo_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(demo_router, prefix="/api")
app.include_router(carreras_router, prefix="/api")
app.include_router(leads_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(colegios_router, prefix="/api")
app.include_router(errores_router, prefix="/api")
app.include_router(reportes_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("paes_api.main:app", host="0.0.0.0", port=8000, reload=True)
