"""Lógica del Modo Ensayo.

El estudiante arma el ensayo: elige ejes, cantidad de preguntas y ritmo, y el
tiempo se calcula en proporción a la prueba oficial (140 min / 65 preguntas).
La selección se reparte proporcionalmente entre los ejes elegidos y se
persiste en `exam_attempt_questions`, porque al ser aleatoria ya no se puede
reconstruir de forma determinística como cuando el examen era siempre completo.
"""

import random
from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from paes_api.modules.content.models import Question
from paes_api.modules.exam_focus import scoring
from paes_api.modules.exam_focus.models import (
    PACE_FACTOR,
    AttemptStatus,
    ExamAnswer,
    ExamAttempt,
    ExamAttemptQuestion,
    Pace,
)
from paes_api.modules.exam_focus.schemas import (
    AxisOptionOut,
    BreakdownItemOut,
    ExamAnswerIn,
    ExamAnswerState,
    ExamAttemptSummary,
    ExamConfigIn,
    ExamConfigOut,
    ExamOptionsOut,
    ExamResultOut,
    ExamReviewOut,
    NodeDiagnosisOut,
    RepasoOut,
    ReviewAlternativeOut,
    ReviewQuestionOut,
)
from paes_api.modules.skill_tree import service as skill_tree_service
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject
from paes_api.modules.users.models import User

#: Nombre legible de cada eje, como aparece en el temario DEMRE.
AXIS_LABELS: dict[str, str] = {
    # Competencia Lectora se organiza por habilidades, no por ejes de contenido.
    SkillAxis.LOCALIZAR.value: "Localizar información",
    SkillAxis.INTERPRETAR.value: "Interpretar y relacionar",
    SkillAxis.EVALUAR.value: "Evaluar y reflexionar",
    # Ciencias: los ejes son las tres disciplinas del temario.
    SkillAxis.BIOLOGIA.value: "Biología",
    SkillAxis.FISICA.value: "Física",
    SkillAxis.QUIMICA.value: "Química",
    # Historia y Ciencias Sociales.
    SkillAxis.HISTORIA.value: "Historia",
    SkillAxis.CIUDADANIA.value: "Formación ciudadana",
    SkillAxis.ECONOMIA.value: "Economía y sociedad",
    SkillAxis.NUMEROS.value: "Números",
    SkillAxis.ALGEBRA.value: "Álgebra y Funciones",
    SkillAxis.GEOMETRIA.value: "Geometría",
    SkillAxis.PROBABILIDAD.value: "Probabilidad y Estadística",
}

DIFFICULTY_LABELS = {"facil": "Fácil", "medio": "Medio", "dificil": "Difícil"}

#: Qué subjects entran al banco de una prueba. M2 evalúa "todos los
#: conocimientos de M1, además de" contenido propio (temario DEMRE), así que
#: su pool incluye los nodos de M1 más los exclusivos de M2.
#: Qué ejes ofrece cada prueba en el configurador de ensayo.
EJES_POR_PRUEBA: dict[Subject, set[str]] = {
    Subject.M1: {"numeros", "algebra", "geometria", "probabilidad"},
    Subject.M2: {"numeros", "algebra", "geometria", "probabilidad"},
    Subject.LECTORA: {"localizar", "interpretar", "evaluar"},
    Subject.CIENCIAS: {"biologia", "fisica", "quimica"},
    Subject.HISTORIA: {"historia", "ciudadania", "economia"},
}

SUBJECT_INCLUDES: dict[Subject, list[Subject]] = {
    Subject.M1: [Subject.M1],
    Subject.M2: [Subject.M1, Subject.M2],
    # Competencia Lectora no comparte banco con matemática.
    Subject.LECTORA: [Subject.LECTORA],
    Subject.CIENCIAS: [Subject.CIENCIAS],
    Subject.HISTORIA: [Subject.HISTORIA],
}


