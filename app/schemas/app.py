from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AppStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Schema(BaseModel):
    """Atributos en snake_case en Python y camelCase en el JSON."""

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)


class Document(Schema):
    id: str = Field(alias="_id")


# Respuestas


class AppSummary(Document):
    url: str
    name: str
    description: str


class Image(Document):
    application_id: str
    url: str
    type: str


class Change(Document):
    application_id: str
    change_type: str
    datetime: str
    description: str


class AppDetail(AppSummary):
    images: List[Image]
    active: bool
    changes: List[Change]


class AppListResponse(Schema):
    data: List[AppSummary]


class AppDetailResponse(Schema):
    data: AppDetail


class AppCreatedResponse(Schema):
    status_code: str = "Ok"
    id: str = Field(alias="_id")


class AppDeactivatedResponse(Schema):
    app_id: str = Field(alias="app_id")
    message: str = "App deleted successfully."


# Peticiones


class NewImage(Schema):
    url: str
    type: str


class AppCreate(Schema):
    url: str
    name: str
    description: str
    images: List[NewImage]


class AppCreateRequest(Schema):
    data: AppCreate
