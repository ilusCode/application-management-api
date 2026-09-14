from fastapi import FastAPI, APIRouter
from services.crudDbService import getAppList, getAppDetailsById
from model.appList import appList
from model.appDetails import appDetails

app = FastAPI()
prefix_router = APIRouter(prefix="/api/v1")

@prefix_router.get("/apps")
def get_apps() -> appList:
    return getAppList()

@prefix_router.get("/apps/{app_id}/details")
def read_app_details(app_id: str) -> appDetails:
    return getAppDetailsById(app_id)

@prefix_router.delete("/apps/{app_id}")
def delete_app(app_id: str) -> dict:
    return {"app_id": app_id, "message": "App deleted successfully."}

@prefix_router.put("/apps/{app_id}")
def update_app(app_id: str, app_data: dict) -> dict:
    return {"app_id": app_id, "updated_data": app_data, "message": "App updated successfully."}

app.include_router(prefix_router)