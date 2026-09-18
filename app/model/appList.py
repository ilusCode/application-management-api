from dataclasses import dataclass
from typing import List
from app.model.dataApp import dataApp

@dataclass
class appList:
	data: List[dataApp]