def _all_questions(db: Session, subject: Subject = Subject.M1) -> list[Question]:
    included = SUBJECT_INCLUDES[subject]
    stmt = (
        select(Question)
        .join(Question.skill_node)
        .where(SkillNode.subject.in_(included))
        .options(selectinload(Question.alternatives), selectinload(Question.skill_node))
        .order_by(Question.skill_node_id, Question.id)
    )
    return list(db.execute(stmt).scalars().all())


def get_options(db: Session, subject: Subject = Subject.M1) -> ExamOptionsOut:
    """Ejes disponibles y cuántas preguntas tiene el banco de cada uno."""
    questions = _all_questions(db, subject)
    counts: dict[str, int] = defaultdict(int)
    for q in questions:
        counts[q.skill_node.axis.value] += 1

    # Solo los ejes que esta prueba usa. Matemática y Competencia Lectora
    # comparten el enum de ejes, así que sin filtrar el configurador de un
    # ensayo de lectura mostraría "Números (0)" y el de matemática mostraría
    # "Localizar (0)".
    axes = [
        AxisOptionOut(axis=axis, label=label, available=counts.get(axis, 0))
        for axis, label in AXIS_LABELS.items()
        if axis in EJES_POR_PRUEBA[subject]
    ]
    return ExamOptionsOut(
        subject=subject,
        axes=axes,
        total_available=len(questions),
        seconds_per_question=scoring.segundos_por_pregunta(subject),
        official_questions=scoring.SCORING_BY_SUBJECT[subject].preguntas_oficiales,
        official_duration_min=scoring.SCORING_BY_SUBJECT[subject].duracion_oficial_min,
    )


def get_repaso(db: Session, user_id: int, subject: Subject = Subject.M1) -> RepasoOut:
    """Sugerencia para "Ensayo de repaso": los ejes de los 2 nodos con peor
    accuracy entre los que el usuario ya intento, reusando el mismo progreso
    que alimenta el Arbol de Habilidades (no es un calculo nuevo).

    Nota: hoy siempre mira el progreso de M1 (el Árbol de Habilidades solo
    tiene UI para esa prueba), incluso si el ensayo que se va a rendir es M2.
    """
    tree = skill_tree_service.get_user_skill_tree(db, user_id, subject)
    attempted = [n for n in tree if n.attempts > 0]
    if not attempted:
        return RepasoOut(has_data=False, axes=[], axis_labels=[])

    weakest = sorted(attempted, key=lambda n: n.accuracy)[:2]
    axes: list[str] = []
    for node in weakest:
        if node.axis.value not in axes:
            axes.append(node.axis.value)

    return RepasoOut(
        has_data=True,
        axes=axes,
        axis_labels=[AXIS_LABELS[a] for a in axes],
    )


def duration_for(question_count: int, pace: Pace, subject: Subject = Subject.M1) -> int:
    """Duración en segundos, proporcional a la razón oficial de la prueba."""
    return round(
        scoring.segundos_por_pregunta(subject) * question_count * PACE_FACTOR[pace]
    )


def _select_questions(
    pool: list[Question], axes: list[str], count: int
) -> list[Question]:
    """Reparte la cantidad pedida proporcionalmente entre los ejes.

    Un muestreo puramente aleatorio puede dejar un eje sin representación en
    ensayos cortos. Aquí se reparte en proporción al tamaño del banco de cada
    eje y recién dentro de cada eje se elige al azar, de modo que un ensayo de
    20 preguntas siempre toca todos los ejes pedidos.
    """
    available = [q for q in pool if not axes or q.skill_node.axis.value in axes]
    if len(available) <= count:
        random.shuffle(available)
        return available

    by_axis: dict[str, list[Question]] = defaultdict(list)
    for q in available:
        by_axis[q.skill_node.axis.value].append(q)

    total = len(available)
    quota = {axis: int(len(group) / total * count) for axis, group in by_axis.items()}
    assigned = sum(quota.values())

    # Las plazas sobrantes por el redondeo van a los ejes con más banco.
    ranked = sorted(by_axis, key=lambda a: len(by_axis[a]), reverse=True)
    i = 0
    while assigned < count and ranked:
        axis = ranked[i % len(ranked)]
        if quota[axis] < len(by_axis[axis]):
            quota[axis] += 1
            assigned += 1
        i += 1
        if i > len(ranked) * count + len(ranked):
            break  # Salvaguarda: ningún eje admite más preguntas.

    chosen: list[Question] = []
    for axis, group in by_axis.items():
        chosen.extend(random.sample(group, quota[axis]))

    random.shuffle(chosen)
    return chosen


