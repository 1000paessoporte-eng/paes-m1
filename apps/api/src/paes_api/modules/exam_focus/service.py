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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from paes_api.modules.content.models import Alternative, Difficulty, Question
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
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree import service as skill_tree_service
from paes_api.modules.skill_tree.models import (
    AXIS_LABELS,
    SkillAxis,
    SkillNode,
    Subject,
)
from paes_api.modules.users.models import User

DIFFICULTY_LABELS = {"facil": "Fácil", "medio": "Medio", "dificil": "Difícil"}

#: Cuántas UNIDADES TEMÁTICAS oficiales tiene cada eje del temario PAES 2027.
#: De aquí sale el reparto del ensayo, y no del tamaño del banco.
#:
#: El temario lista para M1: Números con 3 unidades (enteros y racionales,
#: porcentaje, potencias y raíces); Álgebra y Funciones con 6 (expresiones
#: algebraicas, proporcionalidad, ecuaciones e inecuaciones de primer grado,
#: sistemas 2x2, función lineal y afín, función cuadrática); Geometría con 4
#: (figuras geométricas, cuerpos geométricos, transformaciones isométricas,
#: semejanza); y Probabilidad y Estadística con 3 (representación de datos,
#: medidas de posición, reglas de las probabilidades).
#:
#: Repartir por tamaño de banco daba Geometría 31% y Probabilidad 13%, porque
#: "figuras geométricas" se abrió en dos nodos (Pitágoras y áreas) y en cambio
#: un solo nodo cubre dos unidades de estadística. Contar unidades corrige las
#: dos distorsiones y, sobre todo, deja el reparto declarado en vez de
#: emergente: hoy da 19% / 37% / 25% / 19%.
UNIDADES_POR_EJE: dict[Subject, dict[str, int]] = {
    Subject.M1: {
        SkillAxis.NUMEROS.value: 3,
        SkillAxis.ALGEBRA.value: 6,
        SkillAxis.GEOMETRIA.value: 4,
        SkillAxis.PROBABILIDAD.value: 3,
    },
    #: Unidades PROPIAS de M2, sin contar las de M1 que también evalúa.
    #: Números: reales, matemática financiera y logaritmos. Álgebra: casos de
    #: sistemas 2x2, función potencia/exponencial/logarítmica y funciones
    #: trigonométricas. Geometría: homotecia, razones trigonométricas,
    #: relaciones métricas en la circunferencia, esfera y rectas en el plano.
    #: Probabilidad: dispersión, condicional, permutación y combinatoria, y
    #: modelos probabilísticos.
    Subject.M2: {
        SkillAxis.NUMEROS.value: 3,
        SkillAxis.ALGEBRA.value: 3,
        SkillAxis.GEOMETRIA.value: 5,
        SkillAxis.PROBABILIDAD.value: 4,
    },
}


def _unidades(subject: Subject, axis: str) -> int:
    """Unidades temáticas que el temario de `subject` asigna a ese eje."""
    return UNIDADES_POR_EJE.get(subject, {}).get(axis, 1)

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


#: Mínimo de preguntas que justifica montar un texto largo en el ensayo.
#: Bajo esto conviene dejar el texto fuera antes que pedirle al alumno leer mil
#: palabras para responder dos preguntas. La prueba oficial nunca baja de 7.
MINIMO_POR_TEXTO = 6

#: Preguntas por texto a las que apunta el reparto. Sale de medir las pruebas
#: oficiales: 65 preguntas repartidas en 7 u 8 lecturas, o sea entre 7 y 11 por
#: texto, con un promedio cercano a nueve.
OBJETIVO_POR_TEXTO = 9

#: Cuántos ensayos de lectura hacia atrás se miran para no repetir un texto.
#:
#: Un texto de Competencia Lectora son novecientas palabras: volver a leerlo en
#: el ensayo siguiente no entrena nada, porque el alumno ya sabe lo que dice y
#: responde de memoria en vez de leer. Con esta ventana, un texto que acaba de
#: salir queda al final de la fila y va subiendo a medida que pasan los
#: ensayos, hasta recuperar su prioridad normal al quinto.
#:
#: Cinco es el número que hace que el turno completo tenga sentido con el banco
#: actual: 67 textos y siete por ensayo alcanzan para nueve ensayos seguidos
#: sin repetir ninguno, así que la ventana nunca deja al armador sin material.
VENTANA_SIN_REPETIR = 5


