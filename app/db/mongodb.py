from dataclasses import dataclass
from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection

from app.core.config import get_settings


@dataclass(frozen=True)
class Collections:
    """Colecciones de MongoDB que usa la API."""

    apps: Collection
    images: Collection
    changes: Collection


@lru_cache
def get_client() -> MongoClient:
    """Crea un único cliente MongoDB reutilizable durante la vida del proceso."""
    return MongoClient(get_settings().mongodb_uri)


def get_collections() -> Collections:
    """Dependencia de FastAPI; en los tests se sustituye con `app.dependency_overrides`."""
    settings = get_settings()
    db = get_client()[settings.mongodb_database]
    return Collections(
        apps=db[settings.mongodb_collection],
        images=db[settings.mongodb_collection_images],
        changes=db[settings.mongodb_collection_changes],
    )


def close_client() -> None:
    if get_client.cache_info().currsize:
        get_client().close()
        get_client.cache_clear()