def start_attempt(db: Session, user: User, config: ExamConfigIn) -> ExamAttempt:
    pool = _all_questions(db, config.subject)
    valid_axes = [a for a in config.axes if a in AXIS_LABELS]
    chosen = _select_questions(pool, valid_axes, config.question_count)

    attempt = ExamAttempt(
        user_id=user.id,
        pace=config.pace,
        subject=config.subject,
        axes=",".join(valid_axes) or None,
        duration_limit_seconds=duration_for(len(chosen), config.pace, config.subject),
    )
    db.add(attempt)
    db.flush()  # necesita el id del intento para las filas de preguntas

    db.add_all(
        ExamAttemptQuestion(attempt_id=attempt.id, question_id=q.id, position=i)
        for i, q in enumerate(chosen)
    )
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int) -> ExamAttempt | None:
    return db.get(ExamAttempt, attempt_id)


def attempt_questions(db: Session, attempt: ExamAttempt) -> list[Question]:
    """Preguntas del intento en su orden asignado.

    Los intentos creados antes de que existiera `exam_attempt_questions` no
    tienen set persistido; para esos se cae al comportamiento antiguo (todas
    las preguntas del subject del intento), que es exactamente el ensayo que
    rindieron (esos intentos son todos de antes de que existiera M2).
    """
    rows = (
        db.execute(
            select(ExamAttemptQuestion)
            .where(ExamAttemptQuestion.attempt_id == attempt.id)
            .order_by(ExamAttemptQuestion.position)
        )
        .scalars()
        .all()
    )
    if not rows:
        return _all_questions(db, attempt.subject)

    # Se buscan por id directo (no por `_all_questions`, que filtra por
    # subject): el set ya quedó fijado al crear el intento, así que da igual
    # el subject actual, solo interesan esas preguntas puntuales.
    question_ids = [r.question_id for r in rows]
    stmt = (
        select(Question)
        .where(Question.id.in_(question_ids))
        .options(selectinload(Question.alternatives), selectinload(Question.skill_node))
    )
    by_id = {q.id: q for q in db.execute(stmt).scalars().all()}
    return [by_id[r.question_id] for r in rows if r.question_id in by_id]


def attempt_config(attempt: ExamAttempt, question_count: int) -> ExamConfigOut:
    return ExamConfigOut(
        subject=attempt.subject,
        question_count=question_count,
        pace=attempt.pace,
        axes=attempt.axes.split(",") if attempt.axes else [],
    )


def get_answers_map(db: Session, attempt_id: int) -> dict[int, ExamAnswerState]:
    rows = db.execute(
        select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    ).scalars()
    return {
        r.question_id: ExamAnswerState(
            selected_alternative_id=r.selected_alternative_id,
            time_spent_ms=r.time_spent_ms,
            flagged=r.flagged,
        )
        for r in rows
    }


def upsert_answer(db: Session, attempt_id: int, payload: ExamAnswerIn) -> None:
    existing = db.execute(
        select(ExamAnswer).where(
            ExamAnswer.attempt_id == attempt_id,
            ExamAnswer.question_id == payload.question_id,
        )
    ).scalar_one_or_none()
    now = datetime.now(UTC)
    if existing is not None:
        existing.selected_alternative_id = payload.selected_alternative_id
        existing.time_spent_ms = payload.time_spent_ms
        existing.flagged = payload.flagged
        existing.answered_at = now
    else:
        db.add(
            ExamAnswer(
                attempt_id=attempt_id,
                question_id=payload.question_id,
                selected_alternative_id=payload.selected_alternative_id,
                time_spent_ms=payload.time_spent_ms,
                flagged=payload.flagged,
                answered_at=now,
            )
        )
    db.commit()


