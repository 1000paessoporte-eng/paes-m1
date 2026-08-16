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
from paes_api.modules.content.router import router as content_router
from paes_api.modules.demo.router import router as demo_router
from paes_api.modules.exam_focus.router import router as exam_router
from paes_api.modules.goals.router import router as goals_router
from paes_api.modules.metrics.router import router as metrics_router
from paes_api.modules.practice.router import router as practice_router
from paes_api.modules.reminders.router import router as reminders_router
from paes_api.modules.skill_tree.router import router as skill_tree_router
from paes_api.modules.users.router import router as users_router

settings = get_settings()

app = FastAPI(title="PAES M1 API", version="0.1.0")

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
app.include_router(analytics_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(demo_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("paes_api.main:app", host="0.0.0.0", port=8000, reload=True)
