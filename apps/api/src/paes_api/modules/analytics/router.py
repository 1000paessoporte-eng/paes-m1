from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.analytics import service
from paes_api.modules.analytics.schemas import AnalyticsSummaryOut, DiagnosticoOut
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryOut)
def get_summary(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> AnalyticsSummaryOut:
    return service.get_summary(db, user)


@router.get("/diagnostico", response_model=DiagnosticoOut)
def get_diagnostico(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> DiagnosticoOut:
    """Qué hace mal el alumno, y por qué.

    Dos cosas que ninguna otra pantalla responde: los errores de razonamiento
    en que cae repetidamente --con el texto que ya está escrito en el banco
    para cada distractor-- y su ritmo contra el que exige la prueba real.

    Las dos partes pueden venir vacías, y eso es correcto: con pocos datos no
    se dice nada en vez de decir algo falso.
    """
    return service.diagnostico(db, user)
