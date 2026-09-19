"""La cuenta regresiva animada de los correos.

Un correo no puede ejecutar JavaScript, así que un reloj que se mueva solo se
puede hacer de una forma: una imagen GIF que el servidor dibuja en el momento
en que se abre el correo. Cada vez que el cliente la pide, se calcula cuánto
falta desde ESE instante y se dibujan 60 cuadros, uno por segundo. El alumno
ve correr los segundos durante un minuto y el reloj se queda quieto en el
último cuadro (el GIF no se repite: volver atrás sería mentir la hora).

Outlook de escritorio muestra solo el primer cuadro, que igual es la hora
correcta del momento de abrirlo.

La letra es Instrument Sans, la del sitio (licencia OFL, en `fuentes/`).
"""

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from paes_api.modules.goals.service import FECHA_PAES

#: El inicio del día de la PAES en Chile continental. Noviembre cae en horario
#: de verano (UTC-3), así que las 00:00 de Santiago son las 03:00 UTC. Se
#: cuenta hasta que empieza el DÍA, no hasta una hora de citación: esa la da el
#: DEMRE a cada postulante, y inventarla sería un dato falso.
INICIO_PAES = FECHA_PAES.replace(hour=3, minute=0, second=0, microsecond=0)

FUENTE = Path(__file__).parent / "fuentes" / "InstrumentSans.ttf"

#: Se dibuja al doble y el correo lo muestra a la mitad: nítido en pantallas
#: retina, que son casi todos los teléfonos.
ANCHO, ALTO = 1040, 250
CUADROS = 60

#: El mismo papel de la caja del correo (`plantilla.FONDO`): si no, el GIF se
#: ve como un rectángulo pegado.
PAPEL = (247, 246, 244)
GRAFITO = (43, 43, 51)
GRAFITO_CLARO = (62, 62, 72)
BLANCO = (255, 255, 255)
APAGADO = (92, 91, 99)
ETIQUETAS = ("DÍAS", "HORAS", "MINUTOS", "SEGUNDOS")


@lru_cache(maxsize=8)
def _fuente(tamano: int, peso: int) -> ImageFont.FreeTypeFont:
    fuente = ImageFont.truetype(str(FUENTE), tamano)
    try:
        fuente.set_variation_by_axes([100, peso])  # ancho normal, peso pedido
    except OSError:
        pass  # sin soporte de ejes variables: se queda en el peso por defecto
    return fuente


def _cajas() -> list[tuple[int, int, int, int]]:
    """Las cuatro tarjetas del reloj, repartidas a lo ancho."""
    separacion = 24
    ancho = (ANCHO - separacion * 3) // 4
    return [
        (i * (ancho + separacion), 0, i * (ancho + separacion) + ancho, 188)
        for i in range(4)
    ]


@lru_cache(maxsize=1)
def _fondo() -> Image.Image:
    """Lo que no cambia entre cuadros: las tarjetas y sus etiquetas."""
    img = Image.new("RGB", (ANCHO, ALTO), PAPEL)
    d = ImageDraw.Draw(img)
    etiqueta = _fuente(26, 600)
    for (x0, y0, x1, y1), texto in zip(_cajas(), ETIQUETAS, strict=True):
        d.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=GRAFITO)
        # La línea del medio, como en los relojes de paletas.
        d.line((x0 + 2, (y0 + y1) // 2, x1 - 2, (y0 + y1) // 2), fill=GRAFITO_CLARO, width=3)
        d.text(((x0 + x1) // 2, 222), texto, font=etiqueta, fill=APAGADO, anchor="mm")
    return img


def _partes(restante: timedelta) -> tuple[int, int, int, int]:
    total = max(0, int(restante.total_seconds()))
    dias, resto = divmod(total, 86400)
    horas, resto = divmod(resto, 3600)
    minutos, segundos = divmod(resto, 60)
    return dias, horas, minutos, segundos


def _cuadro(valores: tuple[int, int, int, int]) -> Image.Image:
    img = _fondo().copy()
    d = ImageDraw.Draw(img)
    numero = _fuente(104, 700)
    for (x0, y0, x1, y1), valor in zip(_cajas(), valores, strict=True):
        d.text(((x0 + x1) // 2, (y0 + y1) // 2 + 2), f"{valor:02d}", font=numero, fill=BLANCO, anchor="mm")
    return img


def gif(ahora: datetime | None = None) -> bytes:
    """El GIF de 60 cuadros desde `ahora` hasta el inicio de la PAES."""
    ahora = ahora or datetime.now(UTC)
    cuadros = [_cuadro(_partes(INICIO_PAES - ahora - timedelta(seconds=i))) for i in range(CUADROS)]

    # Una sola paleta para todos los cuadros: si cada uno eligiera la suya, el
    # borde suavizado de los números parpadearía de un segundo al otro.
    paleta = cuadros[0].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    indexados = [c.quantize(palette=paleta, dither=Image.Dither.NONE) for c in cuadros]

    salida = BytesIO()
    indexados[0].save(
        salida,
        format="GIF",
        save_all=True,
        append_images=indexados[1:],
        duration=1000,
        optimize=True,
        disposal=1,
    )
    return salida.getvalue()
