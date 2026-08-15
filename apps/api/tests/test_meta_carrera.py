"""Puntaje ponderado y brecha con la carrera.

Este número decide una matrícula. Los casos de acá recalculan el ponderado a
mano y lo comparan con lo que devuelve el servicio: si alguien cambia la
fórmula, falla.
"""

import pytest
from fastapi.testclient import TestClient

from paes_api.modules.goals.models import Carrera


@pytest.fixture()
def carrera_ing(db_session) -> Carrera:
    """Ponderaciones reales de una carrera de ingeniería: M1 pesa fuerte."""
    c = Carrera(
        codigo="99001",
        universidad="UNIVERSIDAD DE PRUEBA",
        nombre="INGENIERÍA CIVIL",
        sede="SANTIAGO",
        nem=10, ranking=20, lectora=10, m1=35, ciencias=25,
        historia=None, m2=None, prueba_especial=None,
        electivo_alternativo=False,
        proceso=2026,
        fuente="https://demre.cl/",
    )
    db_session.add(c)
    db_session.commit()
    return c


def test_ponderado_es_la_suma_de_cada_factor_por_su_peso(
    client: TestClient, register_user, carrera_ing
) -> None:
    headers, _ = register_user()
    client.put(
        "/api/meta/notas",
        headers=headers,
        json={"puntaje_nem": 700, "puntaje_ranking": 800},
    )
    resp = client.post(
        "/api/meta/postulaciones", headers=headers, json={"carrera_id": carrera_ing.id}
    )
    assert resp.status_code == 201
    datos = resp.json()["postulaciones"][0]

    aportes = {a["factor"]: a for a in datos["aportes"]}
    # 10% de 700 y 20% de 800, recalculado acá sin mirar el servicio.
    assert aportes["nem"]["aporte"] == 70.0
    assert aportes["ranking"]["aporte"] == 160.0

    # Sin ensayos rendidos faltan las pruebas, así que no hay ponderado final:
    # mostrar uno parcial como si fuera el total sería engañar.
    assert datos["ponderado"] is None
    assert "Competencia Lectora" in datos["faltantes"]


def test_cada_10_puntos_valen_la_decima_parte_de_la_ponderacion(
    client: TestClient, register_user, carrera_ing
) -> None:
    """La regla que hace útil la pantalla: en una carrera que pondera M1 al
    35%, subir 10 puntos en M1 sube 3,5 el ponderado."""
    headers, _ = register_user()
    datos = client.post(
        "/api/meta/postulaciones", headers=headers, json={"carrera_id": carrera_ing.id}
    ).json()["postulaciones"][0]

    aportes = {a["factor"]: a for a in datos["aportes"]}
    assert aportes["m1"]["por_cada_10"] == 3.5
    assert aportes["lectora"]["por_cada_10"] == 1.0


def test_la_palanca_pondera_el_peso_por_el_margen(
    client: TestClient, register_user, carrera_ing
) -> None:
    """Con todo en cero, la mejor palanca es la prueba de mayor ponderación."""
    headers, _ = register_user()
    datos = client.post(
        "/api/meta/postulaciones", headers=headers, json={"carrera_id": carrera_ing.id}
    ).json()["postulaciones"][0]
    assert datos["mejor_palanca"] == "Matemática M1"


def test_la_palanca_nunca_es_el_ranking_ni_el_nem(
    client: TestClient, register_user, db_session
) -> None:
    """Las notas del colegio ya están puestas: ninguna hora de estudio las
    mueve. Recomendarlas sería dar un consejo imposible de seguir."""
    from paes_api.modules.goals.models import Carrera

    # Ranking pondera 60% y las pruebas poco: aun así la palanca es una prueba.
    c = Carrera(
        codigo="99002", universidad="U", nombre="CARRERA CON RANKING ALTO",
        sede="S", nem=10, ranking=60, lectora=20, m1=10,
        proceso=2026, fuente="https://demre.cl/",
    )
    db_session.add(c)
    db_session.commit()

    headers, _ = register_user(email="palanca@test.cl")
    client.put(
        "/api/meta/notas",
        headers=headers,
        json={"puntaje_nem": 300, "puntaje_ranking": 300},
    )
    datos = client.post(
        "/api/meta/postulaciones", headers=headers, json={"carrera_id": c.id}
    ).json()["postulaciones"][0]
    assert datos["mejor_palanca"] in ("Competencia Lectora", "Matemática M1")


def test_una_carrera_sin_los_datos_no_entra(client: TestClient, register_user) -> None:
    headers, _ = register_user()
    resp = client.post(
        "/api/meta/postulaciones", headers=headers, json={"carrera_id": 999999}
    )
    assert resp.status_code == 404


