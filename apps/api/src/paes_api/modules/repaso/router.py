from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.repaso import service
from paes_api.modules.repaso.models import RepasoItem
from paes_api.modules.repaso.schemas import (
    RepasoAlternativaOut,
    RepasoPreguntaOut,
    RepasoRespuestaIn,
    RepasoRespuestaOut,
    RepasoResumenOut,
    RepasoSesionOut,
)
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/repaso", tags=["repaso"])


@router.get("/resumen", response_model=RepasoResumenOut)
def resumen(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> RepasoResumenOut:
    """Qué toca hoy. Lo consulta el panel, así que corre en cada visita: por eso
    la puesta al día de la cola vive acá y no en el cierre del ensayo."""
    service.asegurar_items(db, user.id)
    return RepasoResumenOut(**service.resumen(db, user.id))


@router.get("/sesion", response_model=RepasoSesionOut)
def sesion(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> RepasoSesionOut:
    service.asegurar_items(db, user.id)
    items = service.pendientes(db, user.id)

    preguntas: list[RepasoPreguntaOut] = []
    for item in items:
        pregunta = service.cargar_pregunta(db, item.question_id)
        if pregunta is None:
            # La pregunta salió del banco entre medio. No es un error del
            # alumno: se omite y la cola sigue.
            continue
        preguntas.append(
            RepasoPreguntaOut(
                question_id=pregunta.id,
                difficulty=pregunta.difficulty,
                stem=pregunta.stem,
                image_url=pregunta.image_url,
                passage=pregunta.passage.body if pregunta.passage else None,
                passage_title=pregunta.passage.title if pregunta.passage else None,
                node_name=pregunta.skill_node.name,
                alternatives=[
                    RepasoAlternativaOut(id=a.id, label=a.label, text=a.text)
                    for a in pregunta.alternatives
                ],
                veces_fallada=item.veces_fallada,
                nivel=item.nivel,
            )
        )

    return RepasoSesionOut(
        preguntas=preguntas,
        pendientes_totales=service.resumen(db, user.id)["pendientes_hoy"],
    )


@router.post("/responder", response_model=RepasoRespuestaOut)
def responder(
    payload: RepasoRespuestaIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RepasoRespuestaOut:
    item = db.execute(
        select(RepasoItem).where(
            RepasoItem.user_id == user.id, RepasoItem.question_id == payload.question_id
        )
    ).scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Esta pregunta no está en tu repaso")

    pregunta = service.cargar_pregunta(db, payload.question_id)
    if pregunta is None:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")

    elegida = next(
        (a for a in pregunta.alternatives if a.id == payload.selected_alternative_id), None
    )
    if elegida is None:
        raise HTTPException(status_code=422, detail="Alternativa inválida para esta pregunta")
    correcta = next(a for a in pregunta.alternatives if a.is_correct)

    service.registrar_respuesta(item, elegida.is_correct)

    # La respuesta se guarda como cualquier otra práctica: así el repaso suma a
    # la racha y a la analítica en vez de ser un rincón que no cuenta. Sin esto,
    # quien estudia repasando aparecería como que no estudió.
    db.add(
        PracticeAnswer(
            user_id=user.id,
            question_id=pregunta.id,
            skill_node_id=pregunta.skill_node_id,
            is_correct=elegida.is_correct,
        )
    )
    db.commit()

    return RepasoRespuestaOut(
        is_correct=elegida.is_correct,
        correct_alternative_id=correcta.id,
        explanation=pregunta.explanation,
        distractor_justification=None if elegida.is_correct else elegida.distractor_justification,
        proxima_fecha=item.proxima_fecha,
        dominada=item.proxima_fecha is None,
        nivel=item.nivel,
    )
