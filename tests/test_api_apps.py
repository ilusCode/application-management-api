from bson import ObjectId

BASE = "/api/v1"


def _create(client, payload):
    response = client.post(f"{BASE}/app/new", json=payload)
    assert response.status_code == 200
    return response.json()["_id"]


def test_crear_app(client, payload):
    response = client.post(f"{BASE}/app/new", json=payload)

    assert response.status_code == 200
    assert response.json()["statusCode"] == "Ok"
    assert ObjectId.is_valid(response.json()["_id"])


def test_crear_app_payload_invalido(client):
    response = client.post(f"{BASE}/app/new", json={"data": {"name": "sin url"}})

    assert response.status_code == 422


def test_listar_apps_activas_por_defecto(client, payload):
    app_id = _create(client, payload)

    response = client.get(f"{BASE}/apps")

    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {"_id": app_id, "url": "iluscode.local", "name": "Iluscode Server", "description": "Servidor de pruebas"}
        ]
    }


def test_listar_apps_inactivas(client, payload):
    active_id = _create(client, payload)
    inactive_id = _create(client, payload)
    client.put(f"{BASE}/apps/{inactive_id}")

    inactive = client.get(f"{BASE}/apps", params={"status": "INACTIVE"}).json()["data"]
    active = client.get(f"{BASE}/apps", params={"status": "ACTIVE"}).json()["data"]

    assert [a["_id"] for a in inactive] == [inactive_id]
    assert [a["_id"] for a in active] == [active_id]


def test_listar_apps_estado_invalido(client):
    assert client.get(f"{BASE}/apps", params={"status": "FOO"}).status_code == 422


def test_detalle_app(client, payload):
    app_id = _create(client, payload)

    response = client.get(f"{BASE}/apps/{app_id}/details")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["_id"] == app_id
    assert data["active"] is True
    assert data["images"][0] == {
        "_id": data["images"][0]["_id"],
        "applicationId": app_id,
        "url": "https://example.com/icon.svg",
        "type": "icon",
    }
    assert data["changes"][0]["changeType"] == "new"
    assert data["changes"][0]["applicationId"] == app_id


def test_detalle_id_invalido(client):
    response = client.get(f"{BASE}/apps/bad/details")

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid ID format"}


def test_detalle_inexistente(client):
    response = client.get(f"{BASE}/apps/{ObjectId()}/details")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


def test_borrar_app(client, payload):
    app_id = _create(client, payload)

    response = client.put(f"{BASE}/apps/{app_id}")

    assert response.status_code == 200
    assert response.json() == {"app_id": app_id, "message": "App deleted successfully."}
    assert client.get(f"{BASE}/apps/{app_id}/details").json()["data"]["active"] is False


def test_borrar_app_dos_veces(client, payload):
    app_id = _create(client, payload)
    client.put(f"{BASE}/apps/{app_id}")

    response = client.put(f"{BASE}/apps/{app_id}")

    assert response.status_code == 202
    assert response.json() == {"detail": "Application is already inactive"}


def test_borrar_app_inexistente(client):
    assert client.put(f"{BASE}/apps/{ObjectId()}").status_code == 404


def test_cors(client):
    response = client.get(f"{BASE}/apps", headers={"Origin": "http://example.com"})

    assert response.headers["access-control-allow-origin"] == "*"
