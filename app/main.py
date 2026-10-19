from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.exceptions import AppAlreadyInactiveError, AppError, AppNotFoundError, InvalidIdError
from app.db.mongodb import close_client

ERROR_STATUS_CODES = {
    InvalidIdError: 400,
    AppNotFoundError: 404,
    AppAlreadyInactiveError: 202,
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    close_client()


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=ERROR_STATUS_CODES.get(type(exc), 400), content={"detail": str(exc)})


def create_app() -> FastAPI:
    application = FastAPI(
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(AppError, app_error_handler)
    application.include_router(api_router)
    return application


app = create_app()
