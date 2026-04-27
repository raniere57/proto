from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://admin:qualidade%40trunks.57@187.62.153.52:5432/novo_protocolamento"
    DATABASE_URL_SYNC: str = "postgresql://admin:qualidade@trunks.57@187.62.153.52:5432/novo_protocolamento"

    # JWT
    SECRET_KEY: str = "proto-rebuild-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # General
    DEBUG: bool = True

    # HubSoft OAuth
    HUBSOFT_CLIENT_ID: str = "103"
    HUBSOFT_CLIENT_SECRET: str = ""
    HUBSOFT_USERNAME: str = ""
    HUBSOFT_PASSWORD: str = ""

    # HubSoft Database (import)
    HUBSOFT_DB_HOST: str = "177.10.118.77"
    HUBSOFT_DB_PORT: int = 9432
    HUBSOFT_DB_NAME: str = "hubsoft"
    HUBSOFT_DB_USER: str = "mega_leitura"
    HUBSOFT_DB_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
