"""Puntaje ponderado, lista de postulación y qué hacer con la brecha.

En Chile no se postula a una carrera: se postulan hasta diez en orden de
preferencia. La pregunta que importa no es "¿alcanzo para esta?" sino "¿hasta
qué preferencia alcanzo?", y de ahí sale todo lo demás: cuánto falta, a qué
ritmo se está avanzando, y qué conviene practicar esta semana.
"""

import unicodedata
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.goals.models import Carrera, MetaUsuario
from paes_api.modules.goals.schemas import (
    AporteOut,
    CarreraOut,
    MetaOut,
    NodoDebilOut,
    PlanSemanalOut,
    PostulacionOut,
    ProyeccionOut,
)
from paes_api.modules.skill_tree.models import (
    ProgressStatus,
    Subject,
    UserSkillProgress,
)
from paes_api.modules.users.models import User

#: Factor de la carrera -> (etiqueta, subject del ensayo). NEM y ranking no
#: tienen ensayo: los ingresa el estudiante.
FACTORES: dict[str, tuple[str, Subject | None]] = {
    "nem": ("Notas (NEM)", None),
    "ranking": ("Ranking de notas", None),
    "lectora": ("Competencia Lectora", Subject.LECTORA),
    "m1": ("Matemática M1", Subject.M1),
    "m2": ("Matemática M2", Subject.M2),
    "historia": ("Historia y Cs. Sociales", Subject.HISTORIA),
    "ciencias": ("Ciencias", Subject.CIENCIAS),
}

#: Fecha de la PAES regular del proceso de Admisión 2027 (DEMRE).
FECHA_PAES = datetime(2026, 11, 30, tzinfo=UTC)

MAX_PREFERENCIAS = 10

#: Días mínimos entre el primer y el último ensayo para hablar de tendencia.
MIN_DIAS_TENDENCIA = 7


