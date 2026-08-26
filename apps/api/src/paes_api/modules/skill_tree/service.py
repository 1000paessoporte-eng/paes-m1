"""Progreso y desbloqueo del Árbol de Habilidades.

El estado (`UserSkillProgress`) se crea de forma perezosa: la primera vez
que se pide el árbol de un usuario, se crea una fila LOCKED/UNLOCKED por
nodo según tenga o no prerequisitos. El recálculo de desbloqueos
(`_recompute_unlocks`) se corre tanto al leer el árbol como después de
cada submit de examen, así que siempre es consistente aunque no se llame
en un orden particular — es barato (15 nodos) así que no vale la pena
optimizar evitando la relectura.

Un nodo se desbloquea cuando TODOS sus prerequisitos tienen accuracy >=
node.unlock_threshold con al menos MIN_ATTEMPTS_FOR_UNLOCK respuestas (para
no desbloquear con una sola respuesta suerte). Un nodo se marca MASTERED
cuando el propio usuario alcanza ese mismo estándar en el nodo."""

from datetime import UTC, datetime

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import ExamAnswer
from paes_api.modules.skill_tree.models import (
    AXIS_LABELS,
    ProgressStatus,
    SkillNode,
    Subject,
    UserSkillProgress,
)
from paes_api.modules.skill_tree.schemas import (
    LeccionIndiceOut,
    LessonOut,
    LessonStepOut,
    SkillNodeProgressOut,
)

MIN_ATTEMPTS_FOR_UNLOCK = 4


def _load_nodes(db: Session) -> dict[int, SkillNode]:
    nodes = (
        db.execute(select(SkillNode).options(selectinload(SkillNode.prerequisites)))
        .scalars()
        .all()
    )
    return {n.id: n for n in nodes}


def _ensure_progress(
    db: Session, user_id: int, nodes_by_id: dict[int, SkillNode]
) -> dict[int, UserSkillProgress]:
    existing = (
        db.execute(select(UserSkillProgress).where(UserSkillProgress.user_id == user_id))
        .scalars()
        .all()
    )
    progress_by_node = {p.skill_node_id: p for p in existing}

    for node_id in nodes_by_id:
        if node_id in progress_by_node:
            continue
        # NADIE NACE BLOQUEADO. El árbol pasó de puerta a mapa: muestra en qué
        # orden conviene estudiar --los prerequisitos siguen ahí, dibujando los
        # conectores y el "se apoya en"-- pero ya no impide entrar a ningún
        # tema.
        #
        # El caso que lo forzó fue M2: sus dieciséis temas cuelgan de M1, así
        # que quien iba a rendir M2 abría su árbol y lo encontraba entero gris.
        # Y era incoherente con Modo Ensayo, que nunca bloqueó nada: ese mismo
        # alumno podía rendir un ensayo de M2 completo el primer día.
        #
        # `MASTERED` sigue existiendo: dominar un tema se sigue reconociendo,
        # que es la parte del juego que premia en vez de prohibir.
        progress = UserSkillProgress(
            user_id=user_id,
            skill_node_id=node_id,
            status=ProgressStatus.UNLOCKED,
            unlocked_at=datetime.now(UTC),
        )
        db.add(progress)
        progress_by_node[node_id] = progress
    db.flush()
    return progress_by_node


def _recompute_unlocks(
    nodes_by_id: dict[int, SkillNode], progress_by_node: dict[int, UserSkillProgress]
) -> None:
    changed = True
    guard = 0
    while changed and guard <= len(nodes_by_id):
        changed = False
        guard += 1
        for node_id, node in nodes_by_id.items():
            progress = progress_by_node[node_id]

            # Los nodos ya no nacen bloqueados, pero esto sigue acá para las
            # cuentas que SÍ tienen filas en LOCKED de antes del cambio: se
            # abren en cuanto el usuario vuelve a mirar su árbol, sin pedirle
            # nada. La migración de datos hace lo mismo de una vez; esto cubre
            # lo que se le escape.
            if progress.status == ProgressStatus.LOCKED:
                progress.status = ProgressStatus.UNLOCKED
                progress.unlocked_at = datetime.now(UTC)
                changed = True

            if (
                progress.status == ProgressStatus.UNLOCKED
                and progress.attempts >= MIN_ATTEMPTS_FOR_UNLOCK
                and progress.accuracy >= node.unlock_threshold
            ):
                progress.status = ProgressStatus.MASTERED
                progress.mastered_at = datetime.now(UTC)
                changed = True


