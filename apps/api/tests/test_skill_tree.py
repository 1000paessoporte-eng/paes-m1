from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.skill_tree import service as skill_tree_service
from paes_api.modules.skill_tree.models import ProgressStatus, SkillAxis, SkillNode


def _make_node(
    db_session: Session, code: str, prerequisites: list[SkillNode] | None = None
) -> SkillNode:
    node = SkillNode(
        code=code,
        name=code,
        axis=SkillAxis.ALGEBRA,
        tier=1,
        unlock_threshold=0.75,
        display_order=0,
        prerequisites=prerequisites or [],
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)
    return node


def test_todos_los_temas_nacen_abiertos_aunque_tengan_prerequisitos(
    client: TestClient, db_session: Session, register_user
) -> None:
    """El árbol pasó de puerta a mapa.

    Antes un nodo con prerequisitos nacía BLOQUEADO. Eso dejaba M2 entera
    inaccesible --sus dieciséis temas cuelgan de M1-- mientras Modo Ensayo
    dejaba rendir un ensayo de M2 completo el primer día. Ahora los
    prerequisitos siguen ahí, dibujando el orden recomendado, pero no cierran
    nada.
    """
    root = _make_node(db_session, "raiz")
    _make_node(db_session, "hijo", prerequisites=[root])
    headers, _ = register_user()

    resp = client.get("/api/skill-tree", headers=headers)
    assert resp.status_code == 200
    by_code = {n["code"]: n for n in resp.json()}
    assert by_code["raiz"]["status"] == "unlocked"
    assert by_code["hijo"]["status"] == "unlocked"
    # El prerequisito no desaparece: es lo que ordena el árbol en pantalla.
    assert by_code["hijo"]["prerequisite_codes"] == ["raiz"]


