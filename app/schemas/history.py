from pydantic import BaseModel


class HistoryCreate(BaseModel):
    user_id: int
    dialog_id: str
    prompt: str

    class Config:
        orm_mode = True


class HistoryFullCreate(HistoryCreate):
    result_text: str