def _textos_recientes(db: Session, user_id: int) -> dict[int, int]:
    """Qué textos vio el estudiante y hace cuántos ensayos.

    Devuelve `passage_id -> antigüedad`, donde 1 es el ensayo más reciente.
    Los intentos se cuentan aunque hayan quedado abandonados: el texto se
    mostró igual, que es lo único que importa acá.
    """
    filas = db.execute(
        select(ExamAttempt.id, Question.passage_id)
        .join(ExamAttemptQuestion, ExamAttemptQuestion.attempt_id == ExamAttempt.id)
        .join(Question, Question.id == ExamAttemptQuestion.question_id)
        .where(
            ExamAttempt.user_id == user_id,
            ExamAttempt.subject == Subject.LECTORA,
            Question.passage_id.is_not(None),
        )
        .order_by(ExamAttempt.started_at.desc())
    ).all()

    antiguedad: dict[int, int] = {}
    intentos: list[int] = []
    for attempt_id, passage_id in filas:
        if attempt_id not in intentos:
            if len(intentos) == VENTANA_SIN_REPETIR:
                break
            intentos.append(attempt_id)
        # Si un texto salió en dos ensayos, manda el más reciente, que es el
        # primero que aparece en este recorrido.
        antiguedad.setdefault(passage_id, len(intentos))
    return antiguedad


def _cuotas(total: int, partes: int) -> list[int]:
    """Reparte `total` entre `partes` lo más parejo posible.

    El sobrante del redondeo se entrega de a uno a los primeros, de modo que
    las cuotas nunca difieren en más de una pregunta entre sí.
    """
    base, resto = divmod(total, partes)
    return [base + (1 if i < resto else 0) for i in range(partes)]


