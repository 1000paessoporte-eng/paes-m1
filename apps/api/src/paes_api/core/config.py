from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = "change-me"
    database_url: str = "postgresql+psycopg://paes:paes@localhost:5432/paes_m1"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://192.168.1.11:3000",
        "https://healing-aims-photographs-guaranteed.trycloudflare.com",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
