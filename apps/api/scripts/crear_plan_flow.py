"""Crea (o revisa) el plan de cobro recurrente en Flow.

Se corre UNA vez por ambiente --sandbox y produccion son cuentas distintas con
objetos distintos-- y no desde la aplicacion: un plan es un objeto que vive en
Flow, y crearlo desde el camino normal significaria que un despliegue puede
duplicarlo sin que nadie se entere.

Que hace, en orden:

1. Si el plan ya existe en Flow, lo muestra y no toca nada. Es idempotente a
   proposito: correrlo dos veces por equivocacion no puede terminar en dos
   planes cobrando en paralelo.
2. Si no existe, lo crea con el monto del producto `pro_mensual` --el mismo que
   se cobra suelto, para que no haya dos precios que puedan separarse-- y con
   los dias de prueba de `TRIAL_DIAS`.
3. Imprime la variable de entorno que hay que dejar configurada.

Uso:
    cd apps/api
    FLOW_API_KEY=... FLOW_SECRET_KEY=... FLOW_BASE_URL=https://sandbox.flow.cl/api \
    API_URL=https://milpaes-api.vercel.app \
    uv run python scripts/crear_plan_flow.py

El identificador del plan se pasa con --plan-id; por omision es
`pro-mensual-v1`. Si alguna vez cambia el precio, NO se edita este plan: se
crea uno nuevo con otro identificador y se cambia la variable de entorno. Un
plan editado cambia lo que se le cobra a quien ya estaba suscrito, y esa gente
acepto otro precio.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paes_api.core.config import get_settings
from paes_api.modules.billing import flow
from paes_api.modules.billing.service import PRODUCTO_RECURRENTE, PRODUCTOS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan-id",
        default="pro-mensual-v1",
        help="Identificador del plan en Flow (por omision: pro-mensual-v1)",
    )
    parser.add_argument(
        "--crear",
        action="store_true",
        help="Crear el plan. Sin esta bandera solo informa que hay.",
    )
    args = parser.parse_args()

    settings = get_settings()

    if not flow.esta_configurado():
        print("Faltan FLOW_API_KEY y FLOW_SECRET_KEY. No hay nada que hacer.")
        return 1

    producto = PRODUCTOS[PRODUCTO_RECURRENTE]
    url_callback = f"{settings.api_url.rstrip('/')}/api/plan/flow/suscripcion"

    print(f"Ambiente de Flow : {settings.flow_base_url}")
    print(f"Plan             : {args.plan_id}")
    print(f"Monto            : ${producto.monto:,} CLP al mes".replace(",", "."))
    print(f"Dias de prueba   : {settings.trial_dias}")
    print(f"urlCallback      : {url_callback}")
    print()

    try:
        existente = flow.plan_estado(args.plan_id)
    except flow.FlowError:
        existente = None

    if existente and existente.get("planId"):
        print("El plan YA existe en Flow. No se toca nada.")
        for clave in ("planId", "name", "amount", "interval", "trial_period_days", "status"):
            if clave in existente:
                print(f"  {clave}: {existente[clave]}")
        print()
        _recordatorio(args.plan_id, settings.flow_base_url)
        return 0

    if not args.crear:
        print("El plan NO existe. Volve a correr con --crear para crearlo.")
        return 1

    creado = flow.plan_crear(
        plan_id=args.plan_id,
        nombre="1000paes Pro mensual",
        monto=producto.monto,
        trial_dias=settings.trial_dias,
        url_callback=url_callback,
    )
    print("Plan creado:")
    print(f"  {creado}")
    print()
    _recordatorio(args.plan_id, settings.flow_base_url)
    return 0


def _recordatorio(plan_id: str, base_url: str) -> None:
    ambiente = "PRODUCCION" if "sandbox" not in base_url else "sandbox"
    print(f"Configura esta variable en el ambiente de {ambiente}:")
    print(f"  FLOW_PLAN_PRO_ID={plan_id}")
    print()
    print("Sin ella, /api/plan/trial responde 503 y la web no ofrece la prueba.")


if __name__ == "__main__":
    raise SystemExit(main())
