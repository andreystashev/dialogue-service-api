from sqlalchemy import Boolean, Column, String
from sqlalchemy.sql.sqltypes import DateTime, Text

from .base import Base
from .mixin import AbstractModel


class User(Base, AbstractModel):
    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    password = Column(Text, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=False, nullable=True)
    deleted_at = Column(DateTime, default=None, nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, created_at={self.created_at})"
