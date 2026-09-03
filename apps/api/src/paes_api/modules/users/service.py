import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import CorreoNoEnviado, send_email
from paes_api.core.security import hash_password, verify_password
from paes_api.modules.users.models import LoginEvent, PasswordResetToken, User
from paes_api.modules.users.schemas import RegisterIn, UpdateMeIn

logger = logging.getLogger(__name__)

RESET_TOKEN_TTL_MINUTES = 30


def record_login(db: Session, user: User, method: str) -> None:
    """Deja constancia de una entrada exitosa.

    Se guardan las dos cosas a propósito: `last_login_at` responde "¿sigue
    activa esta cuenta?" sin recorrer la tabla de eventos, y `login_events`
    responde "¿cuánta gente entró esta semana?", que el campo suelto no puede."""
    user.last_login_at = datetime.now(UTC)
    db.add(LoginEvent(user_id=user.id, method=method))
    db.commit()


def _as_aware_utc(dt: datetime) -> datetime:
    """Algunos backends (SQLite, usado en tests) devuelven datetimes naive
    incluso en columnas DateTime(timezone=True) tras el roundtrip a la DB.
    Sin esto, comparar contra datetime.now(UTC) revienta con TypeError."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


class WrongPasswordError(Exception):
    pass


class GoogleAuthError(Exception):
    """El ID token de Google no es válido, expiró o no es de esta app."""


def get_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def register_user(db: Session, payload: RegisterIn) -> User | None:
    """Retorna None si el email ya está en uso."""
    if get_by_email(db, payload.email) is not None:
        return None
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email)
    # Las cuentas creadas con Google no tienen contraseña: no se puede entrar
    # por este camino hasta que definan una desde su perfil.
    if user is None or user.hashed_password is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login_with_google(db: Session, credential: str, client_id: str) -> User:
    """Valida el ID token que emitió Google y devuelve el usuario asociado.

    La verificación comprueba la firma de Google, la expiración y que el token
    haya sido emitido para ESTE client_id — sin lo último, un token válido de
    otra aplicación serviría para entrar aquí.
    """
    if not client_id:
        raise GoogleAuthError("El inicio de sesión con Google no está configurado")

    try:
        claims = google_id_token.verify_oauth2_token(
            credential, google_requests.Request(), client_id
        )
    except ValueError as exc:
        raise GoogleAuthError(str(exc)) from exc

    if not claims.get("email_verified", False):
        raise GoogleAuthError("La cuenta de Google no tiene el correo verificado")

    sub = claims["sub"]
    email = claims["email"]
    name = claims.get("name") or email.split("@")[0]
    picture = claims.get("picture")

    user = db.execute(select(User).where(User.google_sub == sub)).scalar_one_or_none()
    if user is None:
        # Mismo correo registrado antes con contraseña: se enlaza la cuenta en
        # lugar de crear una duplicada, así conserva su historial de ensayos.
        user = get_by_email(db, email)
        if user is not None:
            user.google_sub = sub
        else:
            user = User(email=email, name=name, google_sub=sub, hashed_password=None)
            db.add(user)

    user.avatar_url = picture
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, payload: UpdateMeIn) -> User:
    """Lanza WrongPasswordError si se pide cambiar la contraseña sin
    entregar (o con) la contraseña actual correcta."""
    if payload.new_password is not None:
        # Quien entró con Google todavía no tiene contraseña: puede definir una
        # sin dar la anterior, ya que su identidad ya está probada por el JWT.
        if user.hashed_password is not None and (
            payload.current_password is None
            or not verify_password(payload.current_password, user.hashed_password)
        ):
            raise WrongPasswordError
        user.hashed_password = hash_password(payload.new_password)

    if payload.name is not None:
        user.name = payload.name

    if payload.recordatorios_email is not None:
        user.recordatorios_email = payload.recordatorios_email

    db.commit()
    db.refresh(user)
    return user


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def request_password_reset(db: Session, email: str) -> None:
    """No indica si el correo existe: el llamador siempre responde 204,
    exista o no la cuenta, para no filtrar qué correos están registrados."""
    user = get_by_email(db, email)
    if user is None:
        return

    # Cualquier token pendiente anterior queda inválido: solo el link más
    # reciente que se mandó al usuario debe funcionar.
    db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    )

    raw_token = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
        )
    )
    db.commit()

    reset_url = f"{get_settings().frontend_url}/restablecer-contrasena?token={raw_token}"
    # El envío puede fallar, y la respuesta NO puede cambiar por eso: este
    # endpoint contesta igual exista o no la cuenta, y un 500 solo cuando el
    # correo existe delataría cuáles están registradas. El fallo queda en el
    # log y en /api/auth/diagnostico-correo, que es donde sirve.
    try:
        send_email(
            to=user.email,
            subject="Recupera tu contraseña en 1000paes",
            body=(
                f"Hola {user.name},\n\n"
                "Recibimos una solicitud para restablecer tu contraseña en 1000paes.\n"
                f"Este link es válido por {RESET_TOKEN_TTL_MINUTES} minutos y solo se puede usar una vez:\n\n"
                f"{reset_url}\n\n"
                "Si no fuiste tú, ignora este correo: tu contraseña actual sigue funcionando."
            ),
        )
    except CorreoNoEnviado:
        logger.exception("No se pudo enviar el correo de recuperación a %s", user.email)


def reset_password(db: Session, raw_token: str, new_password: str) -> bool:
    """Retorna False si el token no existe, ya se usó o expiró."""
    token = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == _hash_token(raw_token)
        )
    ).scalar_one_or_none()

    if (
        token is None
        or token.used_at is not None
        or _as_aware_utc(token.expires_at) < datetime.now(UTC)
    ):
        return False

    user = db.get(User, token.user_id)
    if user is None:
        return False

    user.hashed_password = hash_password(new_password)
    token.used_at = datetime.now(UTC)
    # Invalida cualquier otro link de reset pendiente para esta cuenta.
    db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.id != token.id,
            PasswordResetToken.used_at.is_(None),
        )
    )
    db.commit()
    return True


def guardar_onboarding(db: Session, user: User, payload) -> User:
    """Guarda las respuestas del cuestionario de bienvenida.

    Marca `onboarding_at` siempre, incluso si el estudiante lo saltó sin
    responder nada: la marca significa "ya se le preguntó", no "respondió". Sin
    esa distinción, a quien lo salta se le vuelve a mostrar en cada inicio de
    sesión, que es la forma más rápida de que alguien deje de entrar.
    """
    from datetime import UTC, datetime

    if payload.pruebas_objetivo:
        user.pruebas_objetivo = ",".join(payload.pruebas_objetivo[:5])
    if payload.curso is not None:
        user.curso = payload.curso
    if payload.primera_vez is not None:
        user.primera_vez = payload.primera_vez
    if payload.puntaje_anterior is not None:
        user.puntaje_anterior = payload.puntaje_anterior
    if payload.horas_semana is not None:
        user.horas_semana = payload.horas_semana

    user.onboarding_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user


def onboarding_de(user: User) -> dict:
    return {
        "pruebas_objetivo": user.pruebas_objetivo.split(",") if user.pruebas_objetivo else [],
        "curso": user.curso,
        "primera_vez": user.primera_vez,
        "puntaje_anterior": user.puntaje_anterior,
        "horas_semana": user.horas_semana,
        "respondido": user.onboarding_at is not None,
    }


def eliminar_cuenta(db: Session, user: User, password: str | None) -> bool:
    """Borra la cuenta y todo lo suyo. False si la contraseña no calza.

    Se BORRA, no se marca como inactiva: la política de privacidad promete
    eliminar los datos personales, y una fila escondida con el correo dentro
    sigue siendo el dato.

    Las visitas de la persona pierden el vínculo con la cuenta pero no se
    borran: son estadística agregada del sitio, y sin user_id ya no la
    identifican. Contarlas de menos falsearía el tráfico histórico.
    """
    if user.hashed_password is not None and (
        not password or not verify_password(password, user.hashed_password)
    ):
        return False

    import paes_api.all_models  # noqa: F401 -- registra los modelos que se borran
    from paes_api.modules.analytics.models import StudyStreak
    from paes_api.modules.billing import service as billing
    from paes_api.modules.billing.models import FlowCustomer, Pago, Subscription
    from paes_api.modules.colegios.models import Colegio
    from paes_api.modules.errores.models import ErrorCliente
    from paes_api.modules.exam_focus.models import (
        ExamAnswer,
        ExamAttempt,
        ExamAttemptQuestion,
    )
    from paes_api.modules.goals.models import MetaUsuario
    from paes_api.modules.metrics.models import PageView
    from paes_api.modules.practice.models import PracticeAnswer
    from paes_api.modules.skill_tree.models import UserSkillProgress

    # ANTES de borrar nada: apagar el cobro recurrente en Flow.
    #
    # Una suscripción viva en la pasarela sobrevive al borrado de la cuenta y
    # sigue cobrándole todos los meses a una tarjeta cuyo dueño ya no tiene
    # dónde entrar a reclamar. Va primero a propósito: si falla, la cuenta NO
    # se borra y queda algo que se puede arreglar, en vez de un cobro fantasma
    # que nadie va a notar hasta que llegue el reclamo.
    billing.cancelar_suscripciones_de_flow(db, user.id)

    intentos = [
        a.id
        for a in db.execute(
            select(ExamAttempt).where(ExamAttempt.user_id == user.id)
        ).scalars()
    ]
    if intentos:
        for tabla in (ExamAnswer, ExamAttemptQuestion):
            db.execute(delete(tabla).where(tabla.attempt_id.in_(intentos)))
    db.execute(delete(ExamAttempt).where(ExamAttempt.user_id == user.id))

    for tabla in (
        UserSkillProgress,
        PracticeAnswer,
        MetaUsuario,
        StudyStreak,
        LoginEvent,
        PasswordResetToken,
        Pago,
        Subscription,
        FlowCustomer,
    ):
        db.execute(delete(tabla).where(tabla.user_id == user.id))

    # El curso que esta persona haya creado NO se borra: adentro hay alumnos
    # que no pidieron nada. Pierde a su creador y sigue en pie, administrado
    # por los profesores que queden.
    db.execute(
        Colegio.__table__.update()
        .where(Colegio.creado_por == user.id)
        .values(creado_por=None)
    )

    # Los errores de JavaScript se conservan sin dueño: son diagnóstico del
    # producto, y sin user_id ya no dicen de quién eran.
    db.execute(
        ErrorCliente.__table__.update()
        .where(ErrorCliente.user_id == user.id)
        .values(user_id=None)
    )

    # La visita se conserva, sin dueño: deja de identificar y sigue contando.
    db.execute(
        PageView.__table__.update()
        .where(PageView.user_id == user.id)
        .values(user_id=None)
    )

    db.execute(delete(User).where(User.id == user.id))
    db.commit()
    return True
