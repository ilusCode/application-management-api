"""Conversión de documentos de MongoDB a esquemas de respuesta."""

from typing import Iterable, List

from app.schemas.app import AppDetail, AppSummary, Change, Image


def to_app_summary(document: dict) -> AppSummary:
    return AppSummary(
        id=str(document["_id"]),
        url=document["url"],
        name=document["name"],
        description=document["description"],
    )


def to_app_summaries(documents: Iterable[dict]) -> List[AppSummary]:
    return [to_app_summary(document) for document in documents]


def to_image(document: dict) -> Image:
    return Image(
        id=str(document["_id"]),
        application_id=str(document["applicationId"]),
        url=str(document["url"]),
        type=str(document["type"]),
    )


def to_change(document: dict) -> Change:
    return Change(
        id=str(document["_id"]),
        application_id=str(document["applicationId"]),
        change_type=str(document["changeType"]),
        datetime=str(document["datetime"]),
        description=str(document["description"]),
    )


def to_app_detail(document: dict, images: Iterable[dict], changes: Iterable[dict]) -> AppDetail:
    return AppDetail(
        **to_app_summary(document).model_dump(),
        images=[to_image(image) for image in images],
        active=document["active"],
        changes=[to_change(change) for change in changes],
    )
