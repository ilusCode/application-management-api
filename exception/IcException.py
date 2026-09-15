from fastapi import HTTPException

class IcException(HTTPException):
	def __init__(self, statusCode: int = 400, messageDetail: str = "Error unknown"):
		super().__init__(status_code=statusCode, detail=messageDetail)
