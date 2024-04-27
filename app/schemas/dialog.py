from pydantic import BaseModel


class GenerationRequest(BaseModel):
    prompt: str


class GenerationResult(BaseModel):
    dialog_id: str
    time: float


class GenerationStatus(BaseModel):
    dialog_id: str
    status: str


class GenerationResultText(BaseModel):
    dialog_id: str
    prompt: str
    result_text: str


class GenerationResultAll(GenerationResultText):
    user_id: int

    class Config:
        orm_mode = True
