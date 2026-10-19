import pytest
from bson import ObjectId

from app.exception.IcException import IcException
from app.model.appDetailsRequest import appDetailsRequest
from app.model.dataAppRequest import dataAppRequest
from app.model.newImage import newImage
from app.model.serviceStatusEnum import serviceStatus
from app.services import managerService
from app.utils.Constants import ERR_01, ERR_02, ERR_03


def _new_request(images=None):
    return appDetailsRequest(
        data=dataAppRequest(url="u", name="App", description="d", images=images or [])
    )


@pytest.mark.parametrize("app_id", ["", "bad", "123"])
def test_get_object_id_invalido(app_id):
    with pytest.raises(IcException) as error:
        managerService._get_object_id(app_id)
    assert error.value.status_code == 400
    assert error.value.detail == ERR_01


def test_collection_sin_variable_de_entorno(monkeypatch, db):
    monkeypatch.delenv("MONGODB_COLLECTION")
    with pytest.raises(RuntimeError, match="MONGODB_COLLECTION"):
        managerService._collection(db, "MONGODB_COLLECTION")


def test_connect_sin_variables_de_entorno(monkeypatch):
    for variable in ("MONGODB_USERNAME", "MONGODB_PASSWORD", "MONGODB_HOST", "MONGODB_PORT", "MONGODB_DATABASE"):
        monkeypatch.delenv(variable, raising=False)
    managerService.connect_to_mongodb.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="Missing required MongoDB"):
            managerService.connect_to_mongodb()
    finally:
        managerService.connect_to_mongodb.cache_clear()


def test_new_application_guarda_app_imagenes_y_cambio(db):
    result = managerService.newApplication(_new_request([newImage(url="i1", type="icon"), newImage(url="i2", type="bg")]))

    app_id = result["_id"]
    stored = db.apps.find_one({"_id": ObjectId(app_id)})
    assert result["statusCode"] == "Ok"
    assert stored["active"] is True
    assert len(stored["images"]) == 2
    assert db.images.count_documents({"applicationId": app_id}) == 2
    change = db.changes.find_one({"applicationId": app_id})
    assert change["changeType"] == "new"
    assert stored["changes"] == [str(change["_id"])]


def test_new_application_sin_imagenes(db):
    app_id = managerService.newApplication(_new_request())["_id"]

    assert db.apps.find_one({"_id": ObjectId(app_id)})["images"] == []
    assert db.images.count_documents({}) == 0


def test_get_app_list_filtra_por_estado(db):
    active_id = managerService.newApplication(_new_request())["_id"]
    inactive_id = managerService.newApplication(_new_request())["_id"]
    managerService.deleteAppById(inactive_id)

    assert [a._id for a in managerService.getAppList(serviceStatus.ACTIVE).data] == [active_id]
    assert [a._id for a in managerService.getAppList(serviceStatus.INACTIVE).data] == [inactive_id]
    assert [a._id for a in managerService.getAppList().data] == [active_id]


def test_get_app_details(db):
    app_id = managerService.newApplication(_new_request([newImage(url="i", type="icon")]))["_id"]

    details = managerService.getAppDetailsById(app_id).data

    assert details._id == app_id
    assert [image.url for image in details.images] == ["i"]
    assert [change.changeType for change in details.changes] == ["new"]


def test_get_app_details_inexistente(db):
    with pytest.raises(IcException) as error:
        managerService.getAppDetailsById(str(ObjectId()))
    assert error.value.status_code == 404
    assert error.value.detail == ERR_03


def test_delete_app_desactiva_y_registra_cambio(db):
    app_id = managerService.newApplication(_new_request())["_id"]

    result = managerService.deleteAppById(app_id)

    stored = db.apps.find_one({"_id": ObjectId(app_id)})
    assert result == {"app_id": app_id, "message": "App deleted successfully."}
    assert stored["active"] is False
    assert [c["changeType"] for c in db.changes.find({"applicationId": app_id})] == ["new", "delete"]
    assert len(stored["changes"]) == 2


def test_delete_app_ya_inactiva(db):
    app_id = managerService.newApplication(_new_request())["_id"]
    managerService.deleteAppById(app_id)

    with pytest.raises(IcException) as error:
        managerService.deleteAppById(app_id)
    assert error.value.status_code == 202
    assert error.value.detail == ERR_02
    assert db.changes.count_documents({"applicationId": app_id, "changeType": "delete"}) == 1


def test_delete_app_inexistente(db):
    with pytest.raises(IcException) as error:
        managerService.deleteAppById(str(ObjectId()))
    assert error.value.status_code == 404
    assert error.value.detail == ERR_03
