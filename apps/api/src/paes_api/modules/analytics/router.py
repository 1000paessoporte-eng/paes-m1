from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.analytics import service
from paes_api.modules.analytics.schemas import AnalyticsSummaryOut
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryOut)
def get_summary(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> AnalyticsSummaryOut:
    return service.get_summary(db, user)
