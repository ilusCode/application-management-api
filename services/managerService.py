import logging
import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional
from urllib.parse import quote_plus

from bson.errors import InvalidId
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

from exception.IcException import IcException
from model.appDetails import appDetails
from model.appDetailsRequest import appDetailsRequest
from model.appList import appList
from model.serviceStatusEnum import serviceStatus
from transform.transformModel import transform_data, transform_data_details
from utils.Constants import ERR_01, ERR_02


load_dotenv()
logger = logging.getLogger(__name__)


def _get_object_id(app_id: str) -> ObjectId:
    if not app_id:
        raise IcException(statusCode=400, messageDetail=ERR_01)
    try:
        return ObjectId(app_id)
    except (InvalidId, TypeError):
        raise IcException(statusCode=400, messageDetail=ERR_01) from None


def _collection(db, variable_name: str):
    collection_name = os.getenv(variable_name)
    if not collection_name:
        raise RuntimeError(f"Missing required environment variable: {variable_name}")
    return db[collection_name]


@lru_cache(maxsize=1)
def connect_to_mongodb():
    """Crea un único cliente MongoDB reutilizable durante la vida del proceso."""
    username = os.getenv("MONGODB_USERNAME")
    password = os.getenv("MONGODB_PASSWORD")
    host = os.getenv("MONGODB_HOST")
    port = os.getenv("MONGODB_PORT")
    database_name = os.getenv("MONGODB_DATABASE")
    if not all((username, password, host, port, database_name)):
        raise RuntimeError("Missing required MongoDB environment variables")

    uri = (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/"
        "?directConnection=true&serverSelectionTimeoutMS=2000&appName=application-management-api"
    )
    return MongoClient(uri)[database_name]


async def getAppList(status: Optional[serviceStatus] = None) -> appList:
    collection = _collection(connect_to_mongodb(), "MONGODB_COLLECTION")
    active = status != serviceStatus.INACTIVE
    return appList(transform_data(collection.find({"active": active})))


async def getAppDetailsById(app_id: str) -> appDetails:
    object_id = _get_object_id(app_id)
    db = connect_to_mongodb()
    application = _collection(db, "MONGODB_COLLECTION").find_one({"_id": object_id})
    if application is None:
        raise IcException(statusCode=202, messageDetail=ERR_02)

    images = list(_collection(db, "MONGODB_COLLECTION_IMAGES").find({"applicationId": str(object_id)}))
    changes = list(_collection(db, "MONGODB_COLLECTION_CHANGES").find({"applicationId": str(object_id)}))
    return appDetails(transform_data_details(application, images, changes))


async def deleteAppById(app_id: str) -> dict:
    object_id = _get_object_id(app_id)
    db = connect_to_mongodb()
    applications = _collection(db, "MONGODB_COLLECTION")
    result = applications.update_one({"_id": object_id, "active": True}, {"$set": {"active": False}})
    if result.modified_count == 0:
        raise IcException(statusCode=202, messageDetail=ERR_02)

    change = _collection(db, "MONGODB_COLLECTION_CHANGES").insert_one(
        {
            "applicationId": str(object_id),
            "changeType": "delete",
            "datetime": datetime.now(timezone.utc),
            "description": "delete App",
        }
    )
    applications.update_one({"_id": object_id}, {"$push": {"changes": str(change.inserted_id)}})
    logger.info("Application deleted: %s", app_id)
    return {"app_id": app_id, "message": "App deleted successfully."}


async def newApplication(payload: appDetailsRequest) -> dict:
    db = connect_to_mongodb()
    applications = _collection(db, "MONGODB_COLLECTION")
    images = _collection(db, "MONGODB_COLLECTION_IMAGES")
    changes = _collection(db, "MONGODB_COLLECTION_CHANGES")
    application_data = payload.data

    result = applications.insert_one(
        {
            "url": application_data.url,
            "name": application_data.name,
            "description": application_data.description,
            "active": True,
            "images": [],
            "changes": [],
        }
    )
    application_id = str(result.inserted_id)
    now = datetime.now(timezone.utc)
    image_documents = [
        {"applicationId": application_id, "url": image.url, "type": image.type, "datetime": now}
        for image in application_data.images
    ]
    image_ids = []
    if image_documents:
        image_ids = [str(item) for item in images.insert_many(image_documents).inserted_ids]

    change = changes.insert_one(
        {
            "applicationId": application_id,
            "changeType": "new",
            "datetime": now,
            "description": f"add new App {application_data.name}",
        }
    )
    applications.update_one(
        {"_id": result.inserted_id},
        {"$push": {"changes": str(change.inserted_id)}, "$addToSet": {"images": {"$each": image_ids}}},
    )
    logger.info("Application created: %s", application_id)
    return {"statusCode": "Ok", "_id": application_id}
