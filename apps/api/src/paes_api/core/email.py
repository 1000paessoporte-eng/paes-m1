"""Envío de correos transaccionales.

Sin SMTP configurado (smtp_host vacío) el correo se deja solo en el log en vez
de fallar: en DESARROLLO eso es lo correcto, porque el flujo completo se puede
probar sin depender de un proveedor real.

En PRODUCCIÓN no lo es. Ahí ese mismo silencio significa que quien pidió
recuperar su contraseña recibe un "revisa tu correo" por un correo que nunca
salió, y queda fuera de su cuenta para siempre. Por eso el caso se registra
como ERROR y `diagnostico()` lo delata, en vez de quedar en un WARNING que
nadie lee.
"""

import logging
import smtplib
from email.message import EmailMessage

from paes_api.core.config import get_settings

logger = logging.getLogger(__name__)


class CorreoNoEnviado(Exception):
    """No se pudo entregar el correo al proveedor.

    Existe para que quien llama pueda decidir qué hacer. Antes las excepciones
    de smtplib subían crudas hasta el endpoint, que respondía 500 -- y en
    "olvidé mi contraseña" ese 500 delataba que la cuenta existía, porque un
    correo desconocido nunca llegaba a intentar el envío.
    """


def send_email(to: str, subject: str, body: str) -> None:
    """Manda el correo, o lanza CorreoNoEnviado.

    Nunca deja pasar una excepción de smtplib hacia arriba: el detalle del
    fallo va al log, donde sirve, y no a la respuesta, donde filtra.
    """
    settings = get_settings()

    if not settings.smtp_host:
        en_produccion = settings.environment == "production"
        # En producción esto es una configuración rota, no un modo de trabajo.
        (logger.error if en_produccion else logger.warning)(
            "SMTP no configurado%s. Correo NO enviado.\nPara: %s\nAsunto: %s\n\n%s",
            " EN PRODUCCIÓN: nadie puede recuperar su contraseña" if en_produccion else "",
            to,
            subject,
            body,
        )
        if en_produccion:
            raise CorreoNoEnviado("SMTP no configurado")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = to
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as err:
        logger.error("Fallo al enviar correo a %s: %s", to, err)
        raise CorreoNoEnviado(str(err)) from err


def diagnostico() -> dict[str, object]:
    """Si el correo saldría o no, y por qué. Para el panel de administración.

    Existe por la misma razón que el diagnóstico de Flow: configurar un
    proveedor falla siempre por lo mismo --una credencial, un puerto, un host
    mal escrito-- y acá el usuario final NUNCA ve el error, porque "olvidé mi
    contraseña" responde igual exista o no la cuenta. Sin esto, la única forma
    de saber si el correo sale es que alguien se quede fuera y lo reporte.

    NUNCA devuelve la contraseña del SMTP; sí dice si está puesta.
    """
    s = get_settings()
    estado: dict[str, object] = {
        "configurado": bool(s.smtp_host),
        "host": s.smtp_host or None,
        "puerto": s.smtp_port,
        "usuario": s.smtp_user or None,
        "tiene_password": bool(s.smtp_password),
        "remitente": s.smtp_from,
        "entorno": s.environment,
    }

    if not s.smtp_host:
        estado["puede_enviar"] = False
        estado["detalle"] = (
            "SMTP no está configurado. Nadie puede recuperar su contraseña: el "
            "enlace solo queda en los logs del servidor."
        )
        return estado

    # Conexión real: que las variables estén puestas no significa que sirvan.
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if s.smtp_user:
                smtp.login(s.smtp_user, s.smtp_password)
        estado["puede_enviar"] = True
        estado["detalle"] = "Conexión y autenticación correctas."
    except Exception as err:  # noqa: BLE001 -- el detalle es justamente lo que se busca
        estado["puede_enviar"] = False
        estado["detalle"] = f"{type(err).__name__}: {err}"

    return estado
