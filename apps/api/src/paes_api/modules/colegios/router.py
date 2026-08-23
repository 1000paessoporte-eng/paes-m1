from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.colegios import service
from paes_api.modules.colegios.models import Colegio, EnsayoProgramado
from paes_api.modules.colegios.schemas import (
    AlumnoOut,
    ColegioAdminOut,
    ColegioOut,
    CrearColegioIn,
    CrearEnsayoIn,
    EjeCursoOut,
    EnsayoProgramadoOut,
    PlanColegioIn,
    UnirseIn,
)
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt
from paes_api.modules.users.deps import get_current_admin, get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/colegio", tags=["colegio"])

#: Hasta cuántos días atrás se listan los ensayos ya pasados. Un ensayo de
#: marzo no le sirve a nadie en octubre, pero el de la semana pasada sí: el
#: profesor todavía está viendo quién no lo rindió.
DIAS_PASADOS = 30


def _colegio_del_usuario(db: Session, user: User) -> Colegio:
    if user.colegio_id is None:
        raise HTTPException(status_code=404, detail="No perteneces a ningún curso")
    colegio = db.get(Colegio, user.colegio_id)
    if colegio is None:
        raise HTTPException(status_code=404, detail="No perteneces a ningún curso")
    return colegio


def _exigir_profesor(db: Session, user: User) -> Colegio:
    colegio = _colegio_del_usuario(db, user)
    if not user.es_profesor:
        raise HTTPException(
            status_code=403, detail="Esto lo ve el profesor del curso"
        )
    return colegio


def _armar_salida(db: Session, colegio: Colegio, user: User) -> ColegioOut:
    alumnos = (
        db.execute(
            select(func.count(User.id)).where(
                User.colegio_id == colegio.id, User.es_profesor.is_(False)
            )
        ).scalar_one()
        or 0
    )
    return ColegioOut(
        id=colegio.id,
        nombre=colegio.nombre,
        # El código solo viaja al profesor. Ver el comentario del schema.
        codigo=colegio.codigo if user.es_profesor else None,
        es_profesor=user.es_profesor,
        alumnos=int(alumnos),
    )


