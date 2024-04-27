from datetime import datetime

from pydantic import BaseModel


class RefreshToken(BaseModel):
    refresh_token: str


class JWTTokenResponse(BaseModel):
    access_token: str


class JWTTokenDisabledResponse(BaseModel):
    access_token_disabled: str


class JWTTokenCreate(BaseModel):
    user_id: int
    token: str
    expires: datetime