def get_user_skill_tree(
    db: Session, user_id: int, subject: Subject | None = Subject.M1
) -> list[SkillNodeProgressOut]:
    """`subject=None` trae los nodos de TODAS las pruebas (uso interno /
    admin); por defecto se filtra a M1 porque hoy el Árbol de Habilidades en
    /arbol solo tiene UI para esa prueba. El cálculo de desbloqueos corre
    igual sobre TODOS los nodos sin filtrar, para no romper el progreso de
    pruebas que sí dependen de nodos de otro subject (M2 depende de M1)."""
    nodes_by_id = _load_nodes(db)
    progress_by_node = _ensure_progress(db, user_id, nodes_by_id)
    _recompute_unlocks(nodes_by_id, progress_by_node)
    db.commit()

    ordered = sorted(nodes_by_id.values(), key=lambda n: (n.axis, n.display_order))
    if subject is not None:
        ordered = [n for n in ordered if n.subject == subject]
    return [
        SkillNodeProgressOut(
            id=node.id,
            code=node.code,
            name=node.name,
            axis=node.axis,
            subject=node.subject,
            tier=node.tier,
            unlock_threshold=node.unlock_threshold,
            display_order=node.display_order,
            prerequisite_codes=[p.code for p in node.prerequisites],
            prerequisite_names=[p.name for p in node.prerequisites],
            status=progress_by_node[node.id].status,
            accuracy=progress_by_node[node.id].accuracy,
            attempts=progress_by_node[node.id].attempts,
            has_lesson=node.lesson is not None,
            lesson_intro=node.lesson.intro if node.lesson is not None else None,
            min_attempts_to_master=MIN_ATTEMPTS_FOR_UNLOCK,
        )
        for node in ordered
    ]


def _compute_impact(nodes_by_id: dict[int, SkillNode]) -> dict[int, int]:
    """Cuántos nodos dependen directamente de cada nodo (out-degree en el
    grafo de prerequisitos). Un nodo con impacto alto desbloquea más
    contenido futuro si se domina, así que pesa más en la recomendación."""
    impact = dict.fromkeys(nodes_by_id, 0)
    for node in nodes_by_id.values():
        for prereq in node.prerequisites:
            impact[prereq.id] += 1
    return impact


def get_recommended_node(
    db: Session, user_id: int, subject: Subject = Subject.M1
) -> SkillNodeProgressOut | None:
    """Motor adaptativo v1: ranking analítico con pandas sobre tres señales
    por nodo desbloqueado y no dominado — NO es un modelo de ML entrenado
    (aún no hay suficientes datos de usuarios para eso), es un score
    ponderado y transparente:

    - accuracy baja  -> más urgente (60% del peso)
    - impacto alto (cuántos nodos desbloquea) -> más prioritario (30%)
    - nunca intentado -> bonus fijo, para guiar la exploración del árbol (40%)

    None si no hay nada desbloqueado pendiente de dominar."""

    nodes_by_id = _load_nodes(db)
    # El árbol de la prueba que se está mirando, no el de M1 siempre.
    # `get_user_skill_tree` sin argumento devuelve M1 por defecto, así que la
    # tarjeta "Empieza por acá" recomendaba un nodo de M1 en las cinco
    # pestañas: alguien que abría el árbol de Ciencias leía "Medidas de
    # posición" y, al tocar "Practicar ahora", terminaba fuera de la prueba
    # que estaba preparando.
    tree = get_user_skill_tree(db, user_id, subject=subject)
    candidates = [n for n in tree if n.status == ProgressStatus.UNLOCKED]
    if not candidates:
        return None

    impact = _compute_impact(nodes_by_id)
    max_impact = max(impact.values()) or 1

    df = pd.DataFrame(
        [
            {
                "code": n.code,
                "accuracy": n.accuracy,
                "never_attempted": 1.0 if n.attempts == 0 else 0.0,
                "impact": impact.get(n.id, 0) / max_impact,
            }
            for n in candidates
        ]
    )
    df["score"] = (
        (1 - df["accuracy"]) * 0.6 + df["impact"] * 0.3 + df["never_attempted"] * 0.4
    )
    best_code = df.sort_values("score", ascending=False).iloc[0]["code"]
    return next(n for n in candidates if n.code == best_code)