@router.get("", response_model=ColegioOut | None)
def mi_colegio(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> ColegioOut | None:
    """El curso al que pertenezco, o `null` si no pertenezco a ninguno."""
    if user.colegio_id is None:
        return None
    colegio = db.get(Colegio, user.colegio_id)
    if colegio is None:
        return None
    return _armar_salida(db, colegio, user)


@router.post("", response_model=ColegioOut, status_code=status.HTTP_201_CREATED)
def crear(
    payload: CrearColegioIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ColegioOut:
    try:
        colegio = service.crear_colegio(db, user, payload.nombre)
    except service.YaTieneColegio:
        raise HTTPException(
            status_code=409, detail="Ya perteneces a un curso. Sal de ese primero."
        ) from None
    return _armar_salida(db, colegio, user)


@router.post("/unirse", response_model=ColegioOut)
def unirse(
    payload: UnirseIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ColegioOut:
    try:
        colegio = service.unirse(db, user, payload.codigo)
    except service.YaTieneColegio:
        raise HTTPException(
            status_code=409, detail="Ya perteneces a un curso. Sal de ese primero."
        ) from None
    except service.CodigoInvalido:
        raise HTTPException(
            status_code=404, detail="Ese código no corresponde a ningún curso"
        ) from None
    return _armar_salida(db, colegio, user)


@router.post("/salir", status_code=status.HTTP_204_NO_CONTENT)
def salir(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    """Salir del curso. No borra nada de lo que la persona haya estudiado."""
    service.salir(db, user)


@router.get("/alumnos", response_model=list[AlumnoOut])
def alumnos(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[AlumnoOut]:
    colegio = _exigir_profesor(db, user)
    return [AlumnoOut(**a) for a in service.resumen_alumnos(db, colegio.id)]


@router.get("/ejes", response_model=list[EjeCursoOut])
def ejes(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[EjeCursoOut]:
    colegio = _exigir_profesor(db, user)
    return [EjeCursoOut(**e) for e in service.ejes_del_curso(db, colegio.id)]


@router.get("/ensayos", response_model=list[EnsayoProgramadoOut])
def listar_ensayos(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[EnsayoProgramadoOut]:
    """La agenda del curso: lo que viene, y lo reciente que ya pasó."""
    colegio = _colegio_del_usuario(db, user)
    # En UTC, igual que la analítica del alumno. Chile va tres o cuatro
    # horas atrás, así que un ensayo entregado después de las 21:00 cuenta
    # como del día siguiente. Se prefiere ese desajuste a que el panel del
    # profesor y el del alumno cuenten días distintos.
    desde = datetime.now(UTC).date() - timedelta(days=DIAS_PASADOS)
    programados = (
        db.execute(
            select(EnsayoProgramado)
            .where(
                EnsayoProgramado.colegio_id == colegio.id,
                EnsayoProgramado.fecha >= desde,
            )
            .order_by(EnsayoProgramado.fecha)
        )
        .scalars()
        .all()
    )

    salida: list[EnsayoProgramadoOut] = []
    for e in programados:
        # Un ensayo agendado no crea intentos: cuenta los que el curso rindió
        # de esa prueba ESE día. Obligar a entrar "por el ensayo del curso"
        # significaría un flujo aparte, y el alumno que lo dio por su cuenta
        # aparecería como que no lo hizo.
        base = select(func.count(ExamAttempt.id)).where(
            ExamAttempt.status == AttemptStatus.SUBMITTED,
            ExamAttempt.subject == e.subject,
            func.date(ExamAttempt.finished_at) == e.fecha,
        )
        if user.es_profesor:
            rendido = db.execute(
                base.join(User, User.id == ExamAttempt.user_id).where(
                    User.colegio_id == colegio.id, User.es_profesor.is_(False)
                )
            ).scalar_one()
            salida.append(
                EnsayoProgramadoOut(
                    id=e.id,
                    titulo=e.titulo,
                    subject=e.subject,
                    pace=e.pace,
                    question_count=e.question_count,
                    fecha=e.fecha,
                    rendido_por=int(rendido or 0),
                )
            )
        else:
            mio = db.execute(base.where(ExamAttempt.user_id == user.id)).scalar_one()
            salida.append(
                EnsayoProgramadoOut(
                    id=e.id,
                    titulo=e.titulo,
                    subject=e.subject,
                    pace=e.pace,
                    question_count=e.question_count,
                    fecha=e.fecha,
                    lo_rendi=bool(mio),
                )
            )
    return salida


@router.post(
    "/ensayos", response_model=EnsayoProgramadoOut, status_code=status.HTTP_201_CREATED
)
def agendar_ensayo(
    payload: CrearEnsayoIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> EnsayoProgramadoOut:
    colegio = _exigir_profesor(db, user)
    ensayo = EnsayoProgramado(
        colegio_id=colegio.id,
        titulo=payload.titulo.strip()[:160],
        subject=payload.subject,
        pace=payload.pace,
        question_count=payload.question_count,
        fecha=payload.fecha,
    )
    db.add(ensayo)
    db.commit()
    db.refresh(ensayo)
    return EnsayoProgramadoOut(
        id=ensayo.id,
        titulo=ensayo.titulo,
        subject=ensayo.subject,
        pace=ensayo.pace,
        question_count=ensayo.question_count,
        fecha=ensayo.fecha,
        rendido_por=0,
    )


@router.delete("/ensayos/{ensayo_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_ensayo(
    ensayo_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    colegio = _exigir_profesor(db, user)
    ensayo = db.get(EnsayoProgramado, ensayo_id)
    # Se compara el colegio y no solo el id: sin eso, un profesor podría borrar
    # la agenda de otro curso probando números.
    if ensayo is None or ensayo.colegio_id != colegio.id:
        raise HTTPException(status_code=404, detail="Ese ensayo no existe")
    db.delete(ensayo)
    db.commit()


# --- Administración -------------------------------------------------------
#
# El plan Colegios se vende conversando: la página de planes dice "Escríbenos"
# y no tiene botón de pago, porque un colegio compra con orden de compra y
# factura, no con tarjeta. Estos dos endpoints son lo que convierte esa
# conversación en acceso real, y por eso son de administración y no del
# profesor: el profesor no se activa el plan solo.


@router.get("/admin/todos", response_model=list[ColegioAdminOut])
def listar_colegios(
    db: Session = Depends(get_db), _: User = Depends(get_current_admin)
) -> list[ColegioAdminOut]:
    alumnos = (
        select(User.colegio_id.label("cid"), func.count(User.id).label("n"))
        .where(User.colegio_id.is_not(None), User.es_profesor.is_(False))
        .group_by(User.colegio_id)
        .subquery()
    )
    filas = db.execute(
        select(Colegio, alumnos.c.n)
        .outerjoin(alumnos, alumnos.c.cid == Colegio.id)
        .order_by(Colegio.creado_en.desc())
    ).all()
    return [
        ColegioAdminOut(
            id=c.id,
            nombre=c.nombre,
            codigo=c.codigo,
            alumnos=int(n or 0),
            plan_hasta=c.plan_hasta,
            creado_en=c.creado_en,
        )
        for c, n in filas
    ]


@router.put("/admin/{colegio_id}/plan", response_model=ColegioAdminOut)
def fijar_plan(
    colegio_id: int,
    payload: PlanColegioIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ColegioAdminOut:
    """Activa (o corta) el plan de un curso hasta una fecha.

    Mientras esté al día, cada alumno del curso tiene los límites del plan Pro
    sin suscripción propia: eso es lo que el colegio compró.
    """
    colegio = db.get(Colegio, colegio_id)
    if colegio is None:
        raise HTTPException(status_code=404, detail="Ese curso no existe")
    colegio.plan_hasta = payload.plan_hasta
    db.commit()
    db.refresh(colegio)

    alumnos = db.execute(
        select(func.count(User.id)).where(
            User.colegio_id == colegio.id, User.es_profesor.is_(False)
        )
    ).scalar_one()
    return ColegioAdminOut(
        id=colegio.id,
        nombre=colegio.nombre,
        codigo=colegio.codigo,
        alumnos=int(alumnos or 0),
        plan_hasta=colegio.plan_hasta,
        creado_en=colegio.creado_en,
    )
