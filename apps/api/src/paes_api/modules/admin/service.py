"""Consultas del panel de administración.

Todo lo que se muestra sale de tablas que ya existen; nada se estima ni se
inventa. Cuando un dato no se puede calcular (por ejemplo, promedio de puntaje
sin ensayos rendidos) el campo viaja como null y la pantalla lo dice, en lugar
de mostrar un 0 que se leería como "rindieron y sacaron cero"."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from paes_api.modules.admin.schemas import (
    AdminMetricsOut,
    ContenidoOut,
    ConteoPeriodo,
    NodoFlojo,
    PreguntaFallada,
    RutaVisitas,
    SerieDia,
    SesionesOut,
    UsuarioResumen,
    UsuariosOut,
    VisitasOut,
)
from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAnswer, ExamAttempt
from paes_api.modules.metrics.models import PageView
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import SkillNode
from paes_api.modules.users.models import LoginEvent, User

#: Cuántos días cubre cada gráfico de evolución.
DIAS_SERIE = 30
#: Cuántas filas trae cada ranking (rutas, preguntas, nodos).
TOPE_RANKING = 10
#: Mínimo de respuestas para que una pregunta o un nodo entre a un ranking de
#: acierto. Sin esto, una pregunta respondida una sola vez y fallada aparece
#: como "la peor" con 0%, que no significa nada.
MINIMO_RESPUESTAS = 5


def _ventanas(ahora: datetime) -> tuple[datetime, datetime, datetime]:
    inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio_hoy, ahora - timedelta(days=7), ahora - timedelta(days=30)


def _contar(db: Session, base: Select[tuple[int]], columna, ahora: datetime) -> ConteoPeriodo:
    """Aplica las tres ventanas al mismo COUNT."""
    hoy, hace_7, hace_30 = _ventanas(ahora)

    def total_desde(desde: datetime | None) -> int:
        consulta = base if desde is None else base.where(columna >= desde)
        return db.execute(consulta).scalar_one() or 0

    return ConteoPeriodo(
        hoy=total_desde(hoy),
        ultimos_7=total_desde(hace_7),
        ultimos_30=total_desde(hace_30),
        total=total_desde(None),
    )


def _serie_por_dia(db: Session, columna, base: Select, ahora: datetime) -> list[SerieDia]:
    """Serie diaria de los últimos DIAS_SERIE días, con los días sin actividad
    rellenados en cero: un gráfico que salta de un día al siguiente omitiendo
    los vacíos exagera la tendencia."""
    desde = (ahora - timedelta(days=DIAS_SERIE)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    filas = db.execute(
        base.where(columna >= desde)
        .group_by(func.date(columna))
        .with_only_columns(func.date(columna).label("dia"), func.count().label("valor"))
    ).all()
    por_dia = {str(fila.dia): int(fila.valor) for fila in filas}

    serie: list[SerieDia] = []
    for i in range(DIAS_SERIE + 1):
        dia = (desde + timedelta(days=i)).date().isoformat()
        serie.append(SerieDia(dia=dia, valor=por_dia.get(dia, 0)))
    return serie


def _usuarios(db: Session, ahora: datetime) -> UsuariosOut:
    registros = _contar(db, select(func.count()).select_from(User), User.created_at, ahora)

    ensayos_por_usuario: dict[int, int] = {
        int(user_id): int(total)
        for user_id, total in db.execute(
            select(ExamAttempt.user_id, func.count())
            .where(ExamAttempt.status == AttemptStatus.SUBMITTED)
            .group_by(ExamAttempt.user_id)
        ).all()
    }

    ultimos = [
        UsuarioResumen(
            id=u.id,
            email=u.email,
            name=u.name,
            created_at=u.created_at,
            last_login_at=u.last_login_at,
            ensayos=ensayos_por_usuario.get(u.id, 0),
        )
        for u in db.execute(
            select(User).order_by(User.created_at.desc()).limit(TOPE_RANKING)
        ).scalars()
    ]

    return UsuariosOut(
        registros=registros,
        nuevos_por_dia=_serie_por_dia(
            db, User.created_at, select(func.count()).select_from(User), ahora
        ),
        ultimos=ultimos,
    )


def _sesiones(db: Session, ahora: datetime) -> SesionesOut:
    _, hace_7, hace_30 = _ventanas(ahora)
    base = select(func.count()).select_from(LoginEvent)

    def activos(desde: datetime) -> int:
        return (
            db.execute(
                select(func.count(func.distinct(LoginEvent.user_id))).where(
                    LoginEvent.created_at >= desde
                )
            ).scalar_one()
            or 0
        )

    por_metodo = {
        str(metodo): int(total)
        for metodo, total in db.execute(
            select(LoginEvent.method, func.count())
            .where(LoginEvent.created_at >= hace_30)
            .group_by(LoginEvent.method)
        ).all()
    }

    return SesionesOut(
        entradas=_contar(db, base, LoginEvent.created_at, ahora),
        activos_7=activos(hace_7),
        activos_30=activos(hace_30),
        por_metodo=por_metodo,
        entradas_por_dia=_serie_por_dia(db, LoginEvent.created_at, base, ahora),
    )


def _visitas(db: Session, ahora: datetime) -> VisitasOut:
    _, hace_7, _ = _ventanas(ahora)
    base = select(func.count()).select_from(PageView)

    vistas = _contar(db, base, PageView.created_at, ahora)
    visitantes = _contar(
        db,
        select(func.count(func.distinct(PageView.visitor_id))).select_from(PageView),
        PageView.created_at,
        ahora,
    )

    anonimas_7 = (
        db.execute(
            select(func.count())
            .select_from(PageView)
            .where(PageView.created_at >= hace_7, PageView.user_id.is_(None))
        ).scalar_one()
        or 0
    )

    top_rutas = [
        RutaVisitas(path=str(fila.path), visitas=int(fila.visitas), visitantes=int(fila.visitantes))
        for fila in db.execute(
            select(
                PageView.path,
                func.count().label("visitas"),
                func.count(func.distinct(PageView.visitor_id)).label("visitantes"),
            )
            .where(PageView.created_at >= hace_7)
            .group_by(PageView.path)
            .order_by(func.count().desc())
            .limit(TOPE_RANKING)
        ).all()
    ]

    return VisitasOut(
        vistas=vistas,
        visitantes=visitantes,
        anonimas_7=anonimas_7,
        vistas_por_dia=_serie_por_dia(db, PageView.created_at, base, ahora),
        top_rutas=top_rutas,
    )


def _acierto_por_pregunta(db: Session) -> dict[int, tuple[int, int]]:
    """(respuestas, aciertos) por pregunta, juntando Modo Ensayo y Modo Práctica.

    Las respuestas en blanco no entran: omitir no es lo mismo que equivocarse, y
    mezclarlas haría ver difíciles preguntas que nadie alcanzó a leer."""
    acumulado: dict[int, list[int]] = defaultdict(lambda: [0, 0])

    for question_id, es_correcta, total in db.execute(
        select(ExamAnswer.question_id, Alternative.is_correct, func.count())
        .join(Alternative, Alternative.id == ExamAnswer.selected_alternative_id)
        .group_by(ExamAnswer.question_id, Alternative.is_correct)
    ).all():
        acumulado[int(question_id)][0] += int(total)
        if es_correcta:
            acumulado[int(question_id)][1] += int(total)

    for question_id, es_correcta, total in db.execute(
        select(PracticeAnswer.question_id, PracticeAnswer.is_correct, func.count()).group_by(
            PracticeAnswer.question_id, PracticeAnswer.is_correct
        )
    ).all():
        acumulado[int(question_id)][0] += int(total)
        if es_correcta:
            acumulado[int(question_id)][1] += int(total)

    return {qid: (datos[0], datos[1]) for qid, datos in acumulado.items()}


def _contenido(db: Session, ahora: datetime) -> ContenidoOut:
    rendidos = select(func.count()).select_from(ExamAttempt).where(
        ExamAttempt.status == AttemptStatus.SUBMITTED
    )
    ensayos = _contar(db, rendidos, ExamAttempt.finished_at, ahora)

    puntaje_promedio = db.execute(
        select(func.avg(ExamAttempt.estimated_score)).where(
            ExamAttempt.status == AttemptStatus.SUBMITTED,
            ExamAttempt.estimated_score.is_not(None),
        )
    ).scalar_one()

    por_pregunta = _acierto_por_pregunta(db)
    respuestas_totales = sum(total for total, _ in por_pregunta.values())
    aciertos_totales = sum(aciertos for _, aciertos in por_pregunta.values())

    candidatas = {
        qid: (total, aciertos)
        for qid, (total, aciertos) in por_pregunta.items()
        if total >= MINIMO_RESPUESTAS
    }

    preguntas: list[PreguntaFallada] = []
    nodos_acumulados: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    if por_pregunta:
        filas = db.execute(
            select(Question.id, Question.stem, Question.skill_node_id, SkillNode.axis, SkillNode.code, SkillNode.name)
            .join(SkillNode, SkillNode.id == Question.skill_node_id)
            .where(Question.id.in_(por_pregunta.keys()))
        ).all()
        info = {int(f.id): f for f in filas}

        for qid, (total, aciertos) in por_pregunta.items():
            fila = info.get(qid)
            if fila is None:
                continue
            nodos_acumulados[int(fila.skill_node_id)][0] += total
            nodos_acumulados[int(fila.skill_node_id)][1] += aciertos

        for qid, (total, aciertos) in candidatas.items():
            fila = info.get(qid)
            if fila is None:
                continue
            preguntas.append(
                PreguntaFallada(
                    question_id=qid,
                    stem=str(fila.stem)[:160],
                    axis=str(fila.axis),
                    respuestas=total,
                    tasa_acierto=round(aciertos / total, 3),
                )
            )
        preguntas.sort(key=lambda p: (p.tasa_acierto, -p.respuestas))
        preguntas = preguntas[:TOPE_RANKING]

    nodos: list[NodoFlojo] = []
    if nodos_acumulados:
        nombres = {
            int(n.id): n
            for n in db.execute(
                select(SkillNode).where(SkillNode.id.in_(nodos_acumulados.keys()))
            ).scalars()
        }
        for node_id, (total, aciertos) in nodos_acumulados.items():
            nodo = nombres.get(node_id)
            if nodo is None or total < MINIMO_RESPUESTAS:
                continue
            nodos.append(
                NodoFlojo(
                    code=nodo.code,
                    name=nodo.name,
                    respuestas=total,
                    tasa_acierto=round(aciertos / total, 3),
                )
            )
        nodos.sort(key=lambda n: (n.tasa_acierto, -n.respuestas))
        nodos = nodos[:TOPE_RANKING]

    return ContenidoOut(
        ensayos=ensayos,
        puntaje_promedio=round(float(puntaje_promedio), 1) if puntaje_promedio is not None else None,
        respuestas_totales=respuestas_totales,
        tasa_acierto_global=(
            round(aciertos_totales / respuestas_totales, 3) if respuestas_totales else None
        ),
        preguntas_mas_falladas=preguntas,
        nodos_mas_flojos=nodos,
    )


def build_metrics(db: Session) -> AdminMetricsOut:
    ahora = datetime.now(UTC)
    return AdminMetricsOut(
        generado_en=ahora,
        usuarios=_usuarios(db, ahora),
        sesiones=_sesiones(db, ahora),
        visitas=_visitas(db, ahora),
        contenido=_contenido(db, ahora),
    )
