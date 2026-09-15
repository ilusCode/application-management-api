from dataclasses import dataclass
from typing import List
from model.change import change
from model.newImage import newImage

@dataclass
class dataAppRequest:
    url: str
    name: str
    description: str
    images: List[newImage]