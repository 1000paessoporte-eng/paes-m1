"""HTML de los correos, con la identidad de 1000paes.

El HTML de correo no es el de la web: Gmail y Outlook ignoran casi todo el CSS
moderno. Por eso esto se arma con tablas y estilos en línea, sin clases ni
flexbox, y con un ancho fijo de 600 px, que es lo que los clientes muestran sin
escalar.

La identidad es la del sitio: papel y grafito, acromática, y el color reservado
para distinguir las cinco pruebas (`globals.css`, `--prueba-*`). La firma de la
marca es la burbuja del cartón de respuestas, así que los pasos numerados van
dentro de burbujas.

Lo que NO lleva, aunque los correos de otras plataformas lo tengan: testimonios
ni cifras de usuarios. No existen, y las reglas del proyecto prohíben
inventarlos.

Todo texto que venga de una persona --el nombre-- pasa por `escape`.
"""

from html import escape

PAPEL = "#ffffff"
FONDO = "#f7f6f4"
BORDE = "#e4e2dc"
GRAFITO = "#2b2b33"
TINTA = "#17171c"
APAGADO = "#5c5b63"

#: Las cinco pruebas con su color del sitio.
PRUEBAS = (
    ("Competencia Lectora", "#b45309"),
    ("Matemática M1", "#1d4ed8"),
    ("Matemática M2", "#7e22ce"),
    ("Historia y Cs. Sociales", "#9f1239"),
    ("Ciencias", "#0f766e"),
)

FUENTE = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"


def boton(texto: str, enlace: str) -> str:
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" '
        'style="margin:8px auto 24px"><tr>'
        f'<td bgcolor="{GRAFITO}" style="border-radius:999px">'
        f'<a href="{escape(enlace)}" target="_blank" style="display:inline-block;padding:14px 30px;'
        f"font-family:{FUENTE};font-size:15px;font-weight:600;color:#ffffff;text-decoration:none;"
        f'border-radius:999px">{escape(texto)}</a></td></tr></table>'
    )


def titulo(texto: str) -> str:
    return (
        f'<p style="margin:32px 0 12px;font-family:{FUENTE};font-size:12px;font-weight:700;'
        f'letter-spacing:.08em;text-transform:uppercase;color:{APAGADO}">{escape(texto)}</p>'
    )


def parrafo(html_seguro: str) -> str:
    """Un párrafo. Recibe HTML ya escapado por quien lo arma."""
    return (
        f'<p style="margin:0 0 16px;font-family:{FUENTE};font-size:15px;line-height:1.6;'
        f'color:{TINTA}">{html_seguro}</p>'
    )


def cifras(items: list[tuple[str, str]]) -> str:
    """Una fila de números grandes con su etiqueta debajo."""
    celdas = "".join(
        f'<td width="{100 // len(items)}%" align="center" style="padding:18px 6px">'
        f'<div style="font-family:{FUENTE};font-size:26px;font-weight:700;color:{GRAFITO};'
        f'letter-spacing:-.02em">{escape(numero)}</div>'
        f'<div style="font-family:{FUENTE};font-size:12px;line-height:1.4;color:{APAGADO};'
        f'margin-top:4px">{escape(etiqueta)}</div></td>'
        for numero, etiqueta in items
    )
    return (
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'style="background:{FONDO};border-radius:12px;margin:8px 0 4px"><tr>{celdas}</tr></table>'
    )


def pruebas() -> str:
    """Las cinco pruebas como etiquetas de color, igual que en el sitio."""
    etiquetas = "".join(
        f'<span style="display:inline-block;margin:0 6px 8px 0;padding:6px 12px;'
        f"border-radius:999px;border:1px solid {color};font-family:{FUENTE};font-size:13px;"
        f'font-weight:600;color:{color}">{escape(nombre)}</span>'
        for nombre, color in PRUEBAS
    )
    return f'<div style="margin:0 0 8px">{etiquetas}</div>'


def funcion(nombre: str, detalle: str, color: str = GRAFITO) -> str:
    """Una tarjeta con barra de color a la izquierda."""
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="margin:0 0 10px"><tr>'
        f'<td width="4" bgcolor="{color}" style="border-radius:4px 0 0 4px">&nbsp;</td>'
        f'<td style="padding:14px 16px;border:1px solid {BORDE};border-left:0;'
        'border-radius:0 10px 10px 0">'
        f'<div style="font-family:{FUENTE};font-size:15px;font-weight:700;color:{TINTA}">'
        f"{escape(nombre)}</div>"
        f'<div style="font-family:{FUENTE};font-size:14px;line-height:1.55;color:{APAGADO};'
        f'margin-top:4px">{escape(detalle)}</div></td></tr></table>'
    )


def pasos(items: list[tuple[str, str, str | None]]) -> str:
    """Pasos numerados dentro de la burbuja del cartón de respuestas.

    Cada item es (título, detalle, enlace o None).
    """
    filas = []
    for numero, (nombre, detalle, enlace) in enumerate(items, start=1):
        link = (
            f'<br><a href="{escape(enlace)}" target="_blank" style="font-family:{FUENTE};'
            f'font-size:14px;font-weight:600;color:{GRAFITO}">Ir ahora →</a>'
            if enlace
            else ""
        )
        filas.append(
            '<tr><td width="44" valign="top" style="padding:0 0 18px">'
            f'<div style="width:32px;height:32px;border-radius:50%;background:{GRAFITO};'
            f"box-shadow:0 0 0 3px {PAPEL},0 0 0 5px #8a8990;color:#ffffff;text-align:center;"
            f'font-family:{FUENTE};font-size:14px;font-weight:700;line-height:32px">{numero}</div>'
            '</td><td valign="top" style="padding:4px 0 18px">'
            f'<div style="font-family:{FUENTE};font-size:15px;font-weight:700;color:{TINTA}">'
            f"{escape(nombre)}</div>"
            f'<div style="font-family:{FUENTE};font-size:14px;line-height:1.55;color:{APAGADO};'
            f'margin-top:2px">{escape(detalle)}{link}</div></td></tr>'
        )
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        + "".join(filas)
        + "</table>"
    )


