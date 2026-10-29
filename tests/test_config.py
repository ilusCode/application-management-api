import pytest
from pydantic import ValidationError

from app.core.config import Settings

ENV = {
    "MONGODB_USERNAME": "user@x",
    "MONGODB_PASSWORD": "p:ss/word",
    "MONGODB_HOST": "localhost",
    "MONGODB_PORT": "27017",
    "MONGODB_DATABASE": "db",
    "MONGODB_COLLECTION_APPLICATIONS": "apps",
    "MONGODB_COLLECTION_IMAGES": "images",
    "MONGODB_COLLECTION_CHANGES": "changes",
    "MONGODB_AUTH_SOURCE": "admin db",
}


def test_settings_sin_variables_de_entorno(monkeypatch):
    for variable in ENV:
        monkeypatch.delenv(variable, raising=False)

    with pytest.raises(ValidationError, match="mongodb_collection"):
        Settings(_env_file=None)


def test_settings_codifica_credenciales_en_la_uri(monkeypatch):
    for variable, value in ENV.items():
        monkeypatch.setenv(variable, value)

    settings = Settings(_env_file=None)

    assert settings.mongodb_uri.startswith("mongodb://user%40x:p%3Ass%2Fword@localhost:27017/?authSource=admin+db&")
