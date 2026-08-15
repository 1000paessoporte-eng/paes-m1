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
    BancoOut,
    CoberturaPrueba,
    ContenidoOut,
    ConteoPeriodo,
    EmbudoOut,
    EnsayosOut,
    NodoFlojo,
    PreguntaFallada,
    RetencionOut,
    RutaVisitas,
    SerieDia,
    SesionesOut,
    UsoPrueba,
    UsuarioResumen,
    UsuariosOut,
    VisitasOut,
)
from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAnswer, ExamAttempt
from paes_api.modules.exam_focus.scoring import SCORING_BY_SUBJECT
from paes_api.modules.exam_focus.service import SUBJECT_INCLUDES
from paes_api.modules.metrics.models import PageView
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import SkillNode, Subject
from paes_api.modules.users.models import LoginEvent, User

#: Cuántos días cubre cada gráfico de evolución.
DIAS_SERIE = 30
#: Cuántas filas trae cada ranking (rutas, preguntas, nodos).
TOPE_RANKING = 10
#: Mínimo de respuestas para que una pregunta o un nodo entre a un ranking de
#: acierto. Sin esto, una pregunta respondida una sola vez y fallada aparece
#: como "la peor" con 0%, que no significa nada.
MINIMO_RESPUESTAS = 5
#: Un ensayo en curso sin actividad por más tiempo que esto se cuenta como
#: abandonado. Nadie retoma al día siguiente un ensayo cronometrado.
HORAS_PARA_ABANDONO = 24
#: Piso de preguntas para que un nodo sea practicable de verdad.
MINIMO_POR_NODO = 5


def _tasa(numerador: int, denominador: int) -> float | None:
    """None cuando no hay denominador: un 0% diría que nadie convierte, cuando
    lo que pasa es que todavía nadie llegó a ese paso."""
    return numerador / denominador if denominador else None


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


def _embudo(db: Session, ahora: datetime) -> EmbudoOut:
    """Dónde se cae la gente entre entrar y terminar un ensayo."""
    _, _, hace_30 = _ventanas(ahora)

    visitantes = (
        db.execute(
            select(func.count(func.distinct(PageView.visitor_id))).where(
                PageView.created_at >= hace_30
            )
        ).scalar_one()
        or 0
    )

    nuevos = select(User.id).where(User.created_at >= hace_30).scalar_subquery()
    registrados = (
        db.execute(select(func.count()).select_from(User).where(User.created_at >= hace_30)).scalar_one()
        or 0
    )

    def cuentas_con_ensayo(solo_terminados: bool) -> int:
        stmt = select(func.count(func.distinct(ExamAttempt.user_id))).where(
            ExamAttempt.user_id.in_(nuevos)
        )
        if solo_terminados:
            stmt = stmt.where(ExamAttempt.status == AttemptStatus.SUBMITTED)
        return db.execute(stmt).scalar_one() or 0

    con_ensayo = cuentas_con_ensayo(False)
    terminado = cuentas_con_ensayo(True)

    # Un navegador que primero anduvo anónimo y después apareció con sesión es
    # una conversión observada, no estimada. Es lo más cerca que se puede
    # llegar sin guardar nada que identifique a la persona.
    anonimos = select(func.distinct(PageView.visitor_id)).where(
        PageView.created_at >= hace_30, PageView.user_id.is_(None)
    )
    convertidos = (
        db.execute(
            select(func.count(func.distinct(PageView.visitor_id))).where(
                PageView.created_at >= hace_30,
                PageView.user_id.is_not(None),
                PageView.visitor_id.in_(anonimos),
            )
        ).scalar_one()
        or 0
    )

    return EmbudoOut(
        visitantes=visitantes,
        registrados=registrados,
        con_ensayo=con_ensayo,
        con_ensayo_terminado=terminado,
        tasa_registro=_tasa(registrados, visitantes),
        tasa_activacion=_tasa(con_ensayo, registrados),
        tasa_finalizacion=_tasa(terminado, con_ensayo),
        visitantes_convertidos=convertidos,
    )


def _retencion(db: Session, ahora: datetime) -> RetencionOut:
    """Cuánta gente vuelve. Se mide sobre visitas, que es la señal más amplia:
    alguien puede entrar a leer una lección sin responder nada."""
    _, hace_7, hace_30 = _ventanas(ahora)

    dias_por_usuario = db.execute(
        select(
            PageView.user_id,
            func.count(func.distinct(func.date(PageView.created_at))).label("dias"),
        )
        .where(PageView.created_at >= hace_30, PageView.user_id.is_not(None))
        .group_by(PageView.user_id)
    ).all()

    un_dia = sum(1 for f in dias_por_usuario if f.dias == 1)
    dos_a_tres = sum(1 for f in dias_por_usuario if 2 <= f.dias <= 3)
    cuatro_o_mas = sum(1 for f in dias_por_usuario if f.dias >= 4)

    # Solo puede "volver" quien lleva al menos una semana registrado: contar a
    # quien se inscribió ayer como no-retornado castiga a los más nuevos.
    con_tiempo = db.execute(
        select(User.id, User.created_at).where(User.created_at < hace_7)
    ).all()
    base = len(con_tiempo)
    volvieron = 0
    for user_id, creado in con_tiempo:
        despues = (
            db.execute(
                select(func.count())
                .select_from(PageView)
                .where(
                    PageView.user_id == user_id,
                    func.date(PageView.created_at) > func.date(creado),
                )
            ).scalar_one()
            or 0
        )
        if despues:
            volvieron += 1

    return RetencionOut(
        un_dia=un_dia,
        dos_a_tres=dos_a_tres,
        cuatro_o_mas=cuatro_o_mas,
        volvieron=volvieron,
        base_volvieron=base,
    )


