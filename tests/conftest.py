import mongomock
import pytest
from fastapi.testclient import TestClient

from app.db.mongodb import Collections, get_collections
from app.main import app


@pytest.fixture
def collections():
    database = mongomock.MongoClient()["test"]
    return Collections(apps=database.apps, images=database.images, changes=database.changes)


@pytest.fixture
def client(collections):
    app.dependency_overrides[get_collections] = lambda: collections
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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