def _correct_alternative_ids(db: Session, questions: list[Question]) -> set[int]:
    return {a.id for q in questions for a in q.alternatives if a.is_correct}


def _tally(
    questions: list[Question],
    answers: dict[int, ExamAnswerState],
    correct_ids: set[int],
    key,
) -> list[BreakdownItemOut]:
    """Agrupa el desempeño según un criterio (eje, nodo o dificultad)."""
    groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"correct": 0, "incorrect": 0, "omitted": 0, "total": 0}
    )
    for q in questions:
        item = groups[key(q)]
        selected = answers.get(q.id)
        selected_id = selected.selected_alternative_id if selected else None
        if selected_id is None:
            item["omitted"] += 1
        elif selected_id in correct_ids:
            item["correct"] += 1
        else:
            item["incorrect"] += 1
        item["total"] += 1

    return sorted(
        (
            BreakdownItemOut(
                name=name,
                correct=v["correct"],
                incorrect=v["incorrect"],
                omitted=v["omitted"],
                total=v["total"],
                percentage=round(v["correct"] / v["total"] * 100) if v["total"] else 0,
            )
            for name, v in groups.items()
        ),
        key=lambda b: b.name,
    )


def _elapsed_seconds(attempt: ExamAttempt) -> int:
    end = attempt.finished_at or datetime.now(UTC)
    elapsed = int((end - attempt.started_at).total_seconds())
    return max(0, min(elapsed, attempt.duration_limit_seconds))


def submit_attempt(db: Session, attempt: ExamAttempt) -> ExamResultOut:
    questions = attempt_questions(db, attempt)
    answers = get_answers_map(db, attempt.id)
    correct_ids = _correct_alternative_ids(db, questions)

    correct = incorrect = omitted = 0
    for q in questions:
        state = answers.get(q.id)
        selected_id = state.selected_alternative_id if state else None
        if selected_id is None:
            omitted += 1
        elif selected_id in correct_ids:
            correct += 1
        else:
            incorrect += 1

    score = scoring.estimar_puntaje(correct, len(questions), attempt.subject)

    if attempt.status == AttemptStatus.IN_PROGRESS:
        attempt.status = AttemptStatus.SUBMITTED
        attempt.finished_at = datetime.now(UTC)
        attempt.estimated_score = score
        db.commit()
        db.refresh(attempt)
        # El árbol de habilidades se alimenta del resultado del ensayo.
        skill_tree_service.apply_attempt_results(db, attempt.user_id, attempt.id)

    return ExamResultOut(
        attempt_id=attempt.id,
        status=attempt.status,
        total_questions=len(questions),
        answered=correct + incorrect,
        correct=correct,
        incorrect=incorrect,
        omitted=omitted,
        estimated_score=attempt.estimated_score or score,
        elapsed_seconds=_elapsed_seconds(attempt),
        duration_limit_seconds=attempt.duration_limit_seconds,
        by_axis=_tally(
            questions, answers, correct_ids, lambda q: AXIS_LABELS[q.skill_node.axis.value]
        ),
        by_difficulty=_tally(
            questions,
            answers,
            correct_ids,
            lambda q: DIFFICULTY_LABELS[q.difficulty.value],
        ),
        by_node=_tally(questions, answers, correct_ids, lambda q: q.skill_node.name),
    )


