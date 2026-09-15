from dataclasses import dataclass
from typing import List
from model.change import change
from model.imageDetails import imageDetails

@dataclass
class dataAppDetails:
	_id: str
	url: str
	name: str
	description: str
	images: List[imageDetails]
	active: bool
	changes: List[change]
