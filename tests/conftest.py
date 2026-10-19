import mongomock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import managerService

COLLECTIONS = {
    "MONGODB_COLLECTION": "apps",
    "MONGODB_COLLECTION_IMAGES": "images",
    "MONGODB_COLLECTION_CHANGES": "changes",
}


@pytest.fixture
def db(monkeypatch):
    for variable, name in COLLECTIONS.items():
        monkeypatch.setenv(variable, name)
    database = mongomock.MongoClient()["test"]
    monkeypatch.setattr(managerService, "connect_to_mongodb", lambda: database)
    return database


@pytest.fixture
def client(db):
    return TestClient(app)


@pytest.fixture
def payload():
    return {
        "data": {
            "url": "iluscode.local",
            "name": "Iluscode Server",
            "description": "Servidor de pruebas",
            "images": [{"url": "https://example.com/icon.svg", "type": "icon"}],
        }
    }
