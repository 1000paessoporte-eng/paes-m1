from slowapi import Limiter
from slowapi.util import get_remote_address

#: Limiter compartido por toda la API, keyed por IP remota. Los limites
#: concretos se aplican por endpoint via @limiter.limit(...) — ver
#: modules/users/router.py para los endpoints de auth (login, registro,
#: recuperacion de contrasena), que son los mas expuestos a fuerza bruta
#: y abuso de envio de correos.
limiter = Limiter(key_func=get_remote_address)
