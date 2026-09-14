from model.dataApp import dataApp
from model.dataAppDetails import dataAppDetails


def transform_data_details(result: dict) -> dataAppDetails:
    return dataAppDetails(
        _id=str(result.get("_id", "")),
        url=result.get("url", ""),
        name=result.get("name", ""),
        description=result.get("description", ""),
        image=result.get("image", "")
    )

def transform_data(result:list) -> list:
	dataApps = []
	for item in result:
		dataApp_instance = dataApp(
			_id=str(item.get("_id", "")),
			url=item.get("url", ""),
			name=item.get("name", ""),
			description=item.get("description", ""),
		)
		dataApps.append(dataApp_instance)
	return dataApps