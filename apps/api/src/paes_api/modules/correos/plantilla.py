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


def cuenta_regresiva(dias: int) -> str:
    if dias <= 0:
        return ""
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="margin:28px 0 8px"><tr>'
        f'<td align="center" bgcolor="{GRAFITO}" style="border-radius:14px;padding:22px 16px">'
        f'<div style="font-family:{FUENTE};font-size:40px;font-weight:700;color:#ffffff;'
        f'letter-spacing:-.02em;line-height:1">{dias}</div>'
        f'<div style="font-family:{FUENTE};font-size:14px;color:#d4d3cf;margin-top:6px">'
        "días para la PAES regular. Cada semana cuenta.</div></td></tr></table>"
    )


def documento(*, url: str, preencabezado: str, cuerpo: str, contacto: str) -> str:
    """El correo completo: logo, tarjeta blanca y pie con la baja.

    `preencabezado` es el texto gris que Gmail muestra junto al asunto en la
    bandeja: se escribe, o el cliente pone lo primero que encuentre.
    """
    logo = f"{url}/apple-icon"
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only"><title>1000paes</title></head>
<body style="margin:0;padding:0;background:{FONDO}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{escape(preencabezado)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{FONDO}">
<tr><td align="center" style="padding:28px 12px">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%">
    <tr><td align="center" style="padding:0 0 20px">
      <a href="{escape(url)}" target="_blank" style="text-decoration:none">
        <img src="{escape(logo)}" width="36" height="36" alt="" style="vertical-align:middle;border:0;border-radius:8px">
        <span style="vertical-align:middle;font-family:{FUENTE};font-size:24px;font-weight:600;color:{GRAFITO};letter-spacing:-.02em;margin-left:8px">1000paes</span>
      </a>
    </td></tr>
    <tr><td bgcolor="{PAPEL}" style="border:1px solid {BORDE};border-radius:16px;padding:36px 36px 28px">
      {cuerpo}
    </td></tr>
    <tr><td align="center" style="padding:24px 24px 8px;font-family:{FUENTE};font-size:12px;line-height:1.7;color:{APAGADO}">
      1000paes — preparación PAES · <a href="{escape(url)}" style="color:{APAGADO}">1000paes.cl</a><br>
      ¿Dudas o sugerencias? Escríbenos a <a href="mailto:{escape(contacto)}" style="color:{APAGADO}">{escape(contacto)}</a><br>
      Recibes este correo porque tienes una cuenta en 1000paes.<br>
      <a href="{escape(url)}/perfil#correos" style="color:{APAGADO}">Dejar de recibir estos correos</a>
    </td></tr>
  </table>
</td></tr></table>
</body></html>"""
