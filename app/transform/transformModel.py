from app.model.change import change
from app.model.dataApp import dataApp
from app.model.dataAppDetails import dataAppDetails
from app.model.imageDetails import imageDetails


def transform_data_details(rData: dict, lImages: list, lChanges: list) -> dataAppDetails:
	images = [
		imageDetails(
			_id=str(image["_id"]),
			applicationId=str(image["applicationId"]),
			url=str(image["url"]),
			type=str(image["type"]),
		)
		for image in lImages
	]
	changes = [
		change(
			_id=str(item["_id"]),
			applicationId=str(item["applicationId"]),
			changeType=str(item["changeType"]),
			datetime=str(item["datetime"]),
			description=str(item["description"]),
		)
		for item in lChanges
	]
	return dataAppDetails(
		_id=str(rData["_id"]),
		url=rData["url"],
		name=rData["name"],
		description=rData["description"],
		images=images,
		active=rData["active"],
		changes=changes,
	)


def transform_data(rData: list) -> list:
	return [
		dataApp(
			_id=str(item["_id"]),
			url=item["url"],
			name=item["name"],
			description=item["description"],
		)
		for item in rData
	]
