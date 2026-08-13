from pydantic import BaseModel, Field


class PageViewIn(BaseModel):
    """Lo que manda el navegador en cada cambio de página."""

    #: Solo rutas internas. El router rechaza cualquier cosa que no empiece
    #: con "/" para que no se registren URLs ajenas.
    path: str = Field(min_length=1, max_length=255)
    visitor_id: str = Field(min_length=8, max_length=64)
