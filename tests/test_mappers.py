from datetime import datetime

from bson import ObjectId

from app.schemas.app import AppSummary, Change, Image
from app.services.mappers import to_app_detail, to_app_summaries


def test_to_app_summaries_convierte_ids_a_texto():
    app_id = ObjectId()
    result = to_app_summaries([{"_id": app_id, "url": "u", "name": "n", "description": "d", "active": True}])

    assert result == [AppSummary(id=str(app_id), url="u", name="n", description="d")]


def test_to_app_summaries_lista_vacia():
    assert to_app_summaries([]) == []


def test_to_app_detail_construye_modelos():
    app_id, image_id, change_id = ObjectId(), ObjectId(), ObjectId()
    now = datetime(2026, 1, 2, 3, 4, 5)

    result = to_app_detail(
        {"_id": app_id, "url": "u", "name": "n", "description": "d", "active": False},
        [{"_id": image_id, "applicationId": str(app_id), "url": "i", "type": "icon", "datetime": now}],
        [{"_id": change_id, "applicationId": str(app_id), "changeType": "new", "datetime": now, "description": "c"}],
    )

    assert result.id == str(app_id)
    assert result.active is False
    assert result.images == [Image(id=str(image_id), application_id=str(app_id), url="i", type="icon")]
    assert result.changes == [
        Change(id=str(change_id), application_id=str(app_id), change_type="new", datetime=str(now), description="c")
    ]
