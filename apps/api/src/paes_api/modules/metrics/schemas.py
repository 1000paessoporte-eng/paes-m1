from pydantic import BaseModel, Field


class PageViewIn(BaseModel):
    """Lo que manda el navegador en cada cambio de página."""

    #: Solo rutas internas. El router rechaza cualquier cosa que no empiece
    #: con "/" para que no se registren URLs ajenas.
    path: str = Field(min_length=1, max_length=255)
    visitor_id: str = Field(min_length=8, max_length=64)
    #: `document.referrer` tal como lo ve el navegador. Puede venir vacío
    #: (entrada directa, o el sitio de origen lo oculta). El router se queda
    #: solo con el host y descarta el resto.
    referrer: str | None = Field(default=None, max_length=500)
