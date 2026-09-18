from dataclasses import dataclass
from typing import List
from app.model.change import change
from app.model.newImage import newImage

@dataclass
class dataAppRequest:
    url: str
    name: str
    description: str
    images: List[newImage]