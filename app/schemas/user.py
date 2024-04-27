from datetime import datetime

import pydantic


class User(pydantic.BaseModel):
    id: int = None
    created_at: datetime = None
    email: str = None
    password: str = None
    is_admin: bool = None
    is_active: bool = None
    deleted_at: datetime | None

    class Config:
        orm_mode = True


class UserLogin(pydantic.BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class UserCreateWeb(pydantic.BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class UserCreate(pydantic.BaseModel):
    email: str | None
    password: str | None
    is_admin: bool = False
    is_active: bool = True

    class Config:
        orm_mode = True


class UserResponse(pydantic.BaseModel):
    id: int
    created_at: datetime
    email: str | None = None
    is_active: bool

    class Config:
        orm_mode = True


class UserListResponse(pydantic.BaseModel):
    users: list[UserResponse]

    class Config:
        orm_mode = True
