"""El ensayo del día: uno por prueba al día, el mismo para todos."""

import subprocess
import sys
from datetime import UTC, date, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus import del_dia
from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject
from paes_api.modules.users.models import User


def _banco(db: Session, cuantas: int = 80) -> None:
    node = SkillNode(
        code="n_dia", name="Tema", axis=SkillAxis.NUMEROS, subject=Subject.M1,
        tier=1, unlock_threshold=0.75,
    )
    db.add(node)
    db.flush()
    for i in range(cuantas):
        q = Question(skill_node_id=node.id, difficulty=Difficulty.MEDIO, stem=f"Dia{i}")
        db.add(q)
        db.flush()
        db.add_all([
            Alternative(question_id=q.id, label="A", text="ok", is_correct=True),
            Alternative(question_id=q.id, label="B", text="mal", is_correct=False,
                        distractor_justification="No."),
        ])
    db.commit()


@pytest.fixture()
def limites_activos(monkeypatch):
    monkeypatch.setenv("LIMITES_ACTIVOS", "true")
    get_settings.cache_clear()
    yield
    monkeypatch.delenv("LIMITES_ACTIVOS", raising=False)
    get_settings.cache_clear()


def _ids(db: Session, fecha: date) -> list[int]:
    return [q.id for q in del_dia.preguntas_del_dia(db, Subject.M1, fecha)]


def test_mismo_dia_mismas_preguntas_otro_dia_otras(db_session: Session) -> None:
    _banco(db_session)
    hoy = date(2026, 9, 21)
    assert len(_ids(db_session, hoy)) == del_dia.PREGUNTAS
    assert _ids(db_session, hoy) == _ids(db_session, hoy)
    assert _ids(db_session, hoy) != _ids(db_session, date(2026, 9, 22))


def test_el_del_dia_no_mueve_el_azar_de_los_demas_ensayos(db_session: Session) -> None:
    """Sembrar el `random` global haría que el ensayo de otro alumno, armado
    justo después, saliera predecible."""
    import random

    _banco(db_session)
    random.seed(123)
    esperado = random.random()
    random.seed(123)
    _ids(db_session, date(2026, 9, 21))
    assert random.random() == esperado


def test_es_el_mismo_en_otro_proceso() -> None:
    """Lo que de verdad importa: dos servidores distintos arman el mismo
    ensayo. Otro proceso trae otro PYTHONHASHSEED, así que si la selección
    dependiera del orden de un set de strings, esto lo delataría."""
    codigo = r'''
import os
os.environ["ENVIRONMENT"] = "test"
os.environ["SMTP_HOST"] = ""
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import paes_api.all_models
from paes_api.shared.base import Base
from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus import del_dia
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject
e = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(e)
db = sessionmaker(bind=e)()
for eje in (SkillAxis.NUMEROS, SkillAxis.ALGEBRA, SkillAxis.GEOMETRIA, SkillAxis.PROBABILIDAD):
    n = SkillNode(code=f"n_{eje.value}", name=eje.value, axis=eje, subject=Subject.M1, tier=1, unlock_threshold=0.75)
    db.add(n); db.flush()
    for i in range(30):
        q = Question(skill_node_id=n.id, difficulty=Difficulty.MEDIO, stem=f"{eje.value}{i}")
        db.add(q); db.flush()
        db.add(Alternative(question_id=q.id, label="A", text="ok", is_correct=True))
db.commit()
print([q.stem for q in del_dia.preguntas_del_dia(db, Subject.M1, date(2026, 9, 21))])
'''
    salidas = {
        subprocess.run(
            [sys.executable, "-c", codigo],
            capture_output=True, text=True, check=True,
            env={"PYTHONHASHSEED": semilla, "PATH": ""},
        ).stdout
        for semilla in ("1", "2", "3")
    }
    assert len(salidas) == 1, salidas


