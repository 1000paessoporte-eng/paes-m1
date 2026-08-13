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


def test_root_node_starts_unlocked_and_child_starts_locked(
    client: TestClient, db_session: Session, register_user
) -> None:
    root = _make_node(db_session, "raiz")
    _make_node(db_session, "hijo", prerequisites=[root])
    headers, _ = register_user()

    resp = client.get("/api/skill-tree", headers=headers)
    assert resp.status_code == 200
    by_code = {n["code"]: n for n in resp.json()}
    assert by_code["raiz"]["status"] == "unlocked"
    assert by_code["hijo"]["status"] == "locked"


def test_child_unlocks_after_prerequisite_meets_threshold(
    client: TestClient, db_session: Session, register_user
) -> None:
    root = _make_node(db_session, "raiz2")
    _make_node(db_session, "hijo2", prerequisites=[root])
    _, user = register_user(email="unlock@milpaes.cl")

    # 4 respuestas correctas en el nodo raiz (MIN_ATTEMPTS_FOR_UNLOCK=4,
    # unlock_threshold=0.75) deben desbloquear a su hijo.
    skill_tree_service.apply_single_answer(db_session, user["id"], root.id, True)
    skill_tree_service.apply_single_answer(db_session, user["id"], root.id, True)
    skill_tree_service.apply_single_answer(db_session, user["id"], root.id, True)
    newly_unlocked = skill_tree_service.apply_single_answer(
        db_session, user["id"], root.id, True
    )

    assert [n.code for n in newly_unlocked] == ["hijo2"]

    tree = skill_tree_service.get_user_skill_tree(db_session, user["id"])
    hijo = next(n for n in tree if n.code == "hijo2")
    assert hijo.status == ProgressStatus.UNLOCKED


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
