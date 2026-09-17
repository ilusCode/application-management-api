from dataclasses import dataclass
from model.serviceStatusEnum import serviceStatus
from pydantic import BaseModel

class requestStructure(BaseModel):
    status: serviceStatus