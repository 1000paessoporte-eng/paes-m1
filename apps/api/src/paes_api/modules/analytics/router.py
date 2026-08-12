from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.analytics import service
from paes_api.modules.analytics.schemas import AnalyticsSummaryOut
from paes_api.modules.users.service import get_or_create_demo_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryOut)
def get_summary(db: Session = Depends(get_db)) -> AnalyticsSummaryOut:
    user = get_or_create_demo_user(db)
    return service.get_summary(db, user)
