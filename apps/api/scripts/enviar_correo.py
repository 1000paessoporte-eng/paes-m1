"""Manda un correo escrito a mano a las cuentas registradas.

Existe como script y no como botón en el panel de administración por dos
razones concretas. Una: las funciones de la API mueren a los 30 segundos
(`vercel.json`), y una tanda de correos con pausa entre uno y otro no cabe ahí
sin cortarse a la mitad, dejando al azar quién recibió. Dos: un botón que
escribe a todos los usuarios es un botón que se aprieta sin querer.

El cuerpo se lee de un archivo de texto, no de un argumento: un correo que vale
la pena mandar se escribe, se relee y se corrige, y eso no se hace dentro de
comillas en la terminal.

Uso (SIEMPRE probar primero, la difusión no se puede deshacer):

    # 1. ¿A cuántos y a quiénes? No manda nada.
    uv run python scripts/enviar_correo.py --asunto "..." --cuerpo aviso.txt --prueba

    # 2. Cómo se ve al llegar: se lo manda solo a una dirección tuya.
    uv run python scripts/enviar_correo.py --asunto "..." --cuerpo aviso.txt \
        --solo 1000paessoporte@gmail.com

    # 3. De verdad, a las cuentas que se registraron con su correo.
    uv run python scripts/enviar_correo.py --asunto "..." --cuerpo aviso.txt \
        --publico correo

Contra producción hay que exportar antes DATABASE_URL (la connection string
DIRECTA de Neon, sin `-pooler`) y las variables SMTP_*, igual que para
alembic y seed.py. Sin SMTP configurado el script no manda nada: lo dice y
sale, en vez de reportar 200 envíos que solo ocurrieron en el log.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import paes_api.all_models  # noqa: F401 — registra todos los modelos en Base.metadata
from paes_api.core.config import get_settings
from paes_api.core.database import SessionLocal
from paes_api.core.email import diagnostico
from paes_api.modules.correos import service


def main() -> int:
    parser = argparse.ArgumentParser(description="Manda un correo a las cuentas registradas.")
    parser.add_argument("--asunto", required=True, help="Asunto del correo")
    parser.add_argument(
        "--cuerpo",
        required=True,
        type=Path,
        help="Archivo de texto con el cuerpo del mensaje",
    )
    parser.add_argument(
        "--publico",
        default="todos",
        choices=list(service.PUBLICOS),
        help="A quién: todos, solo quienes se registraron con correo, o solo Google",
    )
    parser.add_argument(
        "--prueba",
        action="store_true",
        help="No manda nada: solo muestra a quién le llegaría",
    )
    parser.add_argument(
        "--solo",
        default=None,
        help="Manda el correo real a una sola dirección, para revisar cómo llega",
    )
    parser.add_argument(
        "--pausa",
        type=float,
        default=1.0,
        help="Segundos entre correo y correo (default 1)",
    )
    args = parser.parse_args()

    if not args.cuerpo.is_file():
        print(f"No existe el archivo {args.cuerpo}")
        return 1
    cuerpo = args.cuerpo.read_text(encoding="utf-8").strip()
    if not cuerpo:
        print(f"{args.cuerpo} está vacío.")
        return 1

    # El pie de baja lo agrega el servicio; acá solo se muestra lo que se
    # escribió, para releerlo una última vez antes de apretar el gatillo.
    print(f"Asunto: {args.asunto}\n")
    print(cuerpo)
    print()

    if not args.prueba:
        estado = diagnostico()
        if not estado.get("puede_enviar"):
            print(f"El correo NO puede salir: {estado.get('detalle')}")
            print("Configura SMTP_HOST/SMTP_USER/SMTP_PASSWORD y vuelve a intentar.")
            return 1

    with SessionLocal() as db:
        if args.solo:
            service.difundir(db, args.asunto, cuerpo, solo=args.solo)
            print(f"Enviado solo a {args.solo}.")
            return 0

        gente = service.destinatarios(db, args.publico)
        print(f"Destinatarios ({args.publico}): {len(gente)}")
        for u in gente:
            print(f"  - {u.email}  ({u.name})")
        print()

        if args.prueba:
            print("Modo prueba: no se mandó nada.")
            return 0

        if not gente:
            print("No hay a quién escribirle.")
            return 0

        # Confirmación a mano: es la última barrera antes de algo irreversible.
        confirmacion = input(f"Escribe SI para mandarlo a {len(gente)} personas: ")
        if confirmacion.strip() != "SI":
            print("Cancelado.")
            return 1

        resultado = service.difundir(
            db, args.asunto, cuerpo, args.publico, pausa=args.pausa
        )
        print(f"Enviados: {resultado['enviados']} · Fallidos: {resultado['fallidos']}")
        return 0 if resultado["fallidos"] == 0 else 1


if __name__ == "__main__":
    print(f"Frontend: {get_settings().frontend_url}")
    raise SystemExit(main())