def apply_single_answer(
    db: Session, user_id: int, skill_node_id: int, is_correct: bool
) -> list[SkillNode]:
    """Aplica una respuesta de práctica (una pregunta a la vez, feedback
    inmediato) y retorna los nodos que pasaron de LOCKED a UNLOCKED como
    consecuencia — para celebrar el desbloqueo en el frontend."""

    nodes_by_id = _load_nodes(db)
    progress_by_node = _ensure_progress(db, user_id, nodes_by_id)

    locked_before = {
        nid for nid, p in progress_by_node.items() if p.status == ProgressStatus.LOCKED
    }

    progress = progress_by_node[skill_node_id]
    progress.attempts += 1
    progress.correct += int(is_correct)

    _recompute_unlocks(nodes_by_id, progress_by_node)
    db.commit()

    return [
        nodes_by_id[nid]
        for nid in locked_before
        if progress_by_node[nid].status != ProgressStatus.LOCKED
    ]


def apply_attempt_results(db: Session, user_id: int, attempt_id: int) -> None:
    """Suma al progreso por nodo las respuestas de un intento recién
    finalizado y recalcula desbloqueos. Debe llamarse UNA sola vez por
    intento (justo al transicionar IN_PROGRESS -> SUBMITTED), o los
    conteos quedarían duplicados."""

    rows = db.execute(
        select(Question.skill_node_id, Alternative.is_correct)
        .select_from(ExamAnswer)
        .join(Question, ExamAnswer.question_id == Question.id)
        .join(Alternative, ExamAnswer.selected_alternative_id == Alternative.id)
        .where(
            ExamAnswer.attempt_id == attempt_id,
            ExamAnswer.selected_alternative_id.is_not(None),
        )
    ).all()
    if not rows:
        return

    deltas: dict[int, list[int]] = {}
    for skill_node_id, is_correct in rows:
        d = deltas.setdefault(skill_node_id, [0, 0])
        d[0] += 1
        d[1] += int(bool(is_correct))

    nodes_by_id = _load_nodes(db)
    progress_by_node = _ensure_progress(db, user_id, nodes_by_id)

    for node_id, (attempts, correct) in deltas.items():
        progress = progress_by_node[node_id]
        progress.attempts += attempts
        progress.correct += correct

    _recompute_unlocks(nodes_by_id, progress_by_node)
    db.commit()


def get_lesson(db: Session, code: str) -> LessonOut | None:
    """La teoría de un nodo, o None si todavía no tiene.

    No exige progreso: un estudiante puede leer la teoría de un tema bloqueado.
    Bloquear el acceso a la explicación sería castigar justo a quien más la
    necesita; lo que se desbloquea con el progreso es la práctica, no el
    estudio.
    """
    node = db.execute(
        select(SkillNode).where(SkillNode.code == code)
    ).scalar_one_or_none()
    if node is None or node.lesson is None:
        return None

    leccion = node.lesson
    return LessonOut(
        node_code=node.code,
        node_name=node.name,
        intro=leccion.intro,
        theory=leccion.theory,
        example_statement=leccion.example_statement,
        example_steps=[LessonStepOut(**paso) for paso in leccion.example_steps],
        common_error=leccion.common_error,
    )


def listar_lecciones(db: Session) -> list[LeccionIndiceOut]:
    """Los nodos que YA tienen lección escrita, para el índice público.

    Solo los que la tienen: un índice que promete 47 temas y entrega 17
    lecciones manda a Google a 30 redirecciones y a la persona a un tema vacío.
    """
    nodos = (
        db.execute(
            select(SkillNode)
            .join(SkillNode.lesson)
            .options(selectinload(SkillNode.lesson))
            .order_by(SkillNode.subject, SkillNode.display_order, SkillNode.name)
        )
        .scalars()
        .all()
    )
    return [
        LeccionIndiceOut(
            node_code=n.code,
            node_name=n.name,
            subject=n.subject.value,
            axis=n.axis.value,
            axis_label=AXIS_LABELS.get(n.axis.value, n.axis.value),
        )
        for n in nodos
    ]