def _ensayos(db: Session, ahora: datetime) -> EnsayosOut:
    """Qué se rinde, qué se abandona y con qué prueba."""
    iniciados = db.execute(select(func.count()).select_from(ExamAttempt)).scalar_one() or 0
    terminados = (
        db.execute(
            select(func.count())
            .select_from(ExamAttempt)
            .where(ExamAttempt.status == AttemptStatus.SUBMITTED)
        ).scalar_one()
        or 0
    )
    abandonados = (
        db.execute(
            select(func.count())
            .select_from(ExamAttempt)
            .where(
                ExamAttempt.status == AttemptStatus.IN_PROGRESS,
                ExamAttempt.started_at < ahora - timedelta(hours=HORAS_PARA_ABANDONO),
            )
        ).scalar_one()
        or 0
    )

    # Mediana y no promedio: un solo ensayo dejado abierto tres horas mueve el
    # promedio lo suficiente como para inventar una tendencia que no existe.
    duraciones = sorted(
        (fin - ini).total_seconds() / 60
        for ini, fin in db.execute(
            select(ExamAttempt.started_at, ExamAttempt.finished_at).where(
                ExamAttempt.finished_at.is_not(None)
            )
        ).all()
    )
    mediana = None
    if duraciones:
        medio = len(duraciones) // 2
        mediana = (
            duraciones[medio]
            if len(duraciones) % 2
            else (duraciones[medio - 1] + duraciones[medio]) / 2
        )

    por_prueba: list[UsoPrueba] = []
    for subject in Subject:
        filas = db.execute(
            select(
                func.count().label("iniciados"),
                func.count(ExamAttempt.finished_at).label("terminados"),
                func.avg(ExamAttempt.estimated_score).label("promedio"),
            ).where(ExamAttempt.subject == subject)
        ).one()
        if not filas.iniciados:
            continue
        por_prueba.append(
            UsoPrueba(
                subject=subject.value,
                iniciados=int(filas.iniciados),
                terminados=int(filas.terminados),
                puntaje_promedio=round(float(filas.promedio), 1) if filas.promedio else None,
            )
        )

    return EnsayosOut(
        iniciados=iniciados,
        terminados=terminados,
        abandonados=abandonados,
        tasa_finalizacion=_tasa(terminados, iniciados),
        duracion_mediana_min=round(mediana, 1) if mediana is not None else None,
        por_prueba=por_prueba,
    )


def _banco(db: Session) -> BancoOut:
    """Si el banco alcanza para lo que la portada promete.

    Es la métrica que evita el peor error del producto: ofrecer las cinco
    pruebas y que una de ellas no arme ni un ensayo completo."""
    respondidas = set(
        db.execute(select(func.distinct(ExamAnswer.question_id))).scalars().all()
    ) | set(db.execute(select(func.distinct(PracticeAnswer.question_id))).scalars().all())

    por_prueba: list[CoberturaPrueba] = []
    for subject, scoring in SCORING_BY_SUBJECT.items():
        ids = (
            db.execute(
                select(Question.id)
                .join(Question.skill_node)
                .where(SkillNode.subject.in_(SUBJECT_INCLUDES[subject]))
            )
            .scalars()
            .all()
        )
        banco = len(ids)
        por_prueba.append(
            CoberturaPrueba(
                subject=subject.value,
                banco=banco,
                oficiales=scoring.preguntas_oficiales,
                ensayos_completos=round(banco / scoring.preguntas_oficiales, 2),
                nunca_respondidas=sum(1 for qid in ids if qid not in respondidas),
            )
        )

    flacos = [
        str(code)
        for code, total in db.execute(
            select(SkillNode.code, func.count(Question.id))
            .outerjoin(Question, Question.skill_node_id == SkillNode.id)
            .group_by(SkillNode.code)
            .order_by(SkillNode.code)
        ).all()
        if total < MINIMO_POR_NODO
    ]

    return BancoOut(por_prueba=por_prueba, nodos_flacos=flacos)


def build_metrics(db: Session) -> AdminMetricsOut:
    ahora = datetime.now(UTC)
    return AdminMetricsOut(
        generado_en=ahora,
        usuarios=_usuarios(db, ahora),
        sesiones=_sesiones(db, ahora),
        visitas=_visitas(db, ahora),
        contenido=_contenido(db, ahora),
        embudo=_embudo(db, ahora),
        retencion=_retencion(db, ahora),
        ensayos=_ensayos(db, ahora),
        banco=_banco(db),
    )
