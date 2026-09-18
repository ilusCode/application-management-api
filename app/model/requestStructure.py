from dataclasses import dataclass
from app.model.serviceStatusEnum import serviceStatus
from pydantic import BaseModel

class requestStructure(BaseModel):
    status: serviceStatus