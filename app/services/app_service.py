import logging
from datetime import datetime, timezone
from typing import Optional

from bson.errors import InvalidId
from bson.objectid import ObjectId

from app.core.exceptions import AppAlreadyInactiveError, AppNotFoundError, InvalidIdError
from app.db.mongodb import Collections
from app.schemas.app import (
    AppCreate,
    AppCreatedResponse,
    AppDeactivatedResponse,
    AppDetailResponse,
    AppListResponse,
    AppStatus,
)
from app.services.mappers import to_app_detail, to_app_summaries

logger = logging.getLogger(__name__)


def to_object_id(app_id: str) -> ObjectId:
    # ObjectId(None) generaría un id nuevo, por eso se rechaza explícitamente.
    if not app_id:
        raise InvalidIdError()
    try:
        return ObjectId(app_id)
    except (InvalidId, TypeError):
        raise InvalidIdError() from None


def list_applications(collections: Collections, status: Optional[AppStatus] = None) -> AppListResponse:
    active = status != AppStatus.INACTIVE
    return AppListResponse(data=to_app_summaries(collections.apps.find({"active": active})))


def get_application(collections: Collections, app_id: str) -> AppDetailResponse:
    object_id = to_object_id(app_id)
    application = collections.apps.find_one({"_id": object_id})
    if application is None:
        raise AppNotFoundError()

    images = collections.images.find({"applicationId": str(object_id)})
    changes = collections.changes.find({"applicationId": str(object_id)})
    return AppDetailResponse(data=to_app_detail(application, images, changes))


def deactivate_application(collections: Collections, app_id: str) -> AppDeactivatedResponse:
    object_id = to_object_id(app_id)
    result = collections.apps.update_one({"_id": object_id, "active": True}, {"$set": {"active": False}})
    if result.matched_count == 0:
        if collections.apps.count_documents({"_id": object_id}, limit=1) == 0:
            raise AppNotFoundError()
        raise AppAlreadyInactiveError()

    change = collections.changes.insert_one(
        {
            "applicationId": str(object_id),
            "changeType": "delete",
            "datetime": datetime.now(timezone.utc),
            "description": "delete App",
        }
    )
    collections.apps.update_one({"_id": object_id}, {"$push": {"changes": str(change.inserted_id)}})
    logger.info("Application deleted: %s", app_id)
    return AppDeactivatedResponse(app_id=app_id)


def create_application(collections: Collections, application: AppCreate) -> AppCreatedResponse:
    result = collections.apps.insert_one(
        {
            "url": application.url,
            "name": application.name,
            "description": application.description,
            "active": True,
            "images": [],
            "changes": [],
        }
    )
    application_id = str(result.inserted_id)
    now = datetime.now(timezone.utc)
    image_documents = [
        {"applicationId": application_id, "url": image.url, "type": image.type, "datetime": now}
        for image in application.images
    ]
    image_ids = []
    if image_documents:
        image_ids = [str(item) for item in collections.images.insert_many(image_documents).inserted_ids]

    change = collections.changes.insert_one(
        {
            "applicationId": application_id,
            "changeType": "new",
            "datetime": now,
            "description": f"add new App {application.name}",
        }
    )
    collections.apps.update_one(
        {"_id": result.inserted_id},
        {"$push": {"changes": str(change.inserted_id)}, "$addToSet": {"images": {"$each": image_ids}}},
    )
    logger.info("Application created: %s", application_id)
    return AppCreatedResponse(id=application_id)
