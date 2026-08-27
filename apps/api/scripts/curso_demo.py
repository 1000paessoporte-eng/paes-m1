"""Arma un curso de mentira para poder mirar el panel del profesor.

El panel del profesor existe desde que existe el plan Colegios, pero mirarlo
sin alumnos no dice nada: la tabla sale vacía, los ejes no tienen barras y la
frase de arriba dice "todavía no entra nadie". Para saber si sirve hay que
verlo con un curso encima, y armar treinta cuentas a mano no lo hace nadie.

Esto crea un profesor, su curso y doce alumnos con historias distintas: los que
nunca rindieron, los que van bien, los que se perdieron hace tres semanas y el
que practica mucho pero no rinde un ensayo. Son justo los casos por los que el
profesor abre el panel.

Los ensayos se rinden de verdad --pasan por `start_attempt`, se responden
pregunta a pregunta y se entregan con `submit_attempt`-- así que el puntaje,
los ejes y el árbol de habilidades salen del mismo código que usa un alumno
real. Inventar las filas a mano habría dado un panel que se ve bien y miente.

SOLO CORRE CONTRA UNA BASE LOCAL. Es data falsa, y la primera regla del
proyecto es que no hay datos inventados: en producción esto ensuciaría las
métricas y le pondría a alguien doce compañeros que no existen.

    cd apps/api
    uv run python scripts/curso_demo.py              # crea el curso
    uv run python scripts/curso_demo.py --limpiar    # lo borra entero
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

import paes_api.all_models  # noqa: F401  (registra todos los mapeos)
from paes_api.core.config import get_settings
from paes_api.core.database import SessionLocal
from paes_api.core.security import hash_password
from paes_api.modules.colegios.models import Colegio, EnsayoProgramado
from paes_api.modules.content.models import Question
from paes_api.modules.exam_focus import service as exam_service
from paes_api.modules.exam_focus.models import ExamAttempt, Pace
from paes_api.modules.exam_focus.schemas import ExamAnswerIn, ExamConfigIn
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import SkillNode, Subject, UserSkillProgress
from paes_api.modules.users.models import User

#: El código que el profesor le dictaría al curso. Fijo, para poder escribirlo
#: en la pantalla de "unirse" sin ir a buscarlo a la base.
CODIGO = "PRUEBA"
#: Dominio de las cuentas de mentira. NO uses `.local` ni `.test`: son
#: nombres reservados y `EmailStr` los rechaza, así que el registro y el
#: login devuelven 422 sin decir por qué.
DOMINIO = "curso-demo.paes-m1.cl"
CLAVE = "demo1234"
NOMBRE_CURSO = "4° Medio B — Liceo de Prueba"

#: Cada alumno con su historia. `dias` es cuándo rindió cada ensayo, contado
#: hacia atrás desde hoy; `acierto` es la fracción de respuestas correctas, que
#: es lo que termina moviendo el puntaje y las barras por eje.
#:
#: Las historias no son decorado: son los casos que el panel tiene que
#: distinguir. Si los doce fueran iguales, mirarlo no diría si la tabla ordena
#: bien ni si la frase de arriba cuenta a los que hay que ir a buscar.
ALUMNOS: list[dict] = [
    # Los que nunca aparecieron. Entraron con el código y hasta ahí llegaron.
    {"nombre": "Camila Rojas", "ensayos": []},
    {"nombre": "Ignacio Fuentes", "ensayos": []},
    # Los que van bien y siguen rindiendo.
    {"nombre": "Antonia Vergara", "ensayos": [(1, 0.82), (6, 0.78), (14, 0.71)]},
    {"nombre": "Matías Sepúlveda", "ensayos": [(2, 0.75), (9, 0.69)]},
    {"nombre": "Josefa Muñoz", "ensayos": [(3, 0.88), (11, 0.80), (20, 0.74)]},
    # El grueso del curso: rinden, van al medio, aparecen cada tanto.
    {"nombre": "Benjamín Cáceres", "ensayos": [(4, 0.55), (12, 0.49)]},
    {"nombre": "Florencia Tapia", "ensayos": [(5, 0.61)]},
    {"nombre": "Vicente Aravena", "ensayos": [(8, 0.52), (17, 0.44)]},
    {"nombre": "Isidora Peña", "ensayos": [(6, 0.58), (13, 0.63)]},
    # Los perdidos: rindieron en marzo y no volvieron.
    {"nombre": "Tomás Herrera", "ensayos": [(24, 0.41)]},
    {"nombre": "Martina Silva", "ensayos": [(31, 0.38), (38, 0.35)]},
    # Practica harto pero nunca se sienta a rendir el ensayo completo.
    {"nombre": "Diego Contreras", "ensayos": [], "practicas": 47},
]

#: Los ensayos que el profesor dejó agendados: uno que ya pasó y dos por venir.
AGENDA = [
    ("Ensayo de diagnóstico M1", Subject.M1, -9, 65),
    ("Ensayo de Competencia Lectora", Subject.LECTORA, 4, 65),
    ("Repaso de Matemática M1", Subject.M1, 12, 20),
]


def _exigir_base_local() -> None:
    """Frena si la base no es local.

    No es paranoia: el string de producción vive en el `.env` de este mismo
    directorio, y correr esto contra Neon le mete doce alumnos falsos al panel
    de un colegio real y ensucia todas las métricas del producto.
    """
    url = get_settings().database_url
    if "localhost" not in url and "127.0.0.1" not in url:
        destino = url.split("@")[-1].split("/")[0] if "@" in url else "(desconocido)"
        sys.exit(
            f"Esto solo corre contra una base local, y DATABASE_URL apunta a {destino}.\n"
            "Es data inventada: en producción ensucia las métricas y le pone a "
            "alguien doce compañeros que no existen."
        )


def _cuentas_demo(db: Session) -> list[User]:
    """Las cuentas de mentira, por su dominio.

    El patrón es `@curso-demo.` y no el dominio exacto para que --limpiar
    alcance también a las cuentas de una corrida anterior con otro dominio.
    """
    return list(
        db.execute(select(User).where(User.email.like("%@curso-demo.%"))).scalars()
    )


def limpiar(db: Session) -> None:
    """Borra el curso y sus cuentas, con todo lo que colgaba de ellas."""
    usuarios = _cuentas_demo(db)
    ids = [u.id for u in usuarios]
    colegio = db.execute(
        select(Colegio).where(Colegio.codigo == CODIGO)
    ).scalars().first()

    if ids:
        # Los intentos se borran con la misma función que usa el producto
        # cuando un alumno borra un ensayo de su historial: arrastra las
        # respuestas y el set de preguntas del intento. Hacerlo a mano acá
        # significaría acordarse de cada tabla nueva que cuelgue de un intento.
        intentos = list(
            db.execute(
                select(ExamAttempt).where(ExamAttempt.user_id.in_(ids))
            ).scalars()
        )
        for intento in intentos:
            exam_service.delete_attempt(db, intento)
        db.execute(delete(PracticeAnswer).where(PracticeAnswer.user_id.in_(ids)))
        db.execute(
            delete(UserSkillProgress).where(UserSkillProgress.user_id.in_(ids))
        )
    if colegio is not None:
        db.execute(
            delete(EnsayoProgramado).where(EnsayoProgramado.colegio_id == colegio.id)
        )
    if ids:
        db.execute(delete(User).where(User.id.in_(ids)))
    if colegio is not None:
        # Alguien que se unió al curso con su cuenta de verdad para probarlo no
        # se borra: se le suelta el curso. Sin esto, la clave foránea impide
        # borrar el colegio y --limpiar revienta a la mitad.
        db.execute(
            update(User)
            .where(User.colegio_id == colegio.id)
            .values(colegio_id=None, es_profesor=False)
        )
        db.flush()
        db.delete(colegio)
    db.commit()
    print(f"borrado: {len(ids)} cuentas y {'1 curso' if colegio else 'ningún curso'}")


def _crear_usuario(db: Session, nombre: str, correo: str) -> User:
    user = User(
        email=correo,
        name=nombre,
        hashed_password=hash_password(CLAVE),
    )
    db.add(user)
    db.flush()
    return user


def _rendir(db: Session, user: User, dias_atras: int, acierto: float) -> None:
    """Rinde un ensayo completo por el alumno, con la fecha corrida hacia atrás.

    El tiempo importa: un ensayo entregado en cero segundos queda marcado como
    no representativo --con razón-- y entonces no suma al mejor puntaje ni al
    promedio del panel. Así que el intento nace con `started_at` en el pasado y
    se le fija `finished_at` un rato después, como si se hubiera rendido ese
    día.
    """
    config = ExamConfigIn(
        subject=Subject.M1,
        question_count=20,
        pace=Pace.OFICIAL,
        axes=[],
    )
    attempt = exam_service.start_attempt(db, user, config)
    preguntas = exam_service.attempt_questions(db, attempt)

    # Rindió hace `dias_atras` días y le tomó el 80% del tiempo concedido.
    duracion = int(attempt.duration_limit_seconds * 0.8)
    inicio = datetime.now(UTC) - timedelta(days=dias_atras, seconds=duracion)
    attempt.started_at = inicio
    db.flush()

    for pregunta in preguntas:
        alternativas = list(pregunta.alternatives)
        correcta = next((a for a in alternativas if a.is_correct), None)
        if correcta is None:
            continue
        if random.random() < acierto:
            elegida = correcta
        else:
            malas = [a for a in alternativas if not a.is_correct]
            elegida = random.choice(malas) if malas else correcta
        exam_service.upsert_answer(
            db,
            attempt.id,
            ExamAnswerIn(
                question_id=pregunta.id,
                selected_alternative_id=elegida.id,
                time_spent_ms=random.randint(45_000, 180_000),
            ),
        )

    exam_service.submit_attempt(db, attempt)
    # `submit_attempt` marca el fin en el instante actual, que es lo correcto
    # para un alumno de verdad. Acá se corrige a la fecha que le tocaba, que es
    # de donde el panel saca los "días sin rendir".
    attempt.finished_at = inicio + timedelta(seconds=duracion)
    db.commit()


def _practicar(db: Session, user: User, cuantas: int) -> None:
    """Respuestas sueltas de Modo Práctica, repartidas en las últimas semanas."""
    preguntas = list(
        db.execute(
            select(Question)
            .join(SkillNode, SkillNode.id == Question.skill_node_id)
            .where(SkillNode.subject == Subject.M1)
            .limit(cuantas)
        ).scalars()
    )
    for i, pregunta in enumerate(preguntas):
        db.add(
            PracticeAnswer(
                user_id=user.id,
                question_id=pregunta.id,
                skill_node_id=pregunta.skill_node_id,
                is_correct=random.random() < 0.6,
                answered_at=datetime.now(UTC) - timedelta(days=i % 21, hours=i % 7),
            )
        )
    db.commit()


def sembrar(db: Session) -> None:
    if db.execute(select(Colegio).where(Colegio.codigo == CODIGO)).scalars().first():
        sys.exit(
            f"Ya existe el curso {CODIGO}. Bórralo primero con --limpiar "
            "si quieres uno nuevo."
        )

    profe = _crear_usuario(db, "Profesora Demo", f"profe@{DOMINIO}")
    colegio = Colegio(nombre=NOMBRE_CURSO, codigo=CODIGO, creado_por=profe.id)
    db.add(colegio)
    db.flush()
    profe.colegio_id = colegio.id
    profe.es_profesor = True
    db.commit()

    hoy = datetime.now(UTC).date()
    for titulo, subject, dias, cantidad in AGENDA:
        db.add(
            EnsayoProgramado(
                colegio_id=colegio.id,
                titulo=titulo,
                subject=subject,
                pace=Pace.OFICIAL,
                question_count=cantidad,
                fecha=hoy + timedelta(days=dias),
            )
        )
    db.commit()

    for i, perfil in enumerate(ALUMNOS, start=1):
        correo = f"alumno{i:02d}@{DOMINIO}"
        alumno = _crear_usuario(db, perfil["nombre"], correo)
        alumno.colegio_id = colegio.id
        db.commit()
        for dias_atras, acierto in perfil.get("ensayos", []):
            _rendir(db, alumno, dias_atras, acierto)
        if perfil.get("practicas"):
            _practicar(db, alumno, perfil["practicas"])
        print(f"  {perfil['nombre']:22} {correo}")

    print()
    print(f"Curso creado: {NOMBRE_CURSO}")
    print(f"  Código para unirse: {CODIGO}")
    print(f"  Profesora:  profe@{DOMINIO} / {CLAVE}")
    print(f"  Alumnos:    alumnoNN@{DOMINIO} / {CLAVE}  ({len(ALUMNOS)} cuentas)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limpiar",
        action="store_true",
        help="borra el curso demo y todas sus cuentas",
    )
    args = parser.parse_args()

    _exigir_base_local()
    random.seed(42)  # el mismo curso en cada corrida, para poder comparar
    with SessionLocal() as db:
        if args.limpiar:
            limpiar(db)
        else:
            sembrar(db)


if __name__ == "__main__":
    main()