def test_dominar_el_prerequisito_ya_no_desbloquea_nada_porque_nada_esta_cerrado(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Ya no hay nada que celebrar como "desbloqueaste un tema".

    El hijo estaba disponible desde el primer día, así que dominar a su padre
    no le abre nada: `newly_unlocked` viene vacío y el banner de desbloqueo no
    aparece. Lo que sí sigue pasando es que el padre queda DOMINADO.
    """
    root = _make_node(db_session, "raiz2")
    _make_node(db_session, "hijo2", prerequisites=[root])
    _, user = register_user(email="unlock@milpaes.cl")

    tree = skill_tree_service.get_user_skill_tree(db_session, user["id"])
    assert next(n for n in tree if n.code == "hijo2").status == ProgressStatus.UNLOCKED

    for _ in range(4):
        newly_unlocked = skill_tree_service.apply_single_answer(
            db_session, user["id"], root.id, True
        )
        assert newly_unlocked == []

    tree = skill_tree_service.get_user_skill_tree(db_session, user["id"])
    assert next(n for n in tree if n.code == "raiz2").status == ProgressStatus.MASTERED
    assert next(n for n in tree if n.code == "hijo2").status == ProgressStatus.UNLOCKED


def test_node_masters_when_owner_meets_its_own_threshold(
    client: TestClient, db_session: Session, register_user
) -> None:
    root = _make_node(db_session, "raiz3")
    _, user = register_user(email="master@milpaes.cl")

    skill_tree_service.apply_single_answer(db_session, user["id"], root.id, True)
    skill_tree_service.apply_single_answer(db_session, user["id"], root.id, True)
    skill_tree_service.apply_single_answer(db_session, user["id"], root.id, True)
    skill_tree_service.apply_single_answer(db_session, user["id"], root.id, True)

    tree = skill_tree_service.get_user_skill_tree(db_session, user["id"])
    node = next(n for n in tree if n.code == "raiz3")
    assert node.status == ProgressStatus.MASTERED


def test_get_unknown_node_is_404(client: TestClient, register_user) -> None:
    headers, _ = register_user()
    resp = client.get("/api/skill-tree/no-existe", headers=headers)
    assert resp.status_code == 404


def test_recommended_prioritizes_never_attempted_over_weak_accuracy(
    client: TestClient, db_session: Session, register_user
) -> None:
    weak = _make_node(db_session, "debil")
    _make_node(db_session, "nuevo")
    headers, user = register_user(email="recomendado@milpaes.cl")

    # "debil" ya tiene intentos con baja accuracy, pero "nuevo" nunca se
    # intento -- el bonus never_attempted (0.4) debe ganarle igual.
    skill_tree_service.apply_single_answer(db_session, user["id"], weak.id, False)
    skill_tree_service.apply_single_answer(db_session, user["id"], weak.id, False)

    resp = client.get("/api/skill-tree/recommended", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["code"] == "nuevo"


def test_recommended_returns_none_without_unlocked_candidates(
    client: TestClient, register_user
) -> None:
    headers, _ = register_user(email="sinarbol@milpaes.cl")
    resp = client.get("/api/skill-tree/recommended", headers=headers)
    assert resp.status_code == 200
    assert resp.json() is None


def test_el_arbol_dice_de_que_se_trata_cada_tema(
    client: TestClient, db_session: Session, register_user
) -> None:
    """La tarjeta del árbol es donde se ELIGE qué estudiar.

    Traía el nombre y el porcentaje de acierto, nada más. "Transformaciones
    isométricas" no le dice nada a alguien de tercero medio: para saber de qué
    iba había que abrir la lección, o sea decidir antes de tener con qué
    decidir. El texto ya estaba escrito en `lessons.intro` --existe justamente
    para responder "¿para qué me sirve esto?"-- y no viajaba con el nodo.
    """
    from paes_api.modules.content.models import Lesson

    con_leccion = _make_node(db_session, "con_teoria")
    sin_leccion = _make_node(db_session, "sin_teoria")
    db_session.add(
        Lesson(
            skill_node_id=con_leccion.id,
            intro="Las potencias son la forma corta de escribir multiplicaciones repetidas.",
            theory="Propiedades.",
            example_statement="Calcula 2³.",
            example_steps=[{"accion": "Multiplica 2·2·2", "porque": "Es la definición"}],
            common_error="Sumar los exponentes al multiplicar bases distintas.",
        )
    )
    db_session.commit()

    headers, _ = register_user(email="arbol-intro@milpaes.cl")
    nodos = {n["code"]: n for n in client.get("/api/skill-tree", headers=headers).json()}

    assert nodos["con_teoria"]["has_lesson"] is True
    assert nodos["con_teoria"]["lesson_intro"].startswith("Las potencias son")

    # Un nodo sin teoría no inventa una: la tarjeta simplemente no la muestra.
    assert nodos["sin_teoria"]["has_lesson"] is False
    assert nodos["sin_teoria"]["lesson_intro"] is None


def test_el_arbol_dice_cuantas_respuestas_hacen_falta_para_dominar(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Dominar exige umbral de acierto Y un mínimo de respuestas.

    La segunda condición era invisible y es la que frena: en producción hay 24
    nodos-alumno en el umbral o por encima y solo 6 dominados, porque la
    mediana de respuestas por tema es 2 y el mínimo son 4. El estudiante
    respondía bien y el contador seguía en cero sin decirle cuánto faltaba.

    El mínimo viaja con el nodo para que la pantalla lo diga sin recodificar
    la regla: tenerla en Python y en TypeScript es tenerla en un sitio que se
    olvida de cambiar.
    """
    _make_node(db_session, "un_nodo")
    db_session.commit()

    headers, _ = register_user(email="arbol-minimo@milpaes.cl")
    nodo = client.get("/api/skill-tree", headers=headers).json()[0]

    assert nodo["min_attempts_to_master"] == skill_tree_service.MIN_ATTEMPTS_FOR_UNLOCK
    assert nodo["unlock_threshold"] == 0.75


def test_la_recomendacion_sale_del_arbol_que_se_esta_mirando(
    client: TestClient, db_session: Session, register_user
) -> None:
    """"Empieza por acá" recomendaba SIEMPRE un nodo de M1.

    `get_user_skill_tree` sin argumento devuelve M1 por defecto, y la
    recomendación lo llamaba así. En la práctica, alguien que abría el árbol de
    Ciencias leía "Medidas de posición" —un nodo de Matemática M1— y al tocar
    "Practicar ahora" terminaba fuera de la prueba que estaba preparando.
    """
    from paes_api.modules.skill_tree.models import Subject

    nodo_m1 = _make_node(db_session, "reco_m1")
    nodo_cie = SkillNode(
        code="reco_ciencias",
        name="Un tema de Ciencias",
        axis=SkillAxis.BIOLOGIA,
        subject=Subject.CIENCIAS,
        tier=1,
        unlock_threshold=0.75,
    )
    db_session.add(nodo_cie)
    db_session.commit()

    headers, _ = register_user(email="reco-por-prueba@milpaes.cl")

    m1 = client.get("/api/skill-tree/recommended", headers=headers).json()
    assert m1 is not None and m1["code"] == nodo_m1.code

    ciencias = client.get(
        "/api/skill-tree/recommended", params={"subject": "ciencias"}, headers=headers
    ).json()
    assert ciencias is not None, "el árbol de Ciencias tiene nodos: debe recomendar uno"
    assert ciencias["code"] == "reco_ciencias"
    assert ciencias["subject"] == "ciencias", "la recomendación salió de otra prueba"
