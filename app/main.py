from fastapi import FastAPI, APIRouter, Depends
from app.services.managerService import getAppList, getAppDetailsById, deleteAppById, newApplication
from app.model.appList import appList
from app.model.appDetails import appDetails
from app.model.appDetailsRequest import appDetailsRequest
from app.model.requestStructure import requestStructure
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None)
prefix_router = APIRouter(prefix="/api/v1",tags=["Apps"])
prefix_router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@prefix_router.get("/apps")
async def get_apps(requestStructure: requestStructure = Depends()) -> appList:
    return await getAppList(status=requestStructure.status.name)

@prefix_router.get("/apps/{app_id}/details")
async def read_app_details(app_id: str) -> appDetails:
    return await getAppDetailsById(app_id)

@prefix_router.put("/apps/{app_id}")
async def delete_app(app_id: str) -> dict:
    return await deleteAppById(app_id)

@prefix_router.post("/app/new")
async def new_application(payload: appDetailsRequest) -> dict:
    return await newApplication(payload)

app.include_router(prefix_router)