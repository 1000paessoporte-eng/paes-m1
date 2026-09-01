"""Crea en Flow el plan recurrente al que se suscribe cada trial.

    uv run python scripts/crear_plan_flow.py

Se corre UNA vez por ambiente (sandbox y producción son cuentas distintas). Toma
el precio de `PRODUCTOS["pro_mensual"]` y los días de prueba de la configuración,
crea el plan con `plans/create` e imprime el `planId`. Ese id se pone en la
variable de entorno `FLOW_PLAN_ID`, que es lo que lee `service.iniciar_trial`.

POR QUÉ UN SCRIPT Y NO EN RUNTIME
---------------------------------
El plan es una entidad que vive en Flow y se crea una sola vez; crearlo en cada
arranque duplicaría planes o fallaría por id repetido. Igual que el plan de
cuentas de Vercel o el PDF del DEMRE: se hace aparte y su resultado (el id) se
guarda como configuración.

REQUISITOS
----------
`FLOW_API_KEY`, `FLOW_SECRET_KEY` y `FLOW_BASE_URL` configurados (sandbox mientras
se prueba). Sin credenciales, aborta sin tocar nada.

NOTA
----
El valor de `interval` para "mensual" y el nombre exacto de `urlCallback` se
confirman contra el sandbox de Flow: si Flow rechaza el plan, su mensaje dice
qué parámetro no le gustó (el cliente de `flow.py` propaga el texto del error).
"""


from paes_api.core.config import get_settings
from paes_api.modules.billing import flow
from paes_api.modules.billing.service import PRODUCTOS

#: Periodicidad del cobro en Flow. Según su API: 1=diario, 2=semanal, 3=mensual,
#: 4=anual. Se confirma en sandbox; si difiere, se cambia acá.
INTERVAL_MENSUAL = 3


def main() -> int:
    if not flow.esta_configurado():
        print("Flow no está configurado (faltan FLOW_API_KEY / FLOW_SECRET_KEY).")
        return 2

    s = get_settings()
    producto = PRODUCTOS["pro_mensual"]
    plan_id = "pro_mensual"

    print(f"Creando plan '{plan_id}' en {s.flow_base_url} ...")
    print(f"  monto: ${producto.monto} CLP/mes | trial: {s.trial_dias} días")

    api_base = s.api_url.rstrip("/")
    try:
        datos = flow.crear_plan(
            plan_id=plan_id,
            nombre="1000paes Pro mensual",
            monto=producto.monto,
            interval=INTERVAL_MENSUAL,
            trial_period_days=s.trial_dias,
            # Flow avisa acá cada cobro mensual de este plan.
            url_callback=f"{api_base}/api/plan/flow/cobro",
        )
    except flow.FlowError as e:
        print(f"Flow rechazó el plan: {e}")
        return 1

    devuelto = datos.get("planId", plan_id)
    print("\nPlan creado.")
    print(f"  planId: {devuelto}")
    print(f"\nPon esto en el entorno de la API:\n  FLOW_PLAN_ID={devuelto}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
