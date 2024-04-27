from pydantic import BaseModel


class ExceptionMessage(BaseModel):
    status_code: int
    error_details: str
    error_code: int
