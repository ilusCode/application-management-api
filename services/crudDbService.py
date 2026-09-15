import os
from datetime import datetime
from functools import lru_cache

from pymongo import MongoClient
from dotenv import load_dotenv
from model.appList import appList
from model.appDetails import appDetails
from transform.transformModel import transform_data, transform_data_details
from bson.objectid import ObjectId
from bson.errors import InvalidId
from exception.IcException import IcException
from utils.Constants import ERR_01, ERR_02
from model.UpdateRequest import updateRequest
from model.changeType import changeType
from model.appDetailsRequest import appDetailsRequest

load_dotenv()

@lru_cache(maxsize=1)
def connect_to_mongodb():
	uri = f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.8.0"
	database_name = os.getenv("MONGODB_DATABASE")
	client = MongoClient(uri)
	return client[database_name]

async def getAppList(status: str = None) -> appList:
	db = connect_to_mongodb()
	collection = db[os.getenv("MONGODB_COLLECTION")]
	if status == "inactive":
		query = {"active": False}
	else:
		query = {"active": True}
	
	result = list(collection.find(query))
	data = transform_data(result)
	return appList(data)

async def getAppDetailsById(app_id: str) -> appDetails:
	try:
		object_id = ObjectId(app_id)
	except (InvalidId, TypeError):
		raise IcException(statusCode=400, messageDetail=ERR_01)

	db = connect_to_mongodb()
	collection = db[os.getenv("MONGODB_COLLECTION")]
	collectionImages = db[os.getenv("MONGODB_COLLECTION_IMAGES")]
	collectionChanges = db[os.getenv("MONGODB_COLLECTION_CHANGES")]
	rData = collection.find_one({"_id": object_id})

	print(f"Retrieved application data: {rData}")

	if rData is None:
		raise IcException(statusCode=202, messageDetail=ERR_02)
	
	rImages = list(collectionImages.find({"applicationId": str(object_id)}))
	rChanges = list(collectionChanges.find({"applicationId": str(object_id)}))

	print(f"Retrieved application images: {rImages}")
	print(f"Retrieved application changes: {rChanges}")

	data = transform_data_details(rData, rImages, rChanges)
	return appDetails(data)

async def deleteAppById(app_id: str) -> dict:
	if not app_id:
		raise IcException(statusCode=400, messageDetail=ERR_01)

	try:
		object_id = ObjectId(app_id)
	except (InvalidId, TypeError):
		raise IcException(statusCode=400, messageDetail=ERR_01)

	db = connect_to_mongodb()
	collection = db[os.getenv("MONGODB_COLLECTION")]
	collectionChanges = db[os.getenv("MONGODB_COLLECTION_CHANGES")]

	print(f"Deleting application with ID: {app_id}")

	query = {"active": True, "_id": object_id}

	result = list(collection.find(query))
	print(f"Number of active applications before deletion: {len(result)}")

	if len(result) != 0:
		result = collection.update_one({"_id": object_id}, {"$set": {"active": False}})
		rChange = collectionChanges.insert_one({"applicationId": str(object_id), "changeType": "delete", "datetime": datetime.utcnow(), "description": "delete App"})
		collection.update_one({"_id": object_id}, {"$push": {"changes": str(rChange.inserted_id)}})
		print(f"Number of documents modified: {result.modified_count}")
		return {"app_id": app_id, "message": "App deleted successfully."}
	else:
		raise IcException(statusCode=202, messageDetail=ERR_02)

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

async def newApplication(payload: appDetailsRequest) -> dict:
	print("Creating new application: name=%s, url=%s", payload.data.name, payload.data.url)
	db = connect_to_mongodb()
	collection = db[os.getenv("MONGODB_COLLECTION")]
	collectionImages = db[os.getenv("MONGODB_COLLECTION_IMAGES")]
	collectionChanges = db[os.getenv("MONGODB_COLLECTION_CHANGES")]
	result = collection.insert_one({"url": payload.data.url, "name": payload.data.name, "description": payload.data.description, "active":True, "images": [], "changes": []})
	print("Application created successfully: application_id=%s", result.inserted_id)

	for image in payload.data.images:
		rImage = collectionImages.insert_one({"applicationId": str(result.inserted_id), "url": image.url, "type":image.type, "datetime": datetime.utcnow()})
		rChange = collectionChanges.insert_one({"applicationId": str(result.inserted_id), "changeType": "new", "datetime": datetime.utcnow(), "description": "add new App "+ payload.data.name})

		collection.update_one({"_id": result.inserted_id}, {"$push": {"images": str(rImage.inserted_id)}})
		collection.update_one({"_id": result.inserted_id}, {"$push": {"changes": str(rChange.inserted_id)}})
		return { "statusCode": "000" }