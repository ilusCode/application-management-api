import os
from functools import lru_cache

from pymongo import MongoClient
from dotenv import load_dotenv
from model.appList import appList
from model.appDetails import appDetails
from transform.transformModel import transform_data, transform_data_details
from bson.objectid import ObjectId
from bson.errors import InvalidId
from exception.IcException import IcException

load_dotenv()

@lru_cache(maxsize=1)
def connect_to_mongodb():
	uri = f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.8.0"
	database_name = os.getenv("MONGODB_DATABASE")
	client = MongoClient(uri)
	return client[database_name]

def getAppList() -> appList:
	db = connect_to_mongodb()
	collection = db[os.getenv("MONGODB_COLLECTION")]
	result = list(collection.find())
	if result is None:
		raise IcException("Application not found")
	data = transform_data(result)
	return appList(data)

def getAppDetailsById(app_id: str) -> appDetails:
	if not app_id:
		raise IcException("Invalid ID format")

	try:
		object_id = ObjectId(app_id)
	except (InvalidId, TypeError):
		raise IcException("Invalid ID format")

	db = connect_to_mongodb()
	collection = db[os.getenv("MONGODB_COLLECTION")]
	result = collection.find_one({"_id": object_id})

	if result is None:
		raise IcException("Application not found")

	data = transform_data_details(result)
	return appDetails(data)
	