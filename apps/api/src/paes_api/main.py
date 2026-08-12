from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import paes_api.all_models  # noqa: F401 — registra todos los modelos en Base.metadata
from paes_api.core.config import get_settings
from paes_api.modules.analytics.router import router as analytics_router
from paes_api.modules.content.router import router as content_router
from paes_api.modules.exam_focus.router import router as exam_router
from paes_api.modules.skill_tree.router import router as skill_tree_router

settings = get_settings()

app = FastAPI(title="PAES M1 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skill_tree_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(exam_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("paes_api.main:app", host="0.0.0.0", port=8000, reload=True)
