"""Cálculo del puntaje ponderado y de la brecha con la carrera.

El puntaje ponderado es una suma simple —cada factor por su peso, dividido por
100— pero es lo que decide una admisión y casi ningún estudiante lo tiene a la
vista mientras estudia. Lo interesante no es el número sino su consecuencia:
con las mismas horas de estudio, subir diez puntos en la prueba que la carrera
pondera al 35% vale tres veces y media más que subirlos donde pondera 10%.
"""

import unicodedata

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.goals.models import Carrera, MetaUsuario
from paes_api.modules.goals.schemas import AporteOut, CarreraOut, MetaOut
from paes_api.modules.skill_tree.models import Subject

#: Factor de la carrera -> (etiqueta para el estudiante, subject del ensayo).
#: NEM y ranking no tienen ensayo: los ingresa el estudiante.
FACTORES: dict[str, tuple[str, Subject | None]] = {
    "nem": ("Notas (NEM)", None),
    "ranking": ("Ranking de notas", None),
    "lectora": ("Competencia Lectora", Subject.LECTORA),
    "m1": ("Matemática M1", Subject.M1),
    "m2": ("Matemática M2", Subject.M2),
    "historia": ("Historia y Cs. Sociales", Subject.HISTORIA),
    "ciencias": ("Ciencias", Subject.CIENCIAS),
}


def mejores_puntajes(db: Session, user_id: int) -> dict[Subject, int]:
    """El mejor puntaje logrado en cada prueba.

    Se usa el mejor y no el último a propósito: es el que el estudiante ya
    demostró que puede alcanzar, y es el que la proyección debe reflejar.
    """
    filas = db.execute(
        select(ExamAttempt.subject, ExamAttempt.estimated_score)
        .where(ExamAttempt.user_id == user_id)
        .where(ExamAttempt.status == "submitted")
        .where(ExamAttempt.estimated_score.is_not(None))
    ).all()

    mejores: dict[Subject, int] = {}
    for subject, puntaje in filas:
        if puntaje is None:
            continue
        if subject not in mejores or puntaje > mejores[subject]:
            mejores[subject] = puntaje
    return mejores


def calcular_meta(db: Session, user_id: int) -> MetaOut | None:
    meta = db.execute(
        select(MetaUsuario).where(MetaUsuario.user_id == user_id)
    ).scalar_one_or_none()
    if meta is None:
        return None

    carrera = meta.carrera
    puntajes = mejores_puntajes(db, user_id)

    # Con electivo alternativo ("Historia ó Ciencias") solo cuenta la mejor de
    # las dos, y la otra queda fuera del cálculo en vez de sumar dos veces.
    ignorar: set[str] = set()
    if carrera.electivo_alternativo:
        p_hist = puntajes.get(Subject.HISTORIA)
        p_cien = puntajes.get(Subject.CIENCIAS)
        if p_hist is None and p_cien is None:
            ignorar.add("ciencias")  # se pide una sola; se muestra Historia
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
            puntaje = meta.puntaje_nem if factor == "nem" else meta.puntaje_ranking
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
                factor=factor,
                etiqueta=etiqueta,
                ponderacion=peso,
                puntaje=puntaje,
                aporte=round(aporte, 1),
                # La derivada del ponderado respecto de este factor: exacta, no
                # una estimación.
                por_cada_10=round(peso / 10, 1),
                origen=origen,
            )
        )

    # Dónde rinde más ESTUDIAR: pondera cuánto pesa el factor por cuánto margen
    # queda. Un factor con peso alto donde ya se está en 950 rinde menos que uno
    # con peso medio donde se está en 500.
    #
    # NEM y ranking quedan fuera a propósito, aunque suelen ser los de mayor
    # ponderación: son las notas del colegio, ya están puestas y ninguna hora de
    # estudio las mueve. Incluirlas hacía que la pantalla recomendara "mejora tu
    # ranking", que es un consejo imposible de seguir.
    palanca = None
    mejor_valor = -1.0
    for a in aportes:
        if FACTORES[a.factor][1] is None:
            continue
        margen = 1000 - (a.puntaje or 0)
        valor = a.ponderacion * margen
        if valor > mejor_valor:
            mejor_valor, palanca = valor, a.etiqueta

    return MetaOut(
        carrera=CarreraOut.model_validate(carrera),
        ponderado=round(total, 1) if completo else None,
        aportes=aportes,
        faltantes=faltantes,
        mejor_palanca=palanca,
    )


def normalizar(texto: str) -> str:
    """Sin tildes y en minúsculas, para comparar como escribe la gente."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())


def buscar_carreras(db: Session, texto: str, limite: int = 20) -> list[Carrera]:
    """Busca por nombre de carrera, universidad o sede, ignorando tildes.

    Cada palabra se exige por separado en vez de buscar la frase completa: así
    "enfermeria concepcion" encuentra la carrera aunque en el dato el nombre de
    la universidad vaya antes que el de la sede, y el estudiante no tiene que
    adivinar el orden ni el nombre oficial exacto.
    """
    palabras = [p for p in normalizar(texto).split() if p]
    if not palabras:
        return []

    consulta = select(Carrera)
    for palabra in palabras:
        consulta = consulta.where(Carrera.busqueda.like(f"%{palabra}%"))

    return list(
        db.execute(
            consulta.order_by(Carrera.universidad, Carrera.nombre).limit(limite)
        )
        .scalars()
        .all()
    )