def normalizar(texto: str) -> str:
    """Sin tildes y en minúsculas, para comparar como escribe la gente."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())


def buscar_carreras(
    db: Session,
    texto: str,
    limite: int = 20,
    region: str | None = None,
    comuna: str | None = None,
) -> list[Carrera]:
    """Busca por nombre, universidad o sede, ignorando tildes.

    Cada palabra se exige por separado: "enfermeria concepcion" encuentra la
    carrera aunque en el dato la universidad vaya antes que la sede.

    `region` y `comuna` acotan por ubicación y se pueden usar sin texto: filtrar
    "todas las carreras de la Región de Los Ríos" es una consulta legítima. Se
    comparan por igualdad con el valor tal como lo devuelve `ubicaciones`, que
    sale del mismo dato, así que no hace falta normalizarlos.
    """
    palabras = [p for p in normalizar(texto).split() if p]
    if not palabras and not region and not comuna:
        return []
    consulta = select(Carrera)
    for palabra in palabras:
        consulta = consulta.where(Carrera.busqueda.like(f"%{palabra}%"))
    if region:
        consulta = consulta.where(Carrera.region == region)
    if comuna:
        consulta = consulta.where(Carrera.comuna == comuna)
    return list(
        db.execute(consulta.order_by(Carrera.universidad, Carrera.nombre).limit(limite))
        .scalars()
        .all()
    )


def mejores_puntajes(db: Session, user_id: int) -> dict[Subject, int]:
    """El mejor puntaje logrado en cada prueba: lo que ya demostró que puede."""
    filas = db.execute(
        select(ExamAttempt.subject, ExamAttempt.estimated_score)
        .where(ExamAttempt.user_id == user_id)
        .where(ExamAttempt.status == "submitted")
        .where(ExamAttempt.estimated_score.is_not(None))
    ).all()
    mejores: dict[Subject, int] = {}
    for subject, puntaje in filas:
        if puntaje is not None and (subject not in mejores or puntaje > mejores[subject]):
            mejores[subject] = puntaje
    return mejores


def _evaluar(carrera: Carrera, puntajes: dict[Subject, int], user: User) -> dict:
    """Calcula el ponderado de una carrera y de dónde sale cada punto."""
    ignorar: set[str] = set()
    if carrera.electivo_alternativo:
        p_hist = puntajes.get(Subject.HISTORIA)
        p_cien = puntajes.get(Subject.CIENCIAS)
        if p_hist is None and p_cien is None:
            ignorar.add("ciencias")
        elif (p_cien or 0) >= (p_hist or 0):
            ignorar.add("historia")
        else:
            ignorar.add("ciencias")

    aportes: list[AporteOut] = []
    faltantes: list[str] = []
    total = 0.0
    completo = True

    for factor, (etiqueta, subject) in FACTORES.items():
        peso = getattr(carrera, factor) or 0.0
        if peso <= 0 or factor in ignorar:
            continue
        if subject is None:
            puntaje = user.puntaje_nem if factor == "nem" else user.puntaje_ranking
            origen = "ingresado" if puntaje else "falta"
        else:
            puntaje = puntajes.get(subject)
            origen = "ensayo" if puntaje else "falta"
        if puntaje is None:
            completo = False
            faltantes.append(etiqueta)
        aporte = (peso * (puntaje or 0)) / 100
        total += aporte
        aportes.append(
            AporteOut(
                factor=factor, etiqueta=etiqueta, ponderacion=peso, puntaje=puntaje,
                aporte=round(aporte, 1), por_cada_10=round(peso / 10, 1), origen=origen,
            )
        )

    # Dónde rinde más ESTUDIAR. NEM y ranking quedan fuera aunque suelan pesar
    # más: las notas del colegio ya están puestas y ninguna hora de estudio las
    # mueve, así que recomendarlas sería un consejo imposible de seguir.
    palanca, mejor_valor = None, -1.0
    for a in aportes:
        if FACTORES[a.factor][1] is None:
            continue
        valor = a.ponderacion * (1000 - (a.puntaje or 0))
        if valor > mejor_valor:
            mejor_valor, palanca = valor, a.etiqueta

    ponderado = round(total, 1) if completo else None
    minimo = carrera.ponderado_min
    brecha = round(minimo - ponderado, 1) if (ponderado is not None and minimo) else None

    return {
        "ponderado": ponderado,
        "brecha": brecha,
        "alcanza": (brecha <= 0) if brecha is not None else None,
        "aportes": aportes,
        "faltantes": faltantes,
        "mejor_palanca": palanca,
    }


def _proyeccion(db: Session, user_id: int) -> ProyeccionOut:
    """A qué ritmo viene mejorando, medido contra la fecha de la PAES.

    Se calcula sobre los ensayos de la prueba con más intentos: mezclar pruebas
    distintas produciría una tendencia que no significa nada. Con menos de tres
    ensayos no se informa ritmo: dos puntos son una recta, no una tendencia.
    """
    filas = db.execute(
        select(ExamAttempt.subject, ExamAttempt.estimated_score, ExamAttempt.finished_at)
        .where(ExamAttempt.user_id == user_id)
        .where(ExamAttempt.status == "submitted")
        .where(ExamAttempt.estimated_score.is_not(None))
        .where(ExamAttempt.finished_at.is_not(None))
        .order_by(ExamAttempt.finished_at)
    ).all()

    ahora = datetime.now(UTC)
    dias = max(0, (FECHA_PAES - ahora).days)

    por_prueba: dict[Subject, list[tuple[datetime, int]]] = {}
    for subject, puntaje, cuando in filas:
        por_prueba.setdefault(subject, []).append((cuando, puntaje))

    if not por_prueba:
        return ProyeccionOut(
            puntos_por_mes=None, ensayos_considerados=0, dias_para_paes=dias, proyectado=None
        )

    serie = max(por_prueba.values(), key=len)
    # Dos puntos son una recta, no una tendencia.
    if len(serie) < 3:
        return ProyeccionOut(
            puntos_por_mes=None, ensayos_considerados=len(serie),
            dias_para_paes=dias, proyectado=None,
        )

    (primer_dia, primer_puntaje), (ultimo_dia, ultimo_puntaje) = serie[0], serie[-1]
    dias_transcurridos = (ultimo_dia - primer_dia).days

    # Sin al menos una semana entre el primer y el último ensayo no hay ritmo
    # que medir: extrapolar un día a un mes multiplica el ruido por treinta y
    # produce cosas como "vienes bajando 2.760 puntos al mes", que es un
    # disparate con aspecto de dato.
    if dias_transcurridos < MIN_DIAS_TENDENCIA:
        return ProyeccionOut(
            puntos_por_mes=None, ensayos_considerados=len(serie),
            dias_para_paes=dias, proyectado=None,
        )

    por_mes = (ultimo_puntaje - primer_puntaje) / dias_transcurridos * 30

    proyectado = ultimo_puntaje + por_mes * (dias / 30)
    return ProyeccionOut(
        puntos_por_mes=round(por_mes, 1),
        ensayos_considerados=len(serie),
        dias_para_paes=dias,
        # El puntaje no pasa de 1000 ni baja de 100, por buena o mala que sea
        # la tendencia.
        proyectado=round(min(1000, max(100, proyectado)), 1),
    )


def _plan(db: Session, user_id: int, palanca: str | None) -> list[NodoDebilOut]:
    """Los nodos más débiles de la prueba donde conviene mejorar.

    Convierte "tu palanca es M1" en algo que se puede hacer hoy: los temas
    concretos, ordenados por lo que peor rinde, con su lección si existe.
    """
    if palanca is None:
        return []
    subject = next((s for _, (etiqueta, s) in FACTORES.items() if etiqueta == palanca), None)
    if subject is None:
        return []

    incluidos = {Subject.M1, Subject.M2} if subject == Subject.M2 else {subject}
    filas = db.execute(
        select(UserSkillProgress)
        .join(UserSkillProgress.skill_node)
        .where(UserSkillProgress.user_id == user_id)
        .where(UserSkillProgress.status != ProgressStatus.LOCKED)
    ).scalars().all()

    candidatos = [p for p in filas if p.skill_node.subject in incluidos]
    candidatos.sort(key=lambda p: (p.accuracy, -p.attempts))
    return [
        NodoDebilOut(
            code=p.skill_node.code, name=p.skill_node.name, axis=p.skill_node.axis.value,
            accuracy=round(p.accuracy, 2), attempts=p.attempts,
            has_lesson=p.skill_node.lesson is not None,
        )
        for p in candidatos[:4]
    ]


#: Cuánto toma cada cosa, medido con el propio producto.
#: Una lección con su ejemplo se lee en unos diez minutos, y practicar el tema
#: hasta que deje de fallar toma otros veinte.
MINUTOS_POR_TEMA = 30
#: Un ensayo corto son 20 preguntas al ritmo oficial de M1, más la revisión.
MINUTOS_ENSAYO_CORTO = 55


def _plan_semanal(horas: int | None, temas_disponibles: int) -> PlanSemanalOut:
    """Cuánto del plan cabe de verdad en la semana del estudiante.

    Sin horas declaradas se propone el plan completo: es mejor mostrar de más
    que inventarle una disponibilidad que nunca dijo tener.

    Con horas declaradas, el ensayo se reserva PRIMERO. Es lo que mide el
    avance y lo que exige el premio, así que si algo se cae de la semana que
    sean los temas, no el ensayo.
    """
    if horas is None or horas <= 0:
        return PlanSemanalOut(
            horas_semana=horas,
            temas_que_caben=temas_disponibles,
            alcanza_un_ensayo=True,
            minutos_estimados=temas_disponibles * MINUTOS_POR_TEMA
            + MINUTOS_ENSAYO_CORTO,
        )

    minutos = horas * 60
    alcanza_ensayo = minutos >= MINUTOS_ENSAYO_CORTO
    restantes = minutos - (MINUTOS_ENSAYO_CORTO if alcanza_ensayo else 0)
    caben = max(0, min(temas_disponibles, restantes // MINUTOS_POR_TEMA))

    return PlanSemanalOut(
        horas_semana=horas,
        temas_que_caben=int(caben),
        alcanza_un_ensayo=alcanza_ensayo,
        minutos_estimados=int(caben) * MINUTOS_POR_TEMA
        + (MINUTOS_ENSAYO_CORTO if alcanza_ensayo else 0),
    )


def calcular_meta(db: Session, user_id: int) -> MetaOut:
    user = db.get(User, user_id)
    assert user is not None
    postuladas = db.execute(
        select(MetaUsuario)
        .where(MetaUsuario.user_id == user_id)
        .order_by(MetaUsuario.preferencia)
    ).scalars().all()

    puntajes = mejores_puntajes(db, user_id)
    salida: list[PostulacionOut] = []
    for meta in postuladas:
        datos = _evaluar(meta.carrera, puntajes, user)
        salida.append(
            PostulacionOut(
                preferencia=meta.preferencia,
                carrera=CarreraOut.model_validate(meta.carrera),
                **datos,
            )
        )

    # El plan se arma para la preferencia MÁS ALTA que todavía no se alcanza:
    # es la que el estudiante quiere y aún puede pelear.
    objetivo = next((p for p in salida if p.alcanza is not True), None)
    palanca = objetivo.mejor_palanca if objetivo else None

    plan = _plan(db, user_id, palanca)

    return MetaOut(
        postulaciones=salida,
        puntaje_nem=user.puntaje_nem,
        puntaje_ranking=user.puntaje_ranking,
        proyeccion=_proyeccion(db, user_id),
        plan=plan,
        plan_para=objetivo.carrera.nombre if objetivo else None,
        plan_semanal=_plan_semanal(user.horas_semana, len(plan)),
    )
