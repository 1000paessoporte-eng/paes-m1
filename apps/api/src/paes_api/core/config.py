from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = "change-me"
    #: Client ID de la app de Google (OAuth 2.0). Vacío desactiva el login con
    #: Google: la API rechaza /auth/google y la web no muestra el botón.
    google_client_id: str = ""
    database_url: str = "postgresql+psycopg://paes:paes@localhost:5432/paes_m1"

    @field_validator("database_url")
    @classmethod
    def _usar_driver_psycopg(cls, v: str) -> str:
        # Proveedores gestionados (Neon, etc.) entregan connection strings con
        # el esquema generico "postgresql://", que SQLAlchemy resuelve al
        # driver psycopg2 -- no instalado en este proyecto (se usa psycopg 3).
        if v.startswith("postgresql://"):
            return "postgresql+psycopg://" + v[len("postgresql://") :]
        return v
    #: Origen público del frontend, para armar el link de "restablecer
    #: contraseña" que se manda por correo.
    frontend_url: str = "http://localhost:3000"
    #: SMTP para enviar correos transaccionales (recuperación de contraseña).
    #: smtp_host vacío = no hay proveedor configurado: el correo solo se deja
    #: en el log, útil para desarrollo local sin depender de un proveedor real.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "1000paes <no-responder@1000paes.cl>"
    #: Origen público de esta API. Flow necesita una URL alcanzable desde
    #: internet para avisar que un pago se completó, y esa URL no puede
    #: derivarse de la petición del usuario: la fija el despliegue.
    api_url: str = "http://localhost:8000"
    #: Credenciales de Flow, la pasarela de pago. Vacías desactivan el cobro
    #: por completo: la API rechaza /plan/pagar y la web no muestra el botón.
    #: Nunca van al repo —es público—: se cargan como variables de entorno.
    flow_api_key: str = ""
    flow_secret_key: str = ""
    #: Sandbox mientras se prueba, producción cuando se cobra de verdad. El
    #: valor por defecto es el de pruebas a propósito: si alguien despliega sin
    #: configurarlo, cobra en un ambiente falso en vez de cobrarle a una
    #: persona real.
    flow_base_url: str = "https://sandbox.flow.cl/api"
    #: Secreto compartido con el cron que dispara los recordatorios. Vacío deja
    #: el endpoint cerrado: sin él no hay forma de gatillar correos masivos.
    cron_secret: str = ""
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://192.168.1.11:3000",
        "https://healing-aims-photographs-guaranteed.trycloudflare.com",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
