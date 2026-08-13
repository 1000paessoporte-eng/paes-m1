from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.admin import service
from paes_api.modules.admin.schemas import AdminMetricsOut
from paes_api.modules.users.deps import get_current_admin
from paes_api.modules.users.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics", response_model=AdminMetricsOut)
def metrics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> AdminMetricsOut:
    """Todo el panel en una sola llamada: son consultas agregadas y baratas, y
    partirlas en cinco endpoints solo multiplicaría los viajes."""
    return service.build_metrics(db)
