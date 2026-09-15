from dataclasses import dataclass
from model.changeType import changeType

@dataclass
class newChange:
    type: changeType
    value: str