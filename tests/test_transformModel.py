from datetime import datetime

from bson import ObjectId

from app.model.change import change
from app.model.dataApp import dataApp
from app.model.imageDetails import imageDetails
from app.transform.transformModel import transform_data, transform_data_details


def test_transform_data_convierte_ids_a_texto():
	app_id = ObjectId()
	result = transform_data([{"_id": app_id, "url": "u", "name": "n", "description": "d", "active": True}])

	assert result == [dataApp(_id=str(app_id), url="u", name="n", description="d")]


def test_transform_data_lista_vacia():
	assert transform_data([]) == []


def test_transform_data_details_construye_modelos():
	app_id, image_id, change_id = ObjectId(), ObjectId(), ObjectId()
	now = datetime(2026, 1, 2, 3, 4, 5)

	result = transform_data_details(
		{"_id": app_id, "url": "u", "name": "n", "description": "d", "active": False},
		[{"_id": image_id, "applicationId": str(app_id), "url": "i", "type": "icon", "datetime": now}],
		[{"_id": change_id, "applicationId": str(app_id), "changeType": "new", "datetime": now, "description": "c"}],
	)

	assert result._id == str(app_id)
	assert result.active is False
	assert result.images == [imageDetails(_id=str(image_id), applicationId=str(app_id), url="i", type="icon")]
	assert result.changes == [
		change(_id=str(change_id), applicationId=str(app_id), changeType="new", datetime=str(now), description="c")
	]