def list_attempts(db: Session, user: User) -> list[ExamAttemptSummary]:
    attempts = (
        db.execute(
            select(ExamAttempt)
            .where(ExamAttempt.user_id == user.id)
            .order_by(ExamAttempt.started_at.desc())
        )
        .scalars()
        .all()
    )

    out = []
    for a in attempts:
        questions = attempt_questions(db, a)
        answers = get_answers_map(db, a.id)
        correct_ids = _correct_alternative_ids(db, questions)
        correct = sum(
            1
            for q in questions
            if (s := answers.get(q.id))
            and s.selected_alternative_id is not None
            and s.selected_alternative_id in correct_ids
        )
        answered = sum(
            1 for s in answers.values() if s.selected_alternative_id is not None
        )
        # Los intentos anteriores a esta versión no guardaron puntaje; se estima
        # al vuelo para que el historial y su gráfico no queden con huecos.
        score = a.estimated_score
        if score is None and a.status == AttemptStatus.SUBMITTED:
            score = scoring.estimar_puntaje(correct, len(questions), a.subject)
        out.append(
            ExamAttemptSummary(
                attempt_id=a.id,
                started_at=a.started_at,
                finished_at=a.finished_at,
                status=a.status,
                subject=a.subject,
                total_questions=len(questions),
                answered=answered,
                correct=correct,
                estimated_score=score,
                elapsed_seconds=_elapsed_seconds(a),
                duration_limit_seconds=a.duration_limit_seconds,
                pace=a.pace,
                axes=a.axes.split(",") if a.axes else [],
            )
        )
    return out


def delete_attempt(db: Session, attempt: ExamAttempt) -> None:
    """Borra un intento del historial, junto con sus respuestas y su set."""
    db.execute(delete(ExamAnswer).where(ExamAnswer.attempt_id == attempt.id))
    db.execute(
        delete(ExamAttemptQuestion).where(ExamAttemptQuestion.attempt_id == attempt.id)
    )
    db.delete(attempt)
    db.commit()


def get_review(db: Session, attempt: ExamAttempt) -> ExamReviewOut:
    questions = attempt_questions(db, attempt)
    answers = get_answers_map(db, attempt.id)

    node_ids = {q.skill_node_id for q in questions}
    nodes = (
        db.execute(select(SkillNode).where(SkillNode.id.in_(node_ids))).scalars().all()
    )
    node_by_id = {n.id: n for n in nodes}

    review_questions: list[ReviewQuestionOut] = []
    node_stats: dict[int, dict[str, int]] = {}

    for q in questions:
        ans = answers.get(q.id)
        selected_id = ans.selected_alternative_id if ans else None
        time_spent = ans.time_spent_ms if ans else 0
        correct_alt = next((a for a in q.alternatives if a.is_correct), None)

        answered_correctly = None
        if selected_id is not None:
            answered_correctly = correct_alt is not None and selected_id == correct_alt.id

        stats = node_stats.setdefault(q.skill_node_id, {"total": 0, "correct": 0})
        stats["total"] += 1
        if answered_correctly:
            stats["correct"] += 1

        node = node_by_id.get(q.skill_node_id)
        review_questions.append(
            ReviewQuestionOut(
                id=q.id,
                stem=q.stem,
                explanation=q.explanation,
                difficulty=q.difficulty,
                skill_node_id=q.skill_node_id,
                skill_node_code=node.code if node else "",
                skill_node_name=node.name if node else "",
                axis=AXIS_LABELS.get(node.axis.value, "") if node else "",
                time_spent_ms=time_spent,
                answered_correctly=answered_correctly,
                alternatives=[
                    ReviewAlternativeOut(
                        id=a.id,
                        label=a.label,
                        text=a.text,
                        is_correct=a.is_correct,
                        distractor_justification=a.distractor_justification,
                        selected=(a.id == selected_id),
                    )
                    for a in q.alternatives
                ],
            )
        )

    node_diagnosis = [
        NodeDiagnosisOut(
            skill_node_id=nid,
            skill_node_code=node_by_id[nid].code,
            skill_node_name=node_by_id[nid].name,
            axis=node_by_id[nid].axis.value,
            total=s["total"],
            correct=s["correct"],
            accuracy=(s["correct"] / s["total"] if s["total"] else 0.0),
        )
        for nid, s in node_stats.items()
        if nid in node_by_id
    ]
    node_diagnosis.sort(key=lambda d: d.accuracy)

    return ExamReviewOut(
        attempt_id=attempt.id,
        status=attempt.status,
        questions=review_questions,
        node_diagnosis=node_diagnosis,
    )
