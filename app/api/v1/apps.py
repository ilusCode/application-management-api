from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.mongodb import Collections, get_collections
from app.schemas.app import (
    AppCreatedResponse,
    AppCreateRequest,
    AppDeactivatedResponse,
    AppDetailResponse,
    AppListResponse,
    AppStatus,
)
from app.services import app_service

router = APIRouter(tags=["Apps"])

CollectionsDep = Annotated[Collections, Depends(get_collections)]


@router.get("/apps")
def list_apps(collections: CollectionsDep, status: AppStatus = AppStatus.ACTIVE) -> AppListResponse:
    return app_service.list_applications(collections, status)


@router.get("/apps/{app_id}/details")
def get_app_details(app_id: str, collections: CollectionsDep) -> AppDetailResponse:
    return app_service.get_application(collections, app_id)


@router.put("/apps/{app_id}")
def deactivate_app(app_id: str, collections: CollectionsDep) -> AppDeactivatedResponse:
    return app_service.deactivate_application(collections, app_id)


@router.post("/app/new")
def create_app(payload: AppCreateRequest, collections: CollectionsDep) -> AppCreatedResponse:
    return app_service.create_application(collections, payload.data)
