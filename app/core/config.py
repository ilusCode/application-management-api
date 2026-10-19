from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno (y de `.env` en local)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_username: str
    mongodb_password: str
    mongodb_host: str
    mongodb_port: int
    mongodb_database: str
    mongodb_collection_applications: str
    mongodb_collection_images: str
    mongodb_collection_changes: str

    @property
    def mongodb_uri(self) -> str:
        return (
            f"mongodb://{quote_plus(self.mongodb_username)}:{quote_plus(self.mongodb_password)}"
            f"@{self.mongodb_host}:{self.mongodb_port}/"
            "?directConnection=true&serverSelectionTimeoutMS=2000&appName=application-management-api"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
