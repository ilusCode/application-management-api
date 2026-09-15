from model.dataApp import dataApp
from model.dataAppDetails import dataAppDetails


def transform_data_details(rData: dict, lImages: list, lChanges: list) -> dataAppDetails:
	new_images = []

	for image in lImages:
		image_data = {}
		image_data['_id'] = str(image['_id'])
		image_data['url'] = str(image['url'])
		image_data['type'] = str(image['type'])
		image_data['datetime'] = str(image['datetime'])
		new_images.append(image_data)

	new_changes = []
	for change in lChanges:
		change_data = {}
		change_data['_id'] = str(change['_id'])
		change_data['action'] = str(change['changeType'])
		change_data['datetime'] = str(change['datetime'])
		change_data['description'] = str(change['description'])
		new_changes.append(change_data)

	response = dataAppDetails(
        _id=str(rData["_id"]),
        url=rData["url"],
        name=rData["name"],
        description=rData["description"],
        images=new_images,
		changes=new_changes,
		active=rData["active"],
    )
	return response

def transform_data(rData:list) -> list:
	dataApps = []
	for item in rData:
		dataApp_instance = dataApp(
			_id=str(item["_id"]),
			url=item["url"],
			name=item["name"],
			description=item["description"],
		)
		dataApps.append(dataApp_instance)
	return dataApps