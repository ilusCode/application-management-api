from dataclasses import dataclass
from model.newChange import newChange
from pydantic import BaseModel

@dataclass
class updateRequest(BaseModel):
    changes : list[newChange]