def test_la_meta_exige_sesion(client: TestClient) -> None:
    assert client.get("/api/meta").status_code == 401


def test_buscar_carreras_exige_tres_letras(
    client: TestClient, register_user, carrera_ing
) -> None:
    headers, _ = register_user()
    assert client.get("/api/meta/carreras?q=in", headers=headers).status_code == 422
    resp = client.get("/api/meta/carreras?q=ingenier", headers=headers)
    assert resp.status_code == 200
    assert resp.json()[0]["nombre"] == "INGENIERÍA CIVIL"


def test_las_ponderaciones_del_archivo_oficial_suman_100() -> None:
    """El contrato del dataset: si una carrera no suma 100, está mal parseada y
    no debe existir en el archivo."""
    import json
    from pathlib import Path

    ruta = Path(__file__).resolve().parents[1] / "src/paes_api/data/carreras_2026.json"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    campos = ["nem", "ranking", "lectora", "m1", "historia", "ciencias", "m2",
              "prueba_especial"]

    for fila in datos["carreras"]:
        total = sum(fila.get(c) or 0 for c in campos)
        if fila.get("electivo_alternativo"):
            total -= min(fila.get("historia") or 0, fila.get("ciencias") or 0)
        assert abs(total - 100) < 0.51, f"{fila['codigo']} suma {total}"


def test_el_dataset_declara_proceso_y_fuente() -> None:
    """Un puntaje sin año ni origen no se puede verificar, y estos datos
    cambian todos los años."""
    import json
    from pathlib import Path

    ruta = Path(__file__).resolve().parents[1] / "src/paes_api/data/carreras_2026.json"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos["proceso"] == 2026
    assert datos["fuente"].startswith("https://demre.cl/")


def test_se_busca_sin_tildes(client: TestClient, register_user, db_session) -> None:
    """Nadie escribe "ENFERMERÍA" con tilde en un buscador. Este fue un bug
    real: la carrera existía y la búsqueda no la encontraba."""
    from paes_api.modules.goals.models import Carrera

    c = Carrera(
        codigo="99003", universidad="UNIVERSIDAD DE CONCEPCIÓN",
        nombre="ENFERMERÍA", sede="CONCEPCIÓN",
        nem=20, ranking=20, lectora=30, m1=30,
        proceso=2026, fuente="https://demre.cl/",
    )
    db_session.add(c)
    db_session.commit()

    headers, _ = register_user(email="tildes@test.cl")
    for termino in ("enfermeria", "ENFERMERIA", "Enfermería"):
        resp = client.get(f"/api/meta/carreras?q={termino}", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1, f"'{termino}' no encontró la carrera"


def test_se_busca_por_palabras_sueltas(
    client: TestClient, register_user, db_session
) -> None:
    """"enfermeria concepcion" tiene que funcionar aunque en el dato la
    universidad vaya antes que la sede."""
    from paes_api.modules.goals.models import Carrera

    db_session.add(
        Carrera(
            codigo="99004", universidad="UNIVERSIDAD DE CONCEPCIÓN",
            nombre="ENFERMERÍA", sede="LOS ÁNGELES",
            nem=20, ranking=20, lectora=30, m1=30,
            proceso=2026, fuente="https://demre.cl/",
        )
    )
    db_session.commit()

    headers, _ = register_user(email="palabras@test.cl")
    resp = client.get("/api/meta/carreras?q=enfermeria angeles", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_no_hay_ritmo_con_ensayos_del_mismo_dia(
    client: TestClient, register_user, db_session
) -> None:
    """Extrapolar un día a un mes multiplica el ruido por treinta: cuatro
    ensayos rendidos la misma tarde llegaban a decir "vienes bajando 2.760
    puntos al mes", que es un disparate con aspecto de dato."""
    from datetime import UTC, datetime

    from paes_api.modules.exam_focus.models import ExamAttempt

    headers, usuario = register_user(email="ritmo@test.cl")
    hoy = datetime.now(UTC)
    for puntaje in (500, 480, 460, 408):
        db_session.add(
            ExamAttempt(
                user_id=usuario["id"], subject="m1", status="submitted",
                estimated_score=puntaje, started_at=hoy, finished_at=hoy,
                duration_limit_seconds=2580,
            )
        )
    db_session.commit()

    proyeccion = client.get("/api/meta", headers=headers).json()["proyeccion"]
    assert proyeccion["ensayos_considerados"] == 4
    assert proyeccion["puntos_por_mes"] is None
    assert proyeccion["proyectado"] is None
