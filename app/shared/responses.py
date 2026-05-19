from pydantic import BaseModel

class SuccessResponse(BaseModel):
    success: bool = True
    data: dict | None = None