from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from paes_api.shared.base import Base


class PageView(Base):
    """Una visita a una página, incluida la de gente sin cuenta.

    Por qué propio y no solo Vercel Analytics: el panel de administración
    necesita cruzar visitas con registros y ensayos en la misma consulta, y
    Vercel no expone esos datos por API en el plan actual.

    Deliberadamente NO se guarda dirección IP ni el user agent completo. Para
    saber "cuántas personas entran" basta un identificador aleatorio de
    navegador, y no guardar el dato es la única forma segura de no filtrarlo.

    Sí se guardan tres categorías GRUESAS derivadas del user agent —tipo de
    dispositivo, sistema operativo y navegador— porque sin ellas era imposible
    distinguir 27 personas distintas de una sola persona probando el sitio en
    varias pestañas. Son buckets ("móvil", "Windows", "Chrome"), no la cadena
    original: sirven para leer diversidad, no para reconocer a nadie."""

    __tablename__ = "page_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    #: Ruta interna ("/", "/examen"). Nunca la URL completa: los parámetros de
    #: consulta pueden traer tokens (ej. el de restablecer contraseña).
    path: Mapped[str] = mapped_column(String(255), index=True)
    #: Identificador aleatorio generado en el navegador y guardado ahí mismo.
    #: No identifica a una persona, solo permite no contar diez veces a quien
    #: navega por diez páginas.
    visitor_id: Mapped[str] = mapped_column(String(64), index=True)
    #: Presente solo si la visita ocurrió con sesión iniciada.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    #: "movil", "escritorio" o "tablet". NULL en las visitas anteriores a que
    #: se empezara a registrar.
    device: Mapped[str | None] = mapped_column(String(20), nullable=True)
    #: Familia del sistema operativo: "Windows", "Android", "iOS", "macOS"...
    os: Mapped[str | None] = mapped_column(String(20), nullable=True)
    #: Familia del navegador: "Chrome", "Safari", "Firefox", "Edge"...
    browser: Mapped[str | None] = mapped_column(String(20), nullable=True)
    #: Dominio desde el que se llegó ("google.com", "instagram.com"). Solo el
    #: HOST, nunca la URL completa: para saber por qué canal llega la gente
    #: basta el dominio, y la ruta ajena puede llevar términos de búsqueda o
    #: identificadores de campaña que no hay razón para almacenar.
    #: NULL cuando se entró directo o el navegador no lo informó.
    referrer: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    #: Si la visita viene de un rastreador declarado. Se guarda en vez de
    #: descartarse: un bot que entra igual es información sobre el sitio, y
    #: borrarlo impediría notar después que la heurística estaba mal.
    es_bot: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # ── Campaña de origen ───────────────────────────────────────────────
    # Los cuatro parámetros UTM tal como venían en la URL de entrada, y solo
    # en la vista de entrada: en las navegaciones internas quedan NULL porque
    # no los hay.
    #
    # Existen para una pregunta concreta que el referrer no puede responder:
    # qué anuncio trajo a quien terminó pagando. El navegador interno de
    # Instagram muchas veces no manda referrer, así que esas visitas caían en
    # el mismo balde que un amigo pasando el link; y aunque llegara
    # "instagram.com", todos los anuncios se veían iguales.
    #
    # Son etiquetas de campaña que escribe quien arma el anuncio, no datos de
    # la persona. Se acotan a 100 caracteres al guardar: vienen de la URL, o
    # sea de fuera, y una etiqueta legítima no pasa de unas pocas palabras.
    utm_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(100), nullable=True)
    #: El nombre de la campaña. Indexado: el panel agrupa por él.
    utm_campaign: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    #: La creatividad o variante concreta del anuncio.
    utm_content: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
