"""Otorga o quita el rol de administrador a una cuenta.

No existe forma de volverse admin desde la web a propósito: el panel expone
datos de todas las personas registradas, así que el rol solo se da a mano,
con acceso a la base.

Uso:
    uv run python scripts/make_admin.py correo@ejemplo.cl
    uv run python scripts/make_admin.py correo@ejemplo.cl --quitar
    uv run python scripts/make_admin.py --listar

Si la cuenta todavía no existe, se puede crear en el momento:
    uv run python scripts/make_admin.py correo@ejemplo.cl --crear --nombre "Matías" --password "..."

Contra producción hay que exportar antes la connection string DIRECTA de Neon
(la que no lleva `-pooler`), igual que para alembic y seed.py.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import select

import paes_api.all_models  # noqa: F401 — registra todos los modelos en Base.metadata
from paes_api.core.database import SessionLocal
from paes_api.core.security import hash_password
from paes_api.modules.users.models import User


def listar(db) -> int:
    admins = db.execute(select(User).where(User.is_admin.is_(True)).order_by(User.id)).scalars().all()
    if not admins:
        print("No hay ninguna cuenta admin.")
        return 0
    print(f"{len(admins)} cuenta(s) admin:")
    for u in admins:
        print(f"  - {u.email}  ({u.name}, id={u.id})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gestiona el rol de administrador.")
    parser.add_argument("email", nargs="?", help="Correo de la cuenta")
    parser.add_argument("--quitar", action="store_true", help="Quita el rol en vez de darlo")
    parser.add_argument("--listar", action="store_true", help="Muestra los admins actuales")
    parser.add_argument("--crear", action="store_true", help="Crea la cuenta si no existe")
    parser.add_argument("--nombre", default=None, help="Nombre, solo con --crear")
    parser.add_argument("--password", default=None, help="Contraseña, solo con --crear")
    args = parser.parse_args()

    with SessionLocal() as db:
        if args.listar:
            return listar(db)

        if not args.email:
            parser.error("falta el correo (o usa --listar)")

        user = db.execute(select(User).where(User.email == args.email)).scalar_one_or_none()

        if user is None:
            if not args.crear:
                print(f"No existe ninguna cuenta con {args.email}.")
                print("Regístrala en la web, o repite con --crear --nombre ... --password ...")
                return 1
            if not args.password:
                print("--crear necesita --password (mínimo 8 caracteres).")
                return 1
            if len(args.password) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
                return 1
            user = User(
                email=args.email,
                name=args.nombre or args.email.split("@")[0],
                hashed_password=hash_password(args.password),
            )
            db.add(user)
            print(f"Cuenta creada: {args.email}")

        user.is_admin = not args.quitar
        db.commit()

        estado = "ya NO es admin" if args.quitar else "ahora es admin"
        print(f"{user.email} {estado}.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
