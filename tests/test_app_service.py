import pytest
from bson import ObjectId

from app.core.exceptions import AppAlreadyInactiveError, AppNotFoundError, InvalidIdError
from app.schemas.app import AppCreate, AppStatus, NewImage
from app.services import app_service


def _new_app(images=None):
    return AppCreate(url="u", name="App", description="d", images=images or [])


@pytest.mark.parametrize("app_id", ["", "bad", "123"])
def test_to_object_id_invalido(app_id):
    with pytest.raises(InvalidIdError, match="Invalid ID format"):
        app_service.to_object_id(app_id)


def test_create_application_guarda_app_imagenes_y_cambio(collections):
    result = app_service.create_application(
        collections, _new_app([NewImage(url="i1", type="icon"), NewImage(url="i2", type="bg")])
    )

    app_id = result.id
    stored = collections.apps.find_one({"_id": ObjectId(app_id)})
    assert result.status_code == "Ok"
    assert stored["active"] is True
    assert len(stored["images"]) == 2
    assert collections.images.count_documents({"applicationId": app_id}) == 2
    change = collections.changes.find_one({"applicationId": app_id})
    assert change["changeType"] == "new"
    assert stored["changes"] == [str(change["_id"])]


def test_create_application_sin_imagenes(collections):
    app_id = app_service.create_application(collections, _new_app()).id

    assert collections.apps.find_one({"_id": ObjectId(app_id)})["images"] == []
    assert collections.images.count_documents({}) == 0


def test_list_applications_filtra_por_estado(collections):
    active_id = app_service.create_application(collections, _new_app()).id
    inactive_id = app_service.create_application(collections, _new_app()).id
    app_service.deactivate_application(collections, inactive_id)

    assert [a.id for a in app_service.list_applications(collections, AppStatus.ACTIVE).data] == [active_id]
    assert [a.id for a in app_service.list_applications(collections, AppStatus.INACTIVE).data] == [inactive_id]
    assert [a.id for a in app_service.list_applications(collections).data] == [active_id]


def test_get_application(collections):
    app_id = app_service.create_application(collections, _new_app([NewImage(url="i", type="icon")])).id

    details = app_service.get_application(collections, app_id).data

    assert details.id == app_id
    assert [image.url for image in details.images] == ["i"]
    assert [change.change_type for change in details.changes] == ["new"]


def test_get_application_inexistente(collections):
    with pytest.raises(AppNotFoundError, match="Application not found"):
        app_service.get_application(collections, str(ObjectId()))


def test_deactivate_application_desactiva_y_registra_cambio(collections):
    app_id = app_service.create_application(collections, _new_app()).id

    result = app_service.deactivate_application(collections, app_id)

    stored = collections.apps.find_one({"_id": ObjectId(app_id)})
    assert result.app_id == app_id
    assert result.message == "App deleted successfully."
    assert stored["active"] is False
    assert [c["changeType"] for c in collections.changes.find({"applicationId": app_id})] == ["new", "delete"]
    assert len(stored["changes"]) == 2


def test_deactivate_application_ya_inactiva(collections):
    app_id = app_service.create_application(collections, _new_app()).id
    app_service.deactivate_application(collections, app_id)

    with pytest.raises(AppAlreadyInactiveError, match="Application is already inactive"):
        app_service.deactivate_application(collections, app_id)
    assert collections.changes.count_documents({"applicationId": app_id, "changeType": "delete"}) == 1


def test_deactivate_application_inexistente(collections):
    with pytest.raises(AppNotFoundError):
        app_service.deactivate_application(collections, str(ObjectId()))
