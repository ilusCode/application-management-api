from dataclasses import dataclass

@dataclass
class change:
	_id: str
	applicationId: str
	changeType: str
	datetime: str
	description: str
