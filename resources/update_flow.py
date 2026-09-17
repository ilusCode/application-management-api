async def updateAppById(app_id: str, payload: updateRequest) -> dict:
	if not app_id:
		raise IcException(statusCode=400, messageDetail=ERR_01)

	try:
		object_id = ObjectId(app_id)
	except (InvalidId, TypeError):
		raise IcException(statusCode=400, messageDetail=ERR_01)

	db = connect_to_mongodb()
	collection = db[os.getenv("MONGODB_COLLECTION")]
	collectionChanges = db[os.getenv("MONGODB_COLLECTION_CHANGES")]

	print(f"Updating application with ID: {app_id} and data: {payload}")

	query = {"_id": object_id}

	result = list(collection.find(query))
	print(f"Number of applications before update: {len(result)}")

	if len(result) != 0:
		for change in payload.changes:
			print("changeType - "+ change.type.name)
			if change.type.name == "NAME":
				#result = collection.update_one({"_id": object_id}, {"$set": {"name": change.value}})
				print("ok")
			else:
				raise IcException(statusCode=400, messageDetail="Operation not valid")
					
		print(f"Number of documents modified: {result.modified_count}")
		return {"app_id": app_id, "updated_data": changeType, "message": "App updated successfully."}
	else:
		raise IcException(statusCode=202, messageDetail=ERR_02)

else: 
				if change.type == changeType.DESCRIPTION:
					result = collection.update_one({"_id": object_id}, {"$set": {"description": change.value}})
					collectionChanges.insert_one({"applicationId": str(object_id), "changeType": "update", "datetime": datetime.utcnow(),"description":"Change name: "+ change.value})
				else:
					if change.type == changeType.URL:
						result = collection.update_one({"_id": object_id}, {"$set": {"url": change.value}})
						collectionChanges.insert_one({"applicationId": str(object_id), "changeType": "update", "datetime": datetime.utcnow(),"description":"Change url: "+ change.value})
					else:
						if change.type == changeType.AVAILABLE:
							if change.value == "inactive":
								result = collection.update_one({"_id": object_id}, {"$set": {"active": False}})
								collectionChanges.insert_one({"applicationId": str(object_id), "changeType": "update", "datetime": datetime.utcnow(),"description":"Change available: "+ change.value})
							else:
								if change.value == "active":
									result = collection.update_one({"_id": object_id}, {"$set": {"active": True}})
									collectionChanges.insert_one({"applicationId": str(object_id), "changeType": "update", "datetime": datetime.utcnow(),"description":"Change available: "+ change.value})
								else:
									raise IcException(statusCode=400, messageDetail="Operation not valid")		