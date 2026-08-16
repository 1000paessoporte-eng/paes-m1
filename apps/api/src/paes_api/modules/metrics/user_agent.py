"""Reduce un user agent a tres categorías gruesas.

No es identificación: es lo mínimo para responder si dos visitas vinieron de
equipos distintos. Se guarda "Windows" y no la cadena completa —que incluye
versiones exactas de sistema y navegador y sirve para fabricar una huella
digital— porque la pregunta del panel es cuánta diversidad hay, no quién es
cada uno.

Se resuelve con búsquedas de subcadena en vez de una librería de parsing: la
precisión que se necesita acá es la de un histograma, y una dependencia más
en la API se paga en cada despliegue.
"""

#: El orden importa: Edge y Opera se anuncian como Chrome, y Chrome se anuncia
#: como Safari. Quien evalúe primero gana, así que van del más específico al
#: más genérico.
NAVEGADORES: list[tuple[str, str]] = [
    ("edg/", "Edge"),
    ("opr/", "Opera"),
    ("samsungbrowser", "Samsung"),
    ("firefox/", "Firefox"),
    ("chrome/", "Chrome"),
    ("safari/", "Safari"),
]

SISTEMAS: list[tuple[str, str]] = [
    # Android antes que Linux: todo Android dice también "linux".
    ("android", "Android"),
    ("iphone", "iOS"),
    ("ipad", "iPadOS"),
    ("windows", "Windows"),
    ("mac os x", "macOS"),
    ("cros", "ChromeOS"),
    ("linux", "Linux"),
]

MOVILES = ("iphone", "android", "mobile", "windows phone")
TABLETS = ("ipad", "tablet")


def clasificar(user_agent: str | None) -> tuple[str | None, str | None, str | None]:
    """(dispositivo, sistema, navegador). Cualquiera puede ser None."""
    if not user_agent:
        return None, None, None
    ua = user_agent.lower()

    if any(t in ua for t in TABLETS):
        device = "tablet"
    elif any(m in ua for m in MOVILES):
        device = "movil"
    else:
        device = "escritorio"

    sistema = next((nombre for clave, nombre in SISTEMAS if clave in ua), None)
    navegador = next((nombre for clave, nombre in NAVEGADORES if clave in ua), None)
    return device, sistema, navegador


#: Marcas inequívocas de tráfico automatizado en el user agent.
#:
#: La lista es deliberadamente conservadora: solo entra lo que se identifica a
#: sí mismo como robot. Un bot que miente su user agent seguirá contándose como
#: persona, y está bien: es preferible sobrecontar un poco a descartar visitas
#: reales por una heurística agresiva. El panel de administración existe para
#: decidir dónde invertir, y para eso un número inflado engaña menos que uno que
#: silenciosamente borra usuarios.
ROBOTS = (
    "bot",
    "crawl",
    "spider",
    "slurp",
    "headless",
    "python-requests",
    "curl/",
    "wget",
    "scrapy",
    "facebookexternalhit",
    "whatsapp",
    "telegrambot",
    "preview",
    "monitor",
    "pingdom",
    "lighthouse",
)


def es_robot(user_agent: str | None) -> bool:
    """Si la visita viene de un rastreador que se declara como tal.

    Importa más de lo que parece: en la primera medición real del proyecto, 18
    de 27 "visitantes" habían entrado una sola vez y solo a la portada, que es
    la huella típica de un rastreador. Contarlos como personas inflaba el
    número que se usa para decidir dónde invertir.
    """
    if not user_agent:
        # Un navegador siempre manda user agent. Su ausencia es, por sí sola,
        # señal de cliente automatizado.
        return True
    ua = user_agent.lower()
    return any(marca in ua for marca in ROBOTS)