def _seleccionar_por_texto(
    pool: list[Question],
    count: int,
    recientes: dict[int, int] | None = None,
) -> list[Question]:
    """Arma un ensayo de lectura repartiendo las preguntas entre varios TEXTOS.

    Devuelve las preguntas ya agrupadas por texto y en ese orden: el cliente
    las pagina tal cual las recibe, un texto por página con sus preguntas
    debajo, que es como se rinde la prueba de papel.

    El reparto imita la estructura oficial: 65 preguntas en 7 u 8 lecturas, con
    entre 7 y 11 preguntas cada una. Por eso primero se decide CUÁNTOS textos
    entran —apuntando a `OBJETIVO_POR_TEXTO` preguntas por texto— y recién
    después se toma de cada uno el subconjunto que le toca.

    Antes se tomaban textos enteros hasta que faltaran menos de
    `MINIMO_POR_TEXTO` preguntas, y ahí el ensayo se cerraba corto: con textos
    de nueve y once preguntas, pedir 65 entregaba entre 60 y 65 —y solo un
    cuarto de las veces las 65— repartidas en 6 lecturas en vez de 7 u 8.
    """
    por_texto: dict[int, list[Question]] = defaultdict(list)
    sueltas: list[Question] = []
    for q in pool:
        if q.passage_id is None:
            sueltas.append(q)
        else:
            por_texto[q.passage_id].append(q)

    claves = list(por_texto)
    random.shuffle(claves)

    # Los textos que el estudiante acaba de leer van al final de la fila.
    #
    # No es una exclusión sino una postergación, y esa diferencia importa: si
    # el banco no alcanzara —un alumno que rinde muchos ensayos seguidos, o un
    # banco chico—, el armador igual arma el ensayo, empezando por los textos
    # más antiguos. Una exclusión dura, en cambio, lo dejaría sin material.
    #
    # La penalización baja sola con el tiempo: el texto del ensayo anterior
    # pesa 4, el de dos ensayos atrás pesa 3, y al quinto vuelve a valer lo
    # mismo que uno que nunca salió. `sorted` es estable, así que dentro de
    # cada tramo se conserva el orden aleatorio del shuffle de arriba.
    if recientes:
        claves.sort(key=lambda c: max(0, VENTANA_SIN_REPETIR - recientes.get(c, 99)))

    # La prueba oficial siempre trae al menos un texto literario, y el temario
    # dedica trece conocimientos exclusivos a ese tipo de lectura. Se adelanta
    # uno al comienzo de la fila para que ningún ensayo se quede sin él.
    #
    # Esta regla TIENE PRECEDENCIA sobre el enfriamiento de arriba: si todos
    # los literarios del banco salieron hace poco, igual entra uno repetido
    # antes que dejar el ensayo sin literario. Como la lista ya viene ordenada
    # por antigüedad, el que se adelanta es el literario menos reciente, así
    # que el choque solo ocurre cuando no queda alternativa. Con el banco real
    # —trece literarios de sesenta y siete— no ocurre.
    literarias = [
        c for c in claves
        if (por_texto[c][0].passage is not None
            and por_texto[c][0].passage.kind == "literario")
    ]
    if literarias:
        primera = literarias[0]
        claves.remove(primera)
        claves.insert(0, primera)

    # Se barajan las preguntas DENTRO de cada texto para que dos ensayos con el
    # mismo texto no traigan siempre las mismas; el orden entre textos ya quedó
    # fijado arriba.
    grupos = {c: list(por_texto[c]) for c in claves}
    for grupo in grupos.values():
        random.shuffle(grupo)

    # Cuántos textos entran. Se apunta al promedio oficial y se acota por los
    # textos disponibles y por el mínimo que justifica montar una lectura.
    if not claves:
        cuantos = 0
    else:
        cuantos = max(1, round(count / OBJETIVO_POR_TEXTO))
        cuantos = min(cuantos, len(claves), max(1, count // MINIMO_POR_TEXTO))

    # Los textos del banco no traen todos la misma cantidad de preguntas, así
    # que el promedio no basta: hay que comprobar que los textos elegidos
    # ALCANCEN para lo pedido. Con lecturas de nueve preguntas, siete textos
    # llegan a 63 y no a 65, y el ensayo salía corto por eso. Mientras la
    # capacidad no cubra el total, entra un texto más.
    while cuantos < len(claves) and sum(len(grupos[c]) for c in claves[:cuantos]) < count:
        cuantos += 1

    elegidos = list(claves[:cuantos])
    reserva = list(claves[cuantos:])

    tomado: dict[int, int] = dict(zip(elegidos, _cuotas(count, cuantos))) if cuantos else {}

    # Un texto no puede aportar más preguntas de las que tiene. Lo que quede
    # sin cubrir se reparte entre los textos que todavía tengan de sobra, y si
    # aun así falta, entra un texto más de la fila.
    for clave in elegidos:
        tomado[clave] = min(tomado[clave], len(grupos[clave]))

    def _faltante() -> int:
        return count - sum(tomado.values())

    for clave in elegidos:
        if _faltante() <= 0:
            break
        libre = len(grupos[clave]) - tomado[clave]
        tomado[clave] += min(libre, _faltante())

    for clave in list(reserva):
        falta = _faltante()
        if falta < MINIMO_POR_TEXTO:
            break
        elegidos.append(clave)
        tomado[clave] = min(falta, len(grupos[clave]))

    elegidas: list[Question] = []
    for clave in elegidos:
        elegidas.extend(grupos[clave][: tomado[clave]])

    # Las preguntas sin texto asociado solo se usan para completar, y nunca
    # deberían existir en esta prueba: una pregunta de lectura sin lectura no
    # se puede responder. El verificador del banco ya lo prohíbe.
    if len(elegidas) < count and sueltas:
        random.shuffle(sueltas)
        elegidas.extend(sueltas[: count - len(elegidas)])
    return elegidas


def _select_questions(
    pool: list[Question],
    axes: list[str],
    count: int,
    subject: Subject = Subject.M1,
    recientes: dict[int, int] | None = None,
) -> list[Question]:
    """Reparte la cantidad pedida entre los ejes según el temario oficial.

    Un muestreo puramente aleatorio puede dejar un eje sin representación en
    ensayos cortos. Aquí se reparte primero por eje y recién dentro de cada eje
    se elige al azar, de modo que un ensayo de 20 preguntas siempre toca todos
    los ejes pedidos.

    El peso de cada eje sale de UNIDADES_POR_EJE, o sea de cuántas unidades
    temáticas le asigna el temario. Antes salía del tamaño del banco, y eso
    tenía dos problemas: sobrerrepresentaba Geometría (5 nodos para 4 unidades)
    y subrepresentaba Probabilidad (2 nodos para 3 unidades), y además el
    reparto se movía solo cada vez que el banco crecía.

    Cuando una prueba evalúa el temario de otra —M2 evalúa todo M1 además de lo
    suyo— el peso del eje suma las unidades de ambas, y dentro del eje la cuota
    se reparte entre las dos en la misma proporción. Sin eso, el reparto volvía
    a depender del tamaño del banco por la puerta de atrás: M1 tiene cinco veces
    más preguntas que M2, así que un ensayo de M2 traía 56 de M1 y 9 propias.
    """
    # Competencia Lectora no se reparte por eje: se reparte por texto.
    if subject is Subject.LECTORA:
        return _seleccionar_por_texto(pool, count, recientes)
    available = [q for q in pool if not axes or q.skill_node.axis.value in axes]
    if len(available) <= count:
        random.shuffle(available)
        return available

    by_axis: dict[str, list[Question]] = defaultdict(list)
    for q in available:
        by_axis[q.skill_node.axis.value].append(q)

    # Los ejes sin peso declarado (Lectora, Ciencias, Historia) se reparten
    # parejo entre sí: su temario no se organiza por unidades comparables.

    incluidas = SUBJECT_INCLUDES[subject]
    pesos = {
        axis: sum(_unidades(s, axis) for s in incluidas) for axis in by_axis
    }
    total_peso = sum(pesos.values())
    quota = {
        axis: min(int(pesos[axis] / total_peso * count), len(group))
        for axis, group in by_axis.items()
    }
    assigned = sum(quota.values())

    # Las plazas sobrantes por el redondeo van a los ejes de mayor peso.
    ranked = sorted(by_axis, key=lambda a: pesos[a], reverse=True)
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
        chosen.extend(
            _repartir_por_prueba(group, quota[axis], axis, incluidas)
        )

    random.shuffle(chosen)
    return chosen


def _repartir_por_prueba(
    grupo: list[Question], cuantas: int, axis: str, incluidas: list[Subject]
) -> list[Question]:
    """Dentro de un eje, reparte la cuota entre las pruebas que lo alimentan.

    Solo hace algo cuando una prueba evalúa el temario de otra. Para M1, que se
    alimenta únicamente de sí misma, devuelve el reparto por dificultad de
    siempre.
    """
    if len(incluidas) < 2:
        return _repartir_por_dificultad(grupo, cuantas)

    por_prueba: dict[Subject, list[Question]] = defaultdict(list)
    for q in grupo:
        por_prueba[q.skill_node.subject].append(q)

    presentes = [s for s in incluidas if por_prueba[s]]
    if len(presentes) < 2:
        return _repartir_por_dificultad(grupo, cuantas)

    pesos = {s: _unidades(s, axis) for s in presentes}
    total = sum(pesos.values())
    cupos = {
        s: min(round(pesos[s] / total * cuantas), len(por_prueba[s]))
        for s in presentes
    }
    # El redondeo puede dejar plazas sueltas: van a la prueba de mayor peso que
    # todavía tenga banco disponible.
    for s in sorted(presentes, key=lambda x: pesos[x], reverse=True):
        falta = cuantas - sum(cupos.values())
        if falta <= 0:
            break
        cupos[s] = min(cupos[s] + falta, len(por_prueba[s]))

    elegidas: list[Question] = []
    for s in presentes:
        elegidas.extend(_repartir_por_dificultad(por_prueba[s], cupos[s]))
    return elegidas


def _repartir_por_dificultad(grupo: list[Question], cuantas: int) -> list[Question]:
    """Elige `cuantas` preguntas del grupo con las tres dificultades presentes.

    Elegir al azar dentro del eje da el reparto correcto en promedio, pero un
    ensayo concreto puede salir muy desviado: en 20 preguntas es posible sacar
    12 fáciles y 3 difíciles. Como el ensayo se usa para estimar puntaje, esa
    variación cambia el resultado sin que el estudiante haya cambiado.

    El reparto es parejo entre las tres, que es como está construido el banco.
    Si una dificultad no alcanza a llenar su cuota, lo que falta se completa
    con el resto del grupo.
    """
    if cuantas >= len(grupo):
        return list(grupo)

    por_dificultad: dict[str, list[Question]] = defaultdict(list)
    for q in grupo:
        por_dificultad[q.difficulty.value].append(q)

    niveles = [n for n in ("facil", "medio", "dificil") if por_dificultad[n]]
    if not niveles:
        return random.sample(grupo, cuantas)

    elegidas: list[Question] = []
    base, resto = divmod(cuantas, len(niveles))
    # El sobrante del redondeo se reparte empezando por las de dificultad media,
    # que es la franja más poblada de una prueba real.
    orden = sorted(niveles, key=lambda n: ("medio", "facil", "dificil").index(n))
    for i, nivel in enumerate(orden):
        cupo = min(base + (1 if i < resto else 0), len(por_dificultad[nivel]))
        elegidas.extend(random.sample(por_dificultad[nivel], cupo))

    # Si alguna dificultad no tenía suficientes, se completa con lo que sobre.
    if len(elegidas) < cuantas:
        ya = {id(q) for q in elegidas}
        sobrantes = [q for q in grupo if id(q) not in ya]
        elegidas.extend(random.sample(sobrantes, cuantas - len(elegidas)))

    return elegidas


def start_attempt(db: Session, user: User, config: ExamConfigIn) -> ExamAttempt:
    pool = _all_questions(db, config.subject)
    valid_axes = [a for a in config.axes if a in AXIS_LABELS]
    # Solo Lectora usa el historial: es la única prueba donde repetir cuesta
    # novecientas palabras de lectura ya conocida.
    recientes = (
        _textos_recientes(db, user.id)
        if config.subject is Subject.LECTORA
        else None
    )
    chosen = _select_questions(
        pool, valid_axes, config.question_count, config.subject, recientes
    )

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
    """Guarda o actualiza la respuesta de una pregunta dentro del intento.

    Esto se llama MUCHO: cada vez que el alumno marca una alternativa, la
    cambia, marca la pregunta para revisar o navega. En un teléfono con red
    lenta las peticiones se solapan, y dos guardados de la misma pregunta
    llegaban a la vez.

    Antes era leer-comprobar-insertar sin nada que lo impidiera, y la carrera
    dejaba DOS filas para la misma pregunta. A partir de ahí la lectura de la
    siguiente llamada encontraba dos y reventaba, así que esa pregunta quedaba
    inservible por el resto del ensayo y terminaba contada como omitida aunque
    el alumno la hubiera respondido. Un ensayo de prueba llegó a 28 fallos de
    113 guardados.

    Ahora la base impide el duplicado y el insert que pierde la carrera se
    reintenta como actualización, que es lo que el segundo guardado quería
    hacer desde el principio.
    """
    now = datetime.now(UTC)

    def _actualizar() -> bool:
        fila = db.execute(
            select(ExamAnswer).where(
                ExamAnswer.attempt_id == attempt_id,
                ExamAnswer.question_id == payload.question_id,
            )
        ).scalar_one_or_none()
        if fila is None:
            return False
        fila.selected_alternative_id = payload.selected_alternative_id
        fila.time_spent_ms = payload.time_spent_ms
        fila.flagged = payload.flagged
        fila.answered_at = now
        db.commit()
        return True

    if _actualizar():
        return

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
    try:
        db.commit()
    except IntegrityError:
        # Otro guardado de la misma pregunta llegó primero. No es un error que
        # el alumno tenga que ver: su respuesta es la más reciente y es la que
        # tiene que quedar, así que se aplica encima de la fila que ganó.
        db.rollback()
        if not _actualizar():
            raise


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


#: Cuánto pesa cada dificultad al repartir el tiempo del ensayo.
#:
#: No son minutos: son PESOS RELATIVOS. El total que se reparte sigue siendo el
#: tiempo real del intento --el oficial del DEMRE, o el que eligió el alumno si
#: pidió ritmo exigente o relajado--, así que esto no inventa tiempo, lo
#: distribuye. La suma de los tiempos sugeridos es exactamente la duración del
#: ensayo, y hay un test que lo fija.
#:
#: Dividir en partes iguales trataba igual una pregunta de operatoria directa
#: que una de geometría con figura, y esa es justamente la decisión que un
#: alumno tiene que aprender a tomar dentro de la prueba.
PESO_DIFICULTAD: dict[Difficulty, float] = {
    Difficulty.FACIL: 0.75,
    Difficulty.MEDIO: 1.0,
    Difficulty.DIFICIL: 1.4,
}

#: Palabras por minuto de lectura atenta que se asumen para los textos de
#: Competencia Lectora.
#:
#: Es un SUPUESTO declarado, no un dato del DEMRE: sirve para repartir el
#: tiempo, no para prometer nada. Se eligió por lo bajo a propósito --leer un
#: texto para responderlo no es leerlo de corrido--, porque quedarse corto en
#: el presupuesto de lectura es el error que deja preguntas sin responder.
PALABRAS_POR_MINUTO = 180


def _peso_de(pregunta: Question, abre_pasaje: bool) -> float:
    """El peso de una pregunta al repartir el tiempo del ensayo.

    Dos cosas la hacen cara: la dificultad, y en Competencia Lectora, ser la
    PRIMERA de su texto. Esa carga con la lectura completa; las siguientes ya
    la tienen leída y solo vuelven a mirarla.
    """
    peso = PESO_DIFICULTAD.get(pregunta.difficulty, 1.0)
    if abre_pasaje and pregunta.passage is not None:
        palabras = len(pregunta.passage.body.split())
        # El peso extra se expresa en las mismas unidades: cuántas preguntas
        # "medias" cuesta leer ese texto.
        peso += (palabras / PALABRAS_POR_MINUTO) * 60 / scoring.segundos_por_pregunta()
    return peso


def tiempos_sugeridos(
    preguntas: list[Question], duracion_total_s: int
) -> dict[int, int]:
    """Cuántos segundos conviene dedicarle a cada pregunta del intento.

    Reparte el tiempo REAL del ensayo entre sus preguntas según lo que cuesta
    cada una. La suma da la duración del intento, así que el alumno que respeta
    todos los presupuestos termina justo a tiempo.

    Las preguntas de un mismo pasaje se detectan por orden: la primera que trae
    un pasaje nuevo es la que carga con leerlo.
    """
    if not preguntas or duracion_total_s <= 0:
        return {}

    vistos: set[int] = set()
    pesos: dict[int, float] = {}
    for q in preguntas:
        abre = q.passage_id is not None and q.passage_id not in vistos
        if q.passage_id is not None:
            vistos.add(q.passage_id)
        pesos[q.id] = _peso_de(q, abre)

    total_peso = sum(pesos.values())
    return {
        qid: max(1, round(duracion_total_s * peso / total_peso))
        for qid, peso in pesos.items()
    }


def preguntas_falladas_antes(
    db: Session, user_id: int, question_ids: list[int], excluir_intento: int
) -> set[int]:
    """De estas preguntas, cuáles el alumno ya respondió MAL alguna vez.

    Es el reemplazo del módulo de repaso: en vez de una cola aparte a la que
    hay que entrar, la señal aparece donde sirve, con la pregunta al frente.
    Con miles de preguntas sorteadas al azar, reencontrarse con una que uno
    falló es la mejor oportunidad de aprendizaje que da la plataforma, y hasta
    ahora pasaba desapercibida.

    "Alguna vez" y no "la última vez": lo que se le avisa al alumno es que en
    algún momento esta pregunta se le escapó. Si después la acertó, saberlo
    igual le sirve para no repetir el mismo razonamiento.

    Se EXCLUYE el intento en curso: dentro del mismo ensayo la pregunta se
    responde una sola vez, y marcarla con lo que acaba de contestar sería
    decirle la respuesta.

    Junta ensayo y práctica porque para el alumno son la misma pregunta.
    """
    if not question_ids:
        return set()

    falladas = set(
        db.execute(
            select(ExamAnswer.question_id)
            .join(ExamAttempt, ExamAttempt.id == ExamAnswer.attempt_id)
            .join(Alternative, Alternative.id == ExamAnswer.selected_alternative_id)
            .where(
                ExamAttempt.user_id == user_id,
                ExamAnswer.attempt_id != excluir_intento,
                ExamAnswer.question_id.in_(question_ids),
                Alternative.is_correct.is_(False),
            )
        )
        .scalars()
        .all()
    )

    falladas.update(
        db.execute(
            select(PracticeAnswer.question_id).where(
                PracticeAnswer.user_id == user_id,
                PracticeAnswer.question_id.in_(question_ids),
                PracticeAnswer.is_correct.is_(False),
            )
        )
        .scalars()
        .all()
    )
    return falladas
