"""Envío de correos transaccionales.

Sin SMTP configurado (smtp_host vacío) el correo se deja solo en el log en
vez de fallar: mismo patrón que google_client_id vacío en auth — el flujo
completo se puede probar en desarrollo local sin depender de un proveedor
real de correo."""

import logging
import smtplib
from email.message import EmailMessage

from paes_api.core.config import get_settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    settings = get_settings()

    if not settings.smtp_host:
        # WARNING (no INFO) a propósito: el nivel por defecto de logging es
        # WARNING, y este mensaje es el único lugar donde queda el link de
        # reset en desarrollo sin SMTP — si quedara en INFO, no se vería.
        logger.warning(
            "SMTP no configurado, correo no enviado.\nPara: %s\nAsunto: %s\n\n%s", to, subject, body
        )
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = to
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)