def test_el_dia_cambia_a_medianoche_de_chile() -> None:
    # 23:30 del 20 en Santiago (UTC-3) ya es el 21 en UTC.
    assert del_dia.hoy(datetime(2026, 9, 21, 2, 30, tzinfo=UTC)) == date(2026, 9, 20)
    assert del_dia.hoy(datetime(2026, 9, 21, 3, 30, tzinfo=UTC)) == date(2026, 9, 21)


def test_gratis_rinde_uno_por_prueba_al_dia(
    client: TestClient, db_session: Session, register_user, limites_activos
) -> None:
    _banco(db_session)
    headers, _ = register_user(email="dia@milpaes.cl")

    # Pide 65 preguntas a su medida: igual recibe el ensayo del día.
    r = client.post("/api/exam/start", headers=headers,
                    json={"subject": "m1", "question_count": 65, "pace": "relajado"})
    assert r.status_code == 200, r.text
    primero = r.json()
    assert len(primero["questions"]) == del_dia.PREGUNTAS
    esperadas = [q.id for q in del_dia.preguntas_del_dia(db_session, Subject.M1, del_dia.hoy())]
    assert [q["id"] for q in primero["questions"]] == esperadas

    # En curso: no se abre otro, se le dice que lo retome.
    segundo = client.post("/api/exam/start", headers=headers, json={"subject": "m1"})
    assert segundo.status_code == 409
    assert "Retómalo" in segundo.json()["detail"]

    # Terminado: tampoco, y se le dice cuándo vuelve a haber.
    client.post(f"/api/exam/{primero['attempt_id']}/submit", headers=headers)
    tercero = client.post("/api/exam/start", headers=headers, json={"subject": "m1"})
    assert tercero.status_code == 409
    assert "Mañana" in tercero.json()["detail"]

    estado = client.get("/api/exam/del-dia", headers=headers).json()
    assert estado["solo_ensayo_del_dia"] is True
    m1 = next(p for p in estado["pruebas"] if p["subject"] == "m1")
    assert m1["estado"] == "rendido" and m1["attempt_id"] == primero["attempt_id"]
    otras = [p["estado"] for p in estado["pruebas"] if p["subject"] != "m1"]
    assert otras == ["disponible"] * 4


def test_sin_limites_activos_gratis_arma_sus_ensayos(
    client: TestClient, db_session: Session, register_user
) -> None:
    _banco(db_session)
    headers, _ = register_user(email="libre@milpaes.cl")
    for _ in range(2):
        r = client.post("/api/exam/start", headers=headers,
                        json={"subject": "m1", "question_count": 30})
        assert r.status_code == 200
        assert len(r.json()["questions"]) == 30
    assert client.get("/api/exam/del-dia", headers=headers).json()["solo_ensayo_del_dia"] is False


# --- Comparación con quienes rindieron el mismo ensayo -----------------------


def _rendido(db: Session, user_id: int, puntaje: int, cuando: datetime, **extra) -> ExamAttempt:
    intento = ExamAttempt(
        user_id=user_id, subject="m1", status="submitted", estimated_score=puntaje,
        started_at=cuando, finished_at=cuando, duration_limit_seconds=2580, **extra,
    )
    db.add(intento)
    db.commit()
    return intento


def _usuario(db: Session, correo: str) -> User:
    u = User(email=correo, name=correo, hashed_password="x")
    db.add(u)
    db.commit()
    return u


def _mediodia(fecha: date) -> datetime:
    """Las 12:00 en Chile, bien dentro del día, mire quien mire el reloj."""
    return datetime.combine(fecha, time(12, 0), tzinfo=del_dia.CHILE).astimezone(UTC)


def test_con_poca_gente_no_se_compara(db_session: Session) -> None:
    """Un "puesto 2 de 3" no dice nada del nivel, y en un curso de tres deja a
    cada uno deducir el puntaje de los otros."""
    hoy = del_dia.hoy()
    yo = _usuario(db_session, "yo@milpaes.cl")
    _rendido(db_session, yo.id, 700, _mediodia(hoy))
    _rendido(db_session, _usuario(db_session, "otro@milpaes.cl").id, 500, _mediodia(hoy))

    c = del_dia.comparacion(db_session, yo.id, Subject.M1, hoy)
    assert c.rindieron == 2
    assert c.mi_puntaje == 700
    assert (c.promedio, c.mejor, c.posicion) == (None, None, None)


