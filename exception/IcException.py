from fastapi import HTTPException

class IcException(HTTPException):
	def __init__(self, status_code: int = 400, detail: str="Error unknown"):
		super().__init__(status_code=status_code, detail=detail)

	def __init__(self, detail: str="Error unknown"):
		super().__init__(status_code=400, detail=detail)