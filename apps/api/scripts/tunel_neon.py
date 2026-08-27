# -*- coding: utf-8 -*-
"""Túnel local para publicar cuando la red bloquea el puerto 5432.

    uv run python scripts/tunel_neon.py     # escucha en 127.0.0.1:54320

Hay redes domésticas y corporativas que bloquean el 5432 de salida. Cuando eso
pasa, `seed.py` y `sincronizar.py` se quedan colgados en un TimeoutError y no
hay forma de publicar, aunque la API en Vercel llegue a la misma base sin
problema. El 443 al mismo host sí responde, y Neon publica ahí el protocolo
Postgres sobre WebSocket, que es lo que usa su driver serverless.

Este proceso escucha en 127.0.0.1:54320, y cada conexión TCP que recibe la
empalma con un WebSocket a `wss://<host>/v2`, copiando bytes en las dos
direcciones sin mirarlos. Para `seed.py` y `sincronizar.py` eso es una base
Postgres normal en localhost, así que corren sin cambiarles una línea: el
camino a producción sigue siendo el mismo código probado, no uno nuevo.

Con el túnel arriba, la publicación es:

    # terminal 1
    uv run python scripts/tunel_neon.py

    # terminal 2, con la DATABASE_URL real apuntada al túnel
    DATABASE_URL="postgresql+psycopg://USUARIO:CLAVE@127.0.0.1:54320/neondb?sslmode=disable" \
        uv run python scripts/seed.py
    DATABASE_URL="..." uv run python scripts/sincronizar.py --aplicar

`sslmode=disable` es correcto y no baja la seguridad: el tramo que viaja por
internet es el WebSocket, que va cifrado con TLS hasta Neon. Lo que queda en
claro es el tramo de 127.0.0.1 a este proceso, dentro de la misma máquina.

El host se toma de la DATABASE_URL de `apps/api/.env` si está, o de la
variable de entorno NEON_HOST. La contraseña no la lee ni la necesita: la manda
el cliente por dentro del túnel.

Necesita `websockets`, que no es dependencia del proyecto porque esto es una
herramienta de operación y no del runtime:

    uv pip install websockets
"""
import asyncio
import re
import os
import sys
import urllib.parse
from pathlib import Path

import websockets

PUERTO = int(os.environ.get('TUNEL_PUERTO', '54320'))


def host_de_neon():
    """El host de Neon, sin el sufijo -pooler y sin tocar la contraseña."""
    if os.environ.get('NEON_HOST'):
        return os.environ['NEON_HOST']
    env = Path(__file__).resolve().parents[1] / '.env'
    if not env.exists():
        env = Path('.env.prod.local')
    if env.exists():
        m = re.search(r'DATABASE_URL\s*=\s*["\']?([^"\'\n]+)', env.read_text(encoding='utf-8'))
        if m:
            h = urllib.parse.urlparse(m.group(1)).hostname
            if h:
                return h.replace('-pooler', '')
    raise SystemExit(
        'No encuentro el host. Pasa NEON_HOST=ep-....neon.tech o deja un '
        '.env.prod.local con la DATABASE_URL.'
    )


async def empalmar(lector, escritor, host):
    """Une una conexión TCP entrante con un WebSocket a Neon."""
    par = escritor.get_extra_info('peername')
    print(f'  conexión desde {par}', flush=True)
    try:
        async with websockets.connect(
            f'wss://{host}/v2', max_size=None, ping_interval=None
        ) as ws:
            async def hacia_neon():
                while True:
                    datos = await lector.read(65536)
                    if not datos:
                        break
                    await ws.send(datos)

            async def hacia_el_cliente():
                async for datos in ws:
                    escritor.write(datos if isinstance(datos, bytes) else datos.encode())
                    await escritor.drain()

            tareas = [asyncio.create_task(hacia_neon()),
                      asyncio.create_task(hacia_el_cliente())]
            listas, pendientes = await asyncio.wait(
                tareas, return_when=asyncio.FIRST_COMPLETED)
            for t in pendientes:
                t.cancel()
            for t in listas:
                if t.exception():
                    raise t.exception()
    except Exception as e:
        print(f'  se corta: {type(e).__name__}: {str(e)[:120]}', flush=True)
    finally:
        escritor.close()


async def main():
    host = host_de_neon()
    servidor = await asyncio.start_server(
        lambda l, e: empalmar(l, e, host), '127.0.0.1', PUERTO)
    print(f'túnel escuchando en 127.0.0.1:{PUERTO} -> wss://{host}/v2')
    print('ctrl-c para cerrarlo')
    async with servidor:
        await servidor.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\ntúnel cerrado')