def nota(html_seguro: str) -> str:
    """Un recuadro destacado, para los datos útiles."""
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="margin:4px 0 8px"><tr>'
        f'<td style="background:{FONDO};border:1px solid {BORDE};border-radius:12px;'
        f'padding:16px 18px;font-family:{FUENTE};font-size:14px;line-height:1.6;color:{TINTA}">'
        f"{html_seguro}</td></tr></table>"
    )


def cuenta_regresiva(url: str, dias: int, fecha: str) -> str:
    """El reloj animado hasta la PAES (lo dibuja `cuenta_regresiva.gif`).

    El `alt` lleva los días en texto: es lo que ve quien tiene las imágenes
    bloqueadas, que en Outlook y en algunos Gmail de empresa es lo normal.
    """
    if dias <= 0:
        return ""
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'style="margin:32px 0 8px;background:{FONDO};border-radius:16px"><tr>'
        '<td align="center" style="padding:24px 20px 20px">'
        f'<div style="font-family:{FUENTE};font-size:12px;font-weight:700;letter-spacing:.1em;'
        f'text-transform:uppercase;color:{APAGADO};margin-bottom:16px">La PAES regular empieza en</div>'
        f'<img src="{escape(url)}/api/correo/cuenta-regresiva.gif" width="480" '
        f'alt="Quedan {dias} días para la PAES" '
        'style="display:block;width:100%;max-width:480px;height:auto;border:0;margin:0 auto">'
        f'<div style="font-family:{FUENTE};font-size:13px;color:{APAGADO};margin-top:14px">'
        f"{escape(fecha)} · Cada semana de práctica cuenta</div>"
        "</td></tr></table>"
    )


def portada(*, url: str, antetitulo: str, titulo_html: str, bajada: str, boton_texto: str, enlace: str) -> str:
    """La cabecera oscura del correo: logo, titular y botón principal.

    `titulo_html` llega ya escapado (puede traer el nombre en negrita).
    """
    return f"""<tr><td bgcolor="{GRAFITO}" style="background:{GRAFITO};border-radius:20px 20px 0 0;padding:32px 36px 40px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td>
    <a href="{escape(url)}" target="_blank" style="text-decoration:none">
      <img src="{escape(url)}/apple-icon" width="30" height="30" alt="" style="vertical-align:middle;border:0;border-radius:8px">
      <span style="vertical-align:middle;font-family:{FUENTE};font-size:20px;font-weight:600;color:#ffffff;letter-spacing:-.02em;margin-left:8px">1000paes</span>
    </a>
  </td></tr></table>
  <div style="height:36px;line-height:36px">&nbsp;</div>
  <div style="font-family:{FUENTE};font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#a9a8a4">{escape(antetitulo)}</div>
  <h1 style="margin:10px 0 14px;font-family:{FUENTE};font-size:34px;line-height:1.15;font-weight:700;letter-spacing:-.03em;color:#ffffff">{titulo_html}</h1>
  <p style="margin:0 0 28px;font-family:{FUENTE};font-size:16px;line-height:1.6;color:#d4d3cf">{escape(bajada)}</p>
  <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
    <td bgcolor="#ffffff" style="border-radius:999px">
      <a href="{escape(enlace)}" target="_blank" style="display:inline-block;padding:15px 30px;font-family:{FUENTE};font-size:15px;font-weight:700;color:{GRAFITO};text-decoration:none;border-radius:999px">{escape(boton_texto)} →</a>
    </td></tr></table>
</td></tr>"""


def documento(*, url: str, preencabezado: str, portada_html: str, cuerpo: str, contacto: str) -> str:
    """El correo completo: portada oscura, cuerpo blanco y pie con la baja.

    `preencabezado` es el texto gris que Gmail muestra junto al asunto en la
    bandeja: se escribe, o el cliente pone lo primero que encuentre.
    """
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only"><meta name="supported-color-schemes" content="light only">
<title>1000paes</title></head>
<body style="margin:0;padding:0;background:{FONDO}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{escape(preencabezado)}&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{FONDO}">
<tr><td align="center" style="padding:28px 12px">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%">
    {portada_html}
    <tr><td bgcolor="{PAPEL}" style="background:{PAPEL};border:1px solid {BORDE};border-top:0;border-radius:0 0 20px 20px;padding:36px 36px 28px">
      {cuerpo}
    </td></tr>
    <tr><td align="center" style="padding:28px 24px 8px;font-family:{FUENTE};font-size:12px;line-height:1.8;color:{APAGADO}">
      <strong style="color:{GRAFITO}">1000paes</strong> — preparación PAES · <a href="{escape(url)}" style="color:{APAGADO}">1000paes.cl</a><br>
      ¿Dudas o sugerencias? Escríbenos a <a href="mailto:{escape(contacto)}" style="color:{APAGADO}">{escape(contacto)}</a><br>
      Recibes este correo porque tienes una cuenta en 1000paes.<br>
      <a href="{escape(url)}/perfil#correos" style="color:{APAGADO}">Dejar de recibir estos correos</a>
    </td></tr>
  </table>
</td></tr></table>
</body></html>"""
