from fastapi import FastAPI, APIRouter, Depends
from services.managerService import getAppList, getAppDetailsById, deleteAppById, newApplication
from model.appList import appList
from model.appDetails import appDetails
from model.appDetailsRequest import appDetailsRequest
from model.requestStructure import requestStructure

app = FastAPI(version="1.0.0")
prefix_router = APIRouter(prefix="/api/v1",tags=["Apps"])

@prefix_router.get("/apps")
async def get_apps(requestStructure: requestStructure = Depends()) -> appList:
    return await getAppList(status=requestStructure.status.name)

@prefix_router.get("/apps/{app_id}/details")
async def read_app_details(app_id: str) -> appDetails:
    return await getAppDetailsById(app_id)

@prefix_router.delete("/apps/{app_id}")
async def delete_app(app_id: str) -> dict:
    return await deleteAppById(app_id)

@prefix_router.post("/apps/{app_id}/new")
async def new_application(payload: appDetailsRequest) -> dict:
    return await newApplication(payload)

app.include_router(prefix_router)