def test_promedio_y_puesto_con_suficiente_gente(db_session: Session) -> None:
    hoy = del_dia.hoy()
    yo = _usuario(db_session, "yo@milpaes.cl")
    _rendido(db_session, yo.id, 700, _mediodia(hoy))
    for i, puntaje in enumerate((400, 500, 600, 900)):
        _rendido(db_session, _usuario(db_session, f"c{i}@milpaes.cl").id, puntaje, _mediodia(hoy))

    c = del_dia.comparacion(db_session, yo.id, Subject.M1, hoy)
    assert c.rindieron == 5
    assert c.promedio == 620  # (700+400+500+600+900)/5
    assert c.mejor == 900
    assert (c.mi_puntaje, c.posicion) == (700, 2)


def test_repetir_el_ensayo_no_mejora_el_puesto(db_session: Session) -> None:
    """Cuenta la primera vuelta: el plan Pro puede rendir de nuevo, y si valiera
    el mejor intento el ranking sería de quién insiste más, no de quién sabe."""
    hoy = del_dia.hoy()
    yo = _usuario(db_session, "yo@milpaes.cl")
    _rendido(db_session, yo.id, 400, _mediodia(hoy))
    _rendido(db_session, yo.id, 950, _mediodia(hoy) + timedelta(hours=2))
    for i, puntaje in enumerate((500, 600, 700, 800)):
        _rendido(db_session, _usuario(db_session, f"c{i}@milpaes.cl").id, puntaje, _mediodia(hoy))

    c = del_dia.comparacion(db_session, yo.id, Subject.M1, hoy)
    assert c.rindieron == 5  # una persona, un puntaje
    assert (c.mi_puntaje, c.posicion) == (400, 5)


def test_no_entra_lo_de_ayer_ni_lo_sin_terminar_ni_lo_no_representativo(
    db_session: Session,
) -> None:
    hoy = del_dia.hoy()
    yo = _usuario(db_session, "yo@milpaes.cl")
    _rendido(db_session, yo.id, 700, _mediodia(hoy))
    _rendido(db_session, _usuario(db_session, "ayer@milpaes.cl").id, 800,
             _mediodia(hoy - timedelta(days=1)))
    _rendido(db_session, _usuario(db_session, "corto@milpaes.cl").id, 300,
             _mediodia(hoy), representativo=False)
    db_session.add(ExamAttempt(
        user_id=_usuario(db_session, "curso@milpaes.cl").id, subject="m1",
        status="in_progress", started_at=_mediodia(hoy), duration_limit_seconds=2580,
    ))
    db_session.commit()

    c = del_dia.comparacion(db_session, yo.id, Subject.M1, hoy)
    assert c.rindieron == 1 and c.mi_puntaje == 700


def test_el_ensayo_del_dia_trae_su_comparacion(
    client: TestClient, db_session: Session, register_user
) -> None:
    headers, yo = register_user(email="comparo@milpaes.cl")
    hoy = del_dia.hoy()
    _rendido(db_session, yo["id"], 650, _mediodia(hoy))

    r = client.get("/api/exam/del-dia", headers=headers)
    assert r.status_code == 200, r.text
    m1 = next(p for p in r.json()["pruebas"] if p["subject"] == "m1")
    # Sin límites activos arma sus propios ensayos, así que su estado es
    # "disponible" --no se sabe cuál de los de hoy fue el del día-- y aun así
    # la comparación le llega: rindió el mismo ensayo que todos.
    assert m1["estado"] == "disponible"
    assert m1["mi_puntaje"] == 650
    assert m1["rindieron"] == 1
    assert m1["promedio"] is None  # con una persona no hay con quién comparar
    assert m1["minimo_para_comparar"] == del_dia.MINIMO_PARA_COMPARAR
