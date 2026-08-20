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


class UsoPublicoOut(BaseModel):
    """Cuánto se usa la plataforma, en tres números.

    Es la única prueba social que este proyecto puede mostrar: no hay
    testimonios ni logos de colegios porque no existen (regla 1 del CLAUDE.md).
    Lo que sí existe es el uso real, y se cuenta en la base cada vez que se
    pide.

    Quién decide MOSTRARLO es la portada, no este endpoint: con cifras chicas
    la franja no se dibuja, porque "3 ensayos rendidos" espanta en vez de
    convencer. El endpoint devuelve el dato real y punto.
    """

    #: Ensayos terminados (no los abandonados a medias).
    ensayos_rendidos: int
    #: Respuestas contestadas de verdad, entre ensayo y práctica. Las que se
    #: dejaron en blanco no cuentan: nadie "respondió" una pregunta vacía.
    preguntas_respondidas: int
    #: Personas distintas que terminaron al menos un ensayo.
    alumnos: int
