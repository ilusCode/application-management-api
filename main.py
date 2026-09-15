from fastapi import FastAPI, APIRouter
from services.crudDbService import getAppList, getAppDetailsById, deleteAppById, newApplication
from model.appList import appList
from model.appDetails import appDetails
from model.UpdateRequest import updateRequest
from model.appDetailsRequest import appDetailsRequest

app = FastAPI()
prefix_router = APIRouter(prefix="/api/v1")

@prefix_router.get("/apps")
async def get_apps(status: str = None) -> appList:
    return await getAppList(status=status)

@prefix_router.get("/apps/{app_id}/details")
async def read_app_details(app_id: str) -> appDetails:
    return await getAppDetailsById(app_id)

@prefix_router.delete("/apps/{app_id}")
async def delete_app(app_id: str) -> dict:
    return await deleteAppById(app_id)

# @prefix_router.put("/apps/{app_id}")
# async def update_app(app_id: str, payload: updateRequest) -> dict:
#     return await updateAppById(app_id, payload)

@prefix_router.post("/apps/{app_id}/new")
async def new_application(payload: appDetailsRequest) -> dict:
    return await newApplication(payload)

app.include_router(prefix_router)