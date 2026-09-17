from collections import Counter
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.content.models import Question
from paes_api.modules.reportes.models import ReportePregunta
from paes_api.modules.reportes.schemas import (
    ComentarioOut,
    ReporteIn,
    ReportePreguntaOut,
)
from paes_api.modules.users.deps import get_current_admin, get_current_user_optional
from paes_api.modules.users.models import User

router = APIRouter(prefix="/reportes", tags=["reportes"])

#: Cuántas preguntas reportadas devuelve el panel. Si alguna vez hay más que
#: esto pendientes, el problema no es el panel.
LIMITE_PANEL = 100

#: Dentro de esta ventana, el mismo alumno reportando la misma pregunta no
#: agrega una fila. Pasa solo: se reporta durante el ensayo y otra vez en la
#: retroalimentación, al ver que la clave era la que uno había descartado.
VENTANA_REPETIDO = timedelta(days=1)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def reportar_pregunta(
    request: Request,
    payload: ReporteIn,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> None:
    """Recibe el aviso de que una pregunta está mal.

    Sin sesión también: la demo se responde sin cuenta y es donde entra gente
    que nunca nos va a escribir un correo.

    Responde 204 y nada más. El alumno está en medio de un ensayo: lo único que
    necesita ver es que el aviso se fue.
    """
    if db.get(Question, payload.question_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado")

    comentario = (payload.comentario or "").strip() or None

    # El mismo alumno avisando dos veces de la misma pregunta es un aviso, no
    # dos. Sin esto, reportar en el ensayo y de nuevo en la revisión inflaría
    # el contador que usamos justamente para priorizar.
    if user is not None:
        repetido = db.execute(
            select(ReportePregunta.id).where(
                ReportePregunta.question_id == payload.question_id,
                ReportePregunta.user_id == user.id,
                ReportePregunta.creado_en > datetime.now(UTC) - VENTANA_REPETIDO,
            )
        ).first()
        if repetido is not None:
            return

    db.add(
        ReportePregunta(
            question_id=payload.question_id,
            user_id=user.id if user else None,
            motivo=payload.motivo,
            comentario=comentario,
            contexto=payload.contexto,
        )
    )
    db.commit()


@router.get("", response_model=list[ReportePreguntaOut])
def listar_reportes(
    incluir_revisados: bool = False,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[ReportePreguntaOut]:
    """Las preguntas reportadas, la más reportada primero.

    Agrupadas por pregunta: lo que se arregla es la pregunta, y tres alumnos
    avisando de la misma son una sola cosa que hacer. Por defecto solo trae las
    que tienen algún aviso pendiente; el historial completo se pide aparte,
    porque una pregunta ya revisada y dejada como está va a seguir juntando
    avisos para siempre.
    """
    filas = db.execute(
        select(ReportePregunta)
        .options(
            selectinload(ReportePregunta.question).selectinload(Question.alternatives),
            selectinload(ReportePregunta.question).selectinload(Question.skill_node),
        )
        .order_by(ReportePregunta.creado_en.desc())
    ).scalars().all()

    por_pregunta: dict[int, list[ReportePregunta]] = {}
    for fila in filas:
        por_pregunta.setdefault(fila.question_id, []).append(fila)

    salida: list[ReportePreguntaOut] = []
    for question_id, avisos in por_pregunta.items():
        pendientes = sum(1 for a in avisos if a.revisado_en is None)
        if pendientes == 0 and not incluir_revisados:
            continue

        pregunta = avisos[0].question
        correcta = next((a for a in pregunta.alternatives if a.is_correct), None)
        motivos = Counter(a.motivo for a in avisos)

        salida.append(
            ReportePreguntaOut(
                question_id=question_id,
                stem=pregunta.stem,
                skill_node_name=pregunta.skill_node.name,
                respuesta_correcta=correcta.text if correcta else None,
                reportes=len(avisos),
                pendientes=pendientes,
                motivos=dict(motivos.most_common()),
                comentarios=[
                    ComentarioOut(
                        motivo=a.motivo,
                        comentario=a.comentario,
                        contexto=a.contexto,
                        creado_en=a.creado_en,
                        revisado_en=a.revisado_en,
                    )
                    for a in avisos
                ],
                ultimo_en=max(a.creado_en for a in avisos),
            )
        )

    # Primero lo que más gente reportó y todavía nadie miró. El empate se
    # rompe por lo más reciente.
    salida.sort(key=lambda r: (r.pendientes, r.ultimo_en), reverse=True)
    return salida[:LIMITE_PANEL]


@router.post("/{question_id}/revisado", status_code=status.HTTP_204_NO_CONTENT)
def marcar_revisado(
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> None:
    """Cierra todos los avisos de una pregunta.

    Vale tanto si la pregunta se corrigió como si se revisó y estaba bien: en
    los dos casos ya no hay nada que hacer con esos avisos. La pregunta sigue
    en el panel si alguien vuelve a reportarla.
    """
    pendientes = db.execute(
        select(ReportePregunta).where(
            ReportePregunta.question_id == question_id,
            ReportePregunta.revisado_en.is_(None),
        )
    ).scalars().all()
    if not pendientes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado")

    ahora = datetime.now(UTC)
    for aviso in pendientes:
        aviso.revisado_en = ahora
    db.commit()
