from fastapi import APIRouter, Response

from paes_api.modules.correos import cuenta_regresiva

router = APIRouter(prefix="/correo", tags=["correo"])


@router.get("/cuenta-regresiva.gif", include_in_schema=False)
def cuenta_regresiva_gif() -> Response:
    """El reloj animado hasta la PAES que va dentro de los correos.

    Público y sin sesión: lo pide el cliente de correo del alumno, que no manda
    cookies ni token. No revela nada: es la misma fecha que dice la portada.

    `no-store` porque el reloj tiene que marcar la hora del momento en que se
    abre el correo, no la de la primera vez que alguien lo abrió.
    """
    return Response(
        content=cuenta_regresiva.gif(),
        media_type="image/gif",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